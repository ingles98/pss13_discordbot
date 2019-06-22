import sqlite3
from sqlite3 import Error
import os

class DatabaseDAO:
    """
    This class is responsible for parsing data from the database.
    """
    db_path = None
    db_connection = None
    users_table = None
    queue_table = None

    def __init__(self, db_path, users_table, queue_table):
        self.db_path = os.path.abspath(db_path)
        if not os.path.exists( os.path.dirname(self.db_path) ):
            os.makedirs(os.path.dirname(self.db_path))
        self.users_table = users_table
        self.queue_table = queue_table
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
        """.format(self.users_table)

        # Queue table SQL
        queue_tbl_sql = """
            CREATE TABLE IF NOT EXISTS {} (
                command           TEXT,
                command_arguments TEXT,
                msg               TEXT
            );
        """.format(self.queue_table)

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
        sql = "DELETE FROM {};".format(self.queue_table)
        cur = self.db_connection.cursor()
        try:
            cur.execute(sql)
            self.db_connection.commit()
        except Error as e:
            print("Error deleting data from queue tbl %s - %s"% (sql, e))
            return None
        return result

    def get_user_data(self, userid=None, ckey=None):
        if not userid and not ckey:
            return None
        params = tuple()
        if userid and ckey:
            sql = """SELECT * FROM {} WHERE userID = ? AND ckey = ? ;"""
            params = ( str(userid), ckey, )
        elif userid:
            sql = """SELECT * FROM {} WHERE userID = ? ;"""
            params = ( str(userid), )
        elif ckey:
            sql = """SELECT * FROM {} WHERE ckey = ? ;"""
            params = ( str(ckey), )
        sql = sql.format(self.users_table)

        cur:sqlite3.Cursor = self.db_connection.cursor()
        result = None
        try:
            cur.execute(sql, params )
            result = cur.fetchone()
        except Error as e:
            print("Error fetching user data from users tbl %s - %s"% (sql, e))
            return None
        return result

    def get_all_users(self):
        sql = """SELECT * FROM {}""".format(self.users_table)
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
        sql = "SELECT * FROM {};".format(self.queue_table)
        cur = self.db_connection.cursor()
        try:
            cur.execute(sql)
            return cur.fetchall()
        except Error as e:
            print("Error fetching data from queue tbl %s - %s"% (sql, e))
            return False

    def validate_link(self, userid):
        sql = """UPDATE {} SET valid = 1 WHERE userID = ? ;""".format(self.users_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( str(userid), ))
            self.db_connection.commit()
        except Error as e:
            print("Error validating user linkage from users tbl %s - %s"% (sql, e))
            return False
        return True

    def devalidate_link(self, userid):
        sql = """DELETE FROM {} WHERE userID = ? ;""".format(self.users_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( str(userid), ))
            self.db_connection.commit()
        except Error as e:
            print("Error validating user linkage from users tbl %s - %s"% (sql, e))
            return False
        return True

    def create_link(self, userid, ckey, valid=0):
        """
        Debug purposes only. Links should be created ingame.
        """
        # Check if the userid or ckey are already linked somewhere
        #### Discord user ID
        userid_result = self.get_user_data(userid)
        if userid_result and len( list( userid_result ) ):
            print("Warning - create_link command - User ID '{}' already exists in the database.".format(userid))
            return False
        #### CKEY
        ckey_result = self.get_user_data(None, ckey)
        if ckey_result and len( list( ckey_result ) ):
            print("Warning - create_link command - User CKEY '{}' already exists in the database.".format(ckey))
            return False
        # Create the link
        sql = """INSERT INTO {} VALUES(?,?,?) """.format(self.users_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( str(userid), ckey, valid, ))
            self.db_connection.commit()
        except Error as e:
            print("Error creating user linkage on users tbl %s - %s"% (sql, e))
            return False
        return True

    def create_message(self, cmd, arguments, message_content):
        """
        Debug purposes only. Misuse may lead to disaster.
        """
        sql = """INSERT INTO {} VALUES(?, ?, ?) """.format(self.queue_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( cmd, arguments, message_content ))
            self.db_connection.commit()
        except Error as e:
            print("Error creating message to queue tbl %s - %s"% (sql, e))
            return False
        return True