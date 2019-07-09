import sqlite3
from sqlite3 import Error
import os
import datetime
import random

class DatabaseDAO:
    """
    This class is responsible for parsing data from the database.
    """
    db_path = None
    db_connection = None
    users_table = None
    queue_table = None
    dyk_table = None
    settings = None

    def __init__(self, settings):
        self.db_path = os.path.abspath(settings.db_path)
        if not os.path.exists( os.path.dirname(self.db_path) ):
            os.makedirs(os.path.dirname(self.db_path))
        self.users_table = settings.users_table
        self.queue_table = settings.queue_table
        self.dyk_table = settings.dyk_table
        self.settings = settings
        self.__setup_connection()
        self.__setup_tables()

    def __setup_connection(self):
        conn = None
        try:
            conn = sqlite3.connect(self.db_path, 10, isolation_level=None, detect_types=sqlite3.PARSE_DECLTYPES|sqlite3.PARSE_COLNAMES)
        except Error as e:
            print(e)
        conn.row_factory = sqlite3.Row
        self.db_connection = conn

    def __disconnect(self):
        if self.db_connection:
            self.db_connection.commit()
            self.db_connection.close()
            self.db_connection = None

    def __reconnect(self):
        if not self.db_connection:
            self.__setup_connection()

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

        dyk_tbl_sql = """
            CREATE TABLE IF NOT EXISTS {} (
                id INTEGER PRIMARY KEY,
                text TEXT,
                last_announced timestamp
            );
        """.format(self.dyk_table)

        # Execute
        self.__create_table(users_tbl_sql)
        self.__create_table(queue_tbl_sql)
        self.__create_table(dyk_tbl_sql)

    def __create_table(self, tbl_sql):
        self.__reconnect()
        if not self.db_connection:
            raise("No connection to database found!")
        try:
            c = self.db_connection.cursor()
            c.execute(tbl_sql)
        except Error as e:
            print("Error creating database table %s - %s"% (tbl_sql, e))
        finally:
            self.__disconnect()

    def get_messages(self):
        result = self.get_queue()
        self.__reconnect()
        if not result:
            return None
        # Delete the queue
        sql = "DELETE FROM {};".format(self.queue_table)
        cur = self.db_connection.cursor()
        try:
            cur.execute(sql)
        except Error as e:
            print("Error deleting data from queue tbl %s - %s"% (sql, e))
            return None
        finally:
            self.__disconnect()
        return result

    def get_user_data(self, userid=None, ckey=None):
        self.__reconnect()
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
        finally:
            self.__disconnect()
        return result

    def get_all_users(self):
        self.__reconnect()
        sql = """SELECT * FROM {}""".format(self.users_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        result = None
        try:
            cur.execute(sql)
            result = cur.fetchall()
        except Error as e:
            print("Error get_all_users %s - %s"% (sql, e))
            return None
        finally:
            self.__disconnect()
        return result

    def get_queue(self):
        self.__reconnect()
        sql = "SELECT * FROM {};".format(self.queue_table)
        cur = self.db_connection.cursor()
        try:
            cur.execute(sql)
            return cur.fetchall()
        except Error as e:
            print("Error fetching data from queue tbl %s - %s"% (sql, e))
            return False
        finally:
            self.__disconnect()

    def validate_link(self, userid):
        self.__reconnect()
        sql = """UPDATE {} SET valid = 1 WHERE userID = ? ;""".format(self.users_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( str(userid), ))
        except Error as e:
            print("Error validating user linkage from users tbl %s - %s"% (sql, e))
            return False
        finally:
            self.__disconnect()
        return True

    def devalidate_link(self, userid):
        self.__reconnect()
        sql = """DELETE FROM {} WHERE userID = ? ;""".format(self.users_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( str(userid), ))
        except Error as e:
            print("Error validating user linkage from users tbl %s - %s"% (sql, e))
            return False
        finally:
            self.__disconnect()
        return True

    def create_link(self, userid, ckey, valid=0):
        """
        Debug purposes only. Links should be created ingame.
        """
        self.__reconnect()
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
        except Error as e:
            print("Error creating user linkage on users tbl %s - %s"% (sql, e))
            return False
        finally:
            self.__disconnect()
        return True

    def create_message(self, cmd, arguments, message_content):
        """
        Debug purposes only. Misuse may lead to disaster.
        """
        self.__reconnect()
        sql = """INSERT INTO {} VALUES(?, ?, ?) """.format(self.queue_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( cmd, arguments, message_content ))
        except Error as e:
            print("Error creating message to queue tbl %s - %s"% (sql, e))
            return False
        finally:
            self.__disconnect()
        return True

    # Did You Know Stuff

    def create_dyk(self, text):
        self.__reconnect()
        sql = """INSERT INTO {} (text, last_announced) VALUES(?, ?) """.format(self.dyk_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( text, datetime.datetime.min ))
        except Error as e:
            print("Error creating dyk to dyk tbl %s - %s"% (sql, e))
            return False
        finally:
            self.__disconnect()
        return True

    def delete_dyk(self, dyk_id):
        self.__reconnect()
        sql = """DELETE FROM {} WHERE id = ? ;""".format(self.dyk_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( dyk_id, ))
        except Error as e:
            print("Error error deleting DYK %s - %s"% (sql, e))
            return False
        finally:
            self.__disconnect()
        return True

    def update_dyk_date(self, dyk_id, date:datetime.datetime):
        self.__reconnect()
        sql = """UPDATE {} SET last_announced = ? WHERE id = ? ;""".format(self.dyk_table)
        cur:sqlite3.Cursor = self.db_connection.cursor()
        try:
            cur.execute(sql, ( date, dyk_id ))
        except Error as e:
            print("Error updating dyk date. id:%s date:%s sql:%s - %s"% (dyk_id, date, sql, e))
            return False
        finally:
            self.__disconnect()
        return True

    def get_all_dyks(self):
        self.__reconnect()
        sql = "SELECT * FROM {};".format(self.dyk_table)
        cur = self.db_connection.cursor()
        try:
            cur.execute(sql)
            return cur.fetchall()
        except Error as e:
            print("Error fetching data from queue tbl %s - %s"% (sql, e))
            return False
        finally:
            self.__disconnect()

    def get_random_dyk(self, now):
        dyk_query_result = self.get_all_dyks()
        possible_dyks = list()

        for dyk in dyk_query_result:
            last_announced = dyk["last_announced"] if dyk["last_announced"] else datetime.datetime.min
            if (now - last_announced).total_seconds() < 0:
                continue
            possible_dyks.append(dyk)
        if not possible_dyks or not len(possible_dyks):
            return None
        rand_dyk = random.choice(possible_dyks)
        dyk_id = rand_dyk["id"]
        dyk_text = rand_dyk["text"]
        next_same_announcement_date = now + datetime.timedelta(seconds= self.settings.dyk_cooldown)
        self.update_dyk_date(dyk_id, next_same_announcement_date)
        return dyk_text