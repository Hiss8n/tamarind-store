import os
from dotenv import load_dotenv
import mysql.connector
from mysql.connector import MySQLConnection

load_dotenv()


def get_connection() -> MySQLConnection:
	"""Open a MySQL connection using MYSQL_* environment variables."""
	user = os.getenv("MYSQL_USER")
	database = os.getenv("MYSQL_DATABASE")
	if not user or not database:
		raise ValueError("Set MYSQL_USER and MYSQL_DATABASE before connecting.")

	return mysql.connector.connect(
		host=os.getenv("MYSQL_HOST", "localhost"),
		port=int(os.getenv("MYSQL_PORT", "3306")),
		user=user,
		password=os.getenv("MYSQL_PASSWORD", ""),
		database=database,
		connection_timeout=10,
	)
