from sqlite3 import connect, Connection
import os


class SqliteSingleton:

    _instance: 'SqliteSingleton' = None
    client: Connection

    def __new__(cls, *args, **kwargs) -> 'SqliteSingleton':

        if cls._instance is None:

            cls._instance = super().__new__(cls)
            cls._instance.client = connect(*args, **kwargs)

        return cls._instance


con = SqliteSingleton(os.getenv("DB_NAME"), check_same_thread=False).client

cur = con.cursor()
cur.execute("""
CREATE TABLE IF NOT EXISTS xray(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    is_pid INTEGER NOT NULL CHECK (is_pid IN (0, 1)),
    pid INTEGER NOT NULL,
    created_at TEXT NOT NULL,
    last_used_proxy TEXT NOT NULL
);
""")
cur.close()
