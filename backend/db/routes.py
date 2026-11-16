import logging

from fastapi import APIRouter, HTTPException, status
from .schemas import CheckoutCreate, CheckoutRead, OrderRead
from .services import (
	create_checkout,
	get_order_by_id,
	remove_order,
)


router = APIRouter(prefix="/orders", tags=["orders"])
logger = logging.getLogger(__name__)

@router.post("/", response_model=CheckoutRead, status_code=status.HTTP_201_CREATED)
def place_order(checkout: CheckoutCreate) -> CheckoutRead:
	try:
		return create_checkout(checkout)
	except Exception as error:
		logger.exception("Failed to place order")
		raise HTTPException(
			status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
			detail="Order could not be saved. Check the backend logs for details.",
		) from error


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




