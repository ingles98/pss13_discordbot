import sqlite3
from sqlite3 import Error
import BotSettings
import os

class DatabaseDAO:
    """
    This class is responsible for parsing data from the database.
    """
    db_path = None
    db_connection = None
    usersTable = None
    queueTable = None

    def __init__(self, db_path, usersTable, queueTable):
        self.db_path = os.path.abspath(db_path)
        if not os.path.exists( os.path.dirname(self.db_path) ):
            os.makedirs(os.path.dirname(self.db_path))
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
                userID TEXT  PRIMARY KEY ON CONFLICT ROLLBACK
                            UNIQUE ON CONFLICT ROLLBACK
                            NOT NULL ON CONFLICT ROLLBACK,
                ckey   TEXT  UNIQUE ON CONFLICT ROLLBACK
                            NOT NULL ON CONFLICT ROLLBACK,
                valid  BOOLEAN DEFAULT (0) 
            );
        """.format(self.usersTable)

        # Queue table SQL
        queue_tbl_sql = """
            CREATE TABLE IF NOT EXISTS {} (
                command           TEXT,
                command_arguments TEXT,
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
            self.db_connection.commit()
        except Error as e:
            print("Error creating database table %s - %s"% (tbl_sql, e))

    def get_messages(self):
        result = self.get_queue()
        if not result:
            return None
        # Delete the queue
        sql = "DELETE FROM {};".format(self.queueTable)
        cur = self.db_connection.cursor()
        try:
            cur.execute(sql)
            self.db_connection.commit()
        except Error as e:
            print("Error deleting data from queue tbl %s - %s"% (sql, e))
            return None
        return result

    def get_user_data(self, userid, ckey=None):
        if ckey:
            sql = """SELECT * FROM {} WHERE userID = ? AND ckey = ? ;"""
        else:
            sql = """SELECT * FROM {} WHERE userID = ? ;"""
        sql = sql.format(self.usersTable)

        cur:sqlite3.Cursor = self.db_connection.cursor()
        result = None
        try:
            if ckey:
                cur.execute(sql, ( str(userid), ckey, ) )
            else:
                cur.execute(sql, ( str(userid), ) )
            result = cur.fetchone()
        except Error as e:
            print("Error fetching user data from users tbl %s - %s"% (sql, e))
            return None
        return result

    def get_all_users(self):
        sql = """SELECT * FROM {}""".format(self.usersTable)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        result = None
        try:
            cur.execute(sql)
            result = cur.fetchall()
        except Error as e:
            print("Error get_all_users %s - %s"% (sql, e))
            return None
        return result

    def get_queue(self):
        sql = "SELECT * FROM {};".format(self.queueTable)
        cur = self.db_connection.cursor()
        try:
            cur.execute(sql)
            return cur.fetchall()
        except Error as e:
            print("Error fetching data from queue tbl %s - %s"% (sql, e))
            return False

    def validate_link(self, userid):
        sql = """UPDATE {} SET valid = 1 WHERE userID = ? ;""".format(self.usersTable)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( str(userid), ))
            self.db_connection.commit()
        except Error as e:
            print("Error validating user linkage from users tbl %s - %s"% (sql, e))
            return False
        return True

    def devalidate_link(self, userid):
        sql = """DELETE FROM {} WHERE userID = ? ;""".format(self.usersTable)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( str(userid), ))
            self.db_connection.commit()
        except Error as e:
            print("Error validating user linkage from users tbl %s - %s"% (sql, e))
            return False
        return True