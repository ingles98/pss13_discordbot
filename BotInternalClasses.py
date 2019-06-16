import sqlite3
from sqlite3 import Error

class DatabaseDAO:
	db_path = None
	db_connection = None
	usersTable = None
	queueTable = None

	def __init__(self, db_path, usersTable, queueTable):
		self.db_path = db_path
		self.usersTable = usersTable
		self.queueTable = queueTable
		self.__setup_connection()
		self.__setup_tables()

	def __setup_connection(self):
		conn = None
		try:
			conn = sqlite3.connect(self.db_path, 5)
		except Error as e:
			print(e)
		conn.row_factory = sqlite3.Row
		self.db_connection = conn

	def __setup_tables(self):
		# Users table SQL
		users_tbl_sql = """
			CREATE TABLE IF NOT EXISTS {} (
				userID STRING  PRIMARY KEY ON CONFLICT ROLLBACK
							UNIQUE ON CONFLICT ROLLBACK
							NOT NULL ON CONFLICT ROLLBACK,
				ckey   STRING  UNIQUE ON CONFLICT ROLLBACK
							NOT NULL ON CONFLICT ROLLBACK,
				valid  BOOLEAN DEFAULT (0) 
			);
		""".format(self.usersTable)

		# Queue table SQL
		queue_tbl_sql = """
			CREATE TABLE IF NOT EXISTS {} (
				command           STRING,
				command_arguments STRING,
				msg               TEXT
			);
		""".format(self.queueTable)

		# Execute
		self.__create_table(users_tbl_sql)
		self.__create_table(queue_tbl_sql)

	def __create_table(self, tbl_sql):
		if not self.db_connection:
			raise("No connection to database found!")
		try:
			c = self.db_connection.cursor()
			c.execute(tbl_sql)
		except Error as e:
			print("Error creating database table %s - %s"% (tbl_sql, e))

	def get_messages(self):
		sql = "SELECT * FROM {};".format(self.queueTable)
		cur = self.db_connection.cursor()
		result = None
		# Run the SQL code
		try:
			cur.execute(sql)
			result = cur.fetchall()
		except Error as e:
			print("Error fetching data from queue tbl %s - %s"% (sql, e))
			return False
		# Process the queue
		for row in result:
			self.__process_message(row)
		# Delete the queue
		sql = "DELETE FROM {};".format(self.queueTable)
		cur = self.db_connection.cursor()
		try:
			cur.execute(sql)
			self.db_connection.commit()
		except Error as e:
			print("Error deleting data from queue tbl %s - %s"% (sql, e))
			return False

	def __process_message(self, data):
		print(data["msg"])