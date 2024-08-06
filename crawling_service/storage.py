import sqlite3


def get_db_connection(db_name):
    try:
        conn = sqlite3.connect(db_name) # Cretes if not exists
        return conn
    except Exception as e:
        return str(e)



