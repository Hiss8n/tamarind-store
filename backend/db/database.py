import os
from dotenv import load_dotenv
import psycopg
from psycopg.rows import dict_row


load_dotenv()


def get_connection():
	"""Open a PostgreSQL connection using DATABASE_URL."""
	database_url = os.getenv("DATABASE_URL_POOLED") or os.getenv("DATABASE_URL")
	if not database_url:
		raise ValueError("Set DATABASE_URL or DATABASE_URL_POOLED before connecting.")

	return psycopg.connect(
		database_url,
		connect_timeout=10,
		row_factory=dict_row,
	)
