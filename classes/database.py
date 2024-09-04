import psycopg2
# import psycopg2.extras
from psycopg2.extras import RealDictCursor


class Database:
    def __init__(self) -> any:
        pass

    def connect_db(self)->any:
        conn = psycopg2.connect(
            host="localhost",
            database="billrecord",
            Usuario="admin_billrecord",
            password="alexander1995")
        return conn


    # def create_cursor(self) -> any:
    #     self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)

    # def get_cursor(self) -> any:
    #     return self.cursor

    # def query_all(self, query:str) -> any:
    #     self.cursor.execute(query)
    #     return self.cursor.fetchall()

    # def query_one(self, query:str) -> any:
    #     self.cursor.execute(query)
    #     return self.cursor.fetchone()

    # def close_cursor(self) -> any:
    #     self.cursor.close()

    # def close_connection(self) -> any:
    #     self.conn.close()
    
    def execute_one(self, query:str) -> any:
        try:
            conn = self.connect_db()
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            result = cursor.fetchone()
            conn.commit()
            cursor.close()
            return result
        except Exception as e:
            conn.rollback()
            raise e

    # def execute_all(self, query:str) -> any:
    #     try:
    #         self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
    #         self.cursor.execute(query)
    #         result = self.cursor.fetchall()
    #         self.conn.commit()
    #         self.cursor.close()
    #         return result
    #     except Exception as e:
    #         self.conn.rollback()
    #         raise e
    
    def transaction(self, query:str, conn:any) -> tuple:
        try:
            cursor = conn.cursor(cursor_factory=RealDictCursor)
            cursor.execute(query)
            result = cursor.fetchall()
            return (result, cursor)
        except Exception as e:
            conn.rollback()
            raise Exception(e)
            
    def transaction_execute(self, query:str, cursor:any, conn: any) -> tuple:
        try:
            cursor.execute(query)
            result = cursor.fetchall()
            return (result, cursor)
        except Exception as e:
            conn.rollback()
            raise e
    
    def transaction_close(self, conn:any, cursor:any) -> None:
        try:
            conn.commit()
            cursor.close()
        except Exception as e:
            conn.rollback()
            raise e