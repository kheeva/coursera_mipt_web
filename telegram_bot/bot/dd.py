from pg_conn import pgConn


db = pgConn()

db.add_user_data(11, '123.11'.encode(), '(1.11, 2.11)')
