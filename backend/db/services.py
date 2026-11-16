from decimal import Decimal
from typing import Any
from db.schemas import CheckoutCreate, CheckoutRead

from .database import get_connection


def add_to_cart(name: str, count: int, price: Decimal) -> dict[str, Any]:
	"""Add a quantity of an item to the shared cart and return its totals."""
	connection = get_connection()
	cursor = None
	try:
		cursor = connection.cursor()
		cursor.execute(
			"""
			INSERT INTO cart_items (item_name, item_count, price)
			VALUES (%s, %s, %s)
			ON CONFLICT (item_name) DO UPDATE SET
				item_count = cart_items.item_count + EXCLUDED.item_count,
				price = EXCLUDED.price
			""",
			(name, count, price),
		)
		connection.commit()
	except Exception:
		connection.rollback()
		raise
	finally:
		if cursor is not None:
			cursor.close()
		connection.close()
	return get_cart()


def get_cart() -> dict[str, Any]:
	"""Return all cart items with line totals and the cart total."""
	connection = get_connection()
	cursor = None
	try:
		cursor = connection.cursor()
		cursor.execute("SELECT item_name, item_count, price FROM cart_items ORDER BY item_name")
		rows = cursor.fetchall()
		items = []
		cart_total = Decimal("0.00")
		for row in rows:
			price = Decimal(row["price"])
			line_total = price * row["item_count"]
			items.append({
				"name": row["item_name"],
				"count": row["item_count"],
				"price": price,
				"total_price": line_total,
			})
			cart_total += line_total
		return {"items": items, "total_price": cart_total}
	finally:
		if cursor is not None:
			cursor.close()
		connection.close()


def remove_from_cart(name: str) -> bool:
	"""Remove an item from the cart; the cart total is recalculated on read."""
	connection = get_connection()
	cursor = None
	try:
		cursor = connection.cursor()
		cursor.execute("DELETE FROM cart_items WHERE item_name = %s", (name,))
		removed = cursor.rowcount > 0
		connection.commit()
		return removed
	except Exception:
		connection.rollback()
		raise
	finally:
		if cursor is not None:
			cursor.close()
		connection.close()


def get_order_by_id(order_id: int) -> dict[str, Any] | None:
	"""Return an order as a dictionary, or None if it does not exist."""
	connection = get_connection()
	cursor = None
	try:
		cursor = connection.cursor()
		cursor.execute("SELECT * FROM orders WHERE order_id = %s", (order_id,))
		return cursor.fetchone()
	finally:
		if cursor is not None:
			cursor.close()
		connection.close()


def remove_order(order_id: int) -> bool:
	"""Delete an order by ID and return whether a row was deleted."""
	connection = get_connection()
	cursor = None
	try:
		cursor = connection.cursor()
		cursor.execute("DELETE FROM orders WHERE order_id = %s", (order_id,))
		deleted = cursor.rowcount > 0
		connection.commit()
		return deleted
	except Exception:
		connection.rollback()
		raise
	finally:
		if cursor is not None:
			cursor.close()
		connection.close()


def create_checkout(checkout: CheckoutCreate) -> CheckoutRead:
	payer_name = checkout.name.strip()
	payer_phone = checkout.phone.strip()
	connection = get_connection()
	cursor = None
	order_ids = []
	try:
		cursor = connection.cursor()
		for item in checkout.items:
			line_total = item.price * item.quantity
			cursor.execute(
				"""
				INSERT INTO orders
					(product_id, unit, total_price, status, payer_name, payer_phone)
				VALUES (%s, %s, %s, %s, %s, %s)
				RETURNING order_id
				""",
				(
					item.product_id,
					item.quantity,
					line_total,
					checkout.status,
					payer_name,
					payer_phone,
				),
			)
			order_ids.append(int(cursor.fetchone()["order_id"]))
		connection.commit()
		return CheckoutRead(
			order_ids=order_ids,
			total_price=sum(item.price * item.quantity for item in checkout.items),
			status=checkout.status,
			payer_name=payer_name,
			payer_phone=payer_phone,
		)
	except Exception:
		connection.rollback()
		raise
	finally:
		if cursor is not None:
			cursor.close()
		connection.close()
