import sqlite3
from contextlib import contextmanager
from typing import Generator

class DatabaseManager:
    def __init__(self, db_path: str = 'meal_recommender_new.db'):
        self.db_path = db_path
        self.init_database()

    def init_database(self):
        """Initialize the database and create necessary tables."""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    id INTEGER PRIMARY KEY,
                    prefered_flavors TEXT,
                    prefered_types TEXT,
                    dietary_restrictions TEXT
                )
            ''')
            conn.commit()

    @contextmanager
    def get_connection(self) -> Generator[sqlite3.Connection, None, None]:
        """Context manager to get a database connection."""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        finally:
            conn.close()