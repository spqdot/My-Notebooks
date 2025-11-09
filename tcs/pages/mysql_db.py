import streamlit as st
import pandas as pd
import mysql.connector
from mysql.connector import errorcode
from typing import Optional


DEFAULT_DB = "testdb"


def get_connection(host: str, port: int, user: str, password: str, database: Optional[str] = None):
	"""Return a mysql.connector connection. If database is None, connect without selecting a database."""
	conn_args = dict(host=host, port=port, user=user, password=password)
	if database:
		conn_args["database"] = database
	return mysql.connector.connect(**conn_args)


def ensure_database_and_table(conn, database: str):
	"""Create database (if missing) and ensure a simple `items` table exists."""
	cursor = conn.cursor()
	try:
		cursor.execute(f"CREATE DATABASE IF NOT EXISTS `{database}`")
		conn.database = database
	finally:
		cursor.close()

	cursor = conn.cursor()
	try:
		cursor.execute(
			"""
			CREATE TABLE IF NOT EXISTS items (
				id INT AUTO_INCREMENT PRIMARY KEY,
				name VARCHAR(255) NOT NULL,
				value DOUBLE,
				created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
			) ENGINE=InnoDB
			"""
		)
		conn.commit()
	finally:
		cursor.close()


def fetch_items(conn) -> pd.DataFrame:
	cursor = conn.cursor(dictionary=True)
	try:
		cursor.execute("SELECT id, name, value, created_at FROM items ORDER BY id DESC")
		rows = cursor.fetchall()
		return pd.DataFrame(rows)
	finally:
		cursor.close()


def insert_item(conn, name: str, value: float):
	cursor = conn.cursor()
	try:
		cursor.execute("INSERT INTO items (name, value) VALUES (%s, %s)", (name, value))
		conn.commit()
	finally:
		cursor.close()


def update_item(conn, item_id: int, name: str, value: float):
	cursor = conn.cursor()
	try:
		cursor.execute("UPDATE items SET name=%s, value=%s WHERE id=%s", (name, value, item_id))
		conn.commit()
	finally:
		cursor.close()


def delete_item(conn, item_id: int):
	cursor = conn.cursor()
	try:
		cursor.execute("DELETE FROM items WHERE id=%s", (item_id,))
		conn.commit()
	finally:
		cursor.close()


def main():
	st.set_page_config(page_title="MySQL CRUD", page_icon="🗄️")
	st.title("MySQL CRUD (localhost:3306)")

	st.sidebar.header("Connection")
	# host = st.sidebar.text_input("Host", value="localhost")
	# port = st.sidebar.number_input("Port", value=3306, step=1)
	# user = st.sidebar.text_input("User", value="root")
	# password = st.sidebar.text_input("Password", type="password")
	# database = st.sidebar.text_input("Database", value=DEFAULT_DB)
	host = "localhost"
	port = 3306
	user = "root"
	password = ""
	database = "data"

	conn = None
	connect_error = None
	try:
        # Connect without database first to create it if needed
		conn = get_connection(host, port, user, password)
		ensure_database_and_table(conn, database)
		st.sidebar.success(f"Connected and ensured DB `{database}` and table `items`.")
	except mysql.connector.Error as exc:
		connect_error = exc
		st.sidebar.error(f"Connection error: {exc}")

	if connect_error:
		st.error(f"Could not connect: {connect_error}")
		return

	if conn is None:
		st.info("Click Connect in the sidebar to open a connection to the database.")
		return

	# Main CRUD UI
	fetch_items(conn)
	st.header("Add new item")
	with st.form("add_form"):
		name = st.text_input("Name")
		value = st.number_input("Value", value=0.0, format="%.6f")
		submitted = st.form_submit_button("Insert")
		if submitted:
			try:
				insert_item(conn, name, float(value))
				st.success("Inserted item")
			except Exception as e:
				st.error(f"Insert failed: {e}")

	st.header("Items")
	try:
		df = fetch_items(conn)
		if df.empty:
			st.info("No items found")
		else:
			st.dataframe(df)

			cols = df.columns.tolist()
			# Allow user to choose an ID to edit or delete
			selected = st.selectbox("Select item id to edit/delete", options=df["id"].tolist())

			if selected:
				row = df[df["id"] == selected].iloc[0]
				st.subheader("Edit selected item")
				edit_name = st.text_input("Name (edit)", value=row["name"])
				edit_value = st.number_input("Value (edit)", value=float(row["value"]))
				if st.button("Update"):
					try:
						update_item(conn, int(selected), edit_name, float(edit_value))
						st.success("Updated item")
					except Exception as e:
						st.error(f"Update failed: {e}")

				if st.button("Delete"):
					try:
						delete_item(conn, int(selected))
						st.success("Deleted item")
					except Exception as e:
						st.error(f"Delete failed: {e}")
	except Exception as e:
		st.error(f"Error fetching items: {e}")


if __name__ == "__main__":
	main()

