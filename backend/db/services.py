from typing import Any
from db.schemas import CheckoutCreate, CheckoutRead

from .database import get_connection

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


def update_order_status(order_ids: list[int], status: str) -> int:
	if not order_ids:
		return 0

	connection = get_connection()
	cursor = None
	try:
		cursor = connection.cursor()
		cursor.execute(
			"UPDATE orders SET status = %s WHERE order_id = ANY(%s)",
			(status, order_ids),
		)
		updated = cursor.rowcount
		connection.commit()
		return updated
	except Exception:
		connection.rollback()
		raise
	finally:
		if cursor is not None:
			cursor.close()
		connection.close()
