from fastapi import APIRouter, HTTPException, status

from .schemas import CartItemCreate, CartRead, OrderCreate, OrderRead
from .services import (
	add_order,
	add_to_cart,
	get_cart,
	get_order_by_id,
	remove_from_cart,
	remove_order,
)


router = APIRouter(prefix="/orders", tags=["orders"])
cart_router = APIRouter(prefix="/cart", tags=["cart"])


@cart_router.post("/items", response_model=CartRead)
def add_cart_item(item: CartItemCreate) -> CartRead:
	cart = add_to_cart(item.name, item.count, item.price)
	return CartRead.model_validate(cart)


@cart_router.get("", response_model=CartRead)
def read_cart() -> CartRead:
	return CartRead.model_validate(get_cart())


@cart_router.delete("/items/{name}", response_model=CartRead)
def delete_cart_item(name: str) -> CartRead:
	if not remove_from_cart(name):
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Cart item not found",
		)
	return CartRead.model_validate(get_cart())


@router.post("", response_model=OrderRead, status_code=status.HTTP_201_CREATED)
def create_order(order: OrderCreate) -> OrderRead:
	order_id = add_order(order.total_price, order.status)
	return OrderRead(order_id=order_id, **order.model_dump())


@router.get("/{order_id}", response_model=OrderRead)
def read_order(order_id: int) -> OrderRead:
	order = get_order_by_id(order_id)
	if order is None:
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Order not found",
		)
	return OrderRead.model_validate(order)


@router.delete("/{order_id}")
def delete_order(order_id: int) -> dict[str, str]:
	if not remove_order(order_id):
		raise HTTPException(
			status_code=status.HTTP_404_NOT_FOUND,
			detail="Order not found",
		)
	return {"message": "Order deleted"}
