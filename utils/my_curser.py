import logging
import sqlite3
from utils import my_logger as ml


class MyCursor(sqlite3.Cursor):
    def __init__(self, connection, *args, **kwargs):
        super().__init__(connection)
        self.my_logger = logging.getLogger("Lumiel")
        self._connection = connection

    def execute(self, query: str, args=None):
        conn = self._connection

        self.my_logger.debug(f"Executing query: {query}")
        self.my_logger.debug(f"Query executed successfully: {self.rowcount} row(s) affected")

        try:
            if args is not None:
                result = super().execute(query, args)
            else:
                result = super().execute(query)
        except sqlite3.Error as e:
            self.my_logger.warning(f"SQLite error: {e}")
            raise
        self.my_logger.debug(f"Query executed successfully")
        return result
