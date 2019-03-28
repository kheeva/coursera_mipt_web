import logging
import time
import os
from os.path import join, dirname

from dotenv import load_dotenv

import psycopg2
import psycopg2.pool


class pgConn():
    db = None
    cursor = None
    engine = None
    cnf = None

    def __init__(self):
        dotenv_path = join(dirname(__file__), '.env')
        load_dotenv(dotenv_path)
        # self.cnf = cnf
        self.pool = self.connect()

    def __del__(self):
        self.pool.closeall()

    def connect(self):
        # cnf = self.cnf
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

    def add_user_data(self, telegram_id, photo, place_point):
        conn = self.get_conn()
        try:
            cur = conn.cursor()
            cur.execute(
                '''
                INSERT INTO users_data (telegram_id, photo, place_point)
                VALUES (%s, %s, %s)''',
                (telegram_id, photo, place_point)
            )
        except psycopg2.DatabaseError as err:
            logging.error(err)
        else:
            cur.close()
        finally:
            self.pool.putconn(conn)
