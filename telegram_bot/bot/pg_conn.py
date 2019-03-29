import logging
import time
import os

import psycopg2
import psycopg2.pool


class pgConn():
    cursor = None

    def __init__(self):
        self.pool = self.connect()

    def __del__(self):
        self.pool.closeall()

    def connect(self):
        while True:
            try:
                pool = psycopg2.pool.ThreadedConnectionPool(
                    minconn=os.environ.get("MINCONN"),
                    maxconn=os.environ.get("MAXCONN"),
                    host=os.environ.get("HOST"),
                    port=os.environ.get("PORT"),
                    user=os.environ.get("POSTGRES_USER"),
                    password=os.environ.get("POSTGRES_PASSWORD"),
                    database=os.environ.get("POSTGRES_DB"),
                )

            except (psycopg2.OperationalError, psycopg2.DatabaseError) as err:
                logging.error(err)
                time.sleep(1)
            else:
                return pool

    def get_conn(self):
        while True:
            try:
                conn = self.pool.getconn()
            except psycopg2.DatabaseError as err:
                logging.error(err)
                time.sleep(1)
            else:
                conn.autocommit = True
                return conn

    def add_user_data(self, telegram_id, name, photo, place_point):
        conn = self.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                '''
                INSERT INTO users_data (telegram_id, name, photo, place_point)
                VALUES (%s, %s, %s, %s)''',
                (telegram_id, name, photo, place_point)
            )
        except psycopg2.DatabaseError as err:
            logging.error(err)
        else:
            cur.close()
        finally:
            self.pool.putconn(conn)


    def reset_user_data(self, telegram_id):
        conn = self.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                '''
                DELETE FROM users_data WHERE telegram_id=%s''',
                (telegram_id,)
            )
        except psycopg2.DatabaseError as err:
            logging.error(err)
        else:
            cur.close()
        finally:
            self.pool.putconn(conn)


    def get_user_list(self, telegram_id, longitude, latitude, distance=500):
        conn = self.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                '''
                SELECT *, (place_point <-> POINT(%s,%s))*100000 AS distance FROM users_data WHERE
                 telegram_id=%s AND (place_point <-> POINT(%s,%s))*100000 < %s''',
                ( latitude, longitude, telegram_id, latitude, longitude, distance)
            )
            result = cur.fetchall()
        except psycopg2.DatabaseError as err:
            logging.error(err)
        else:
            cur.close()
            return result
        finally:
            self.pool.putconn(conn)
