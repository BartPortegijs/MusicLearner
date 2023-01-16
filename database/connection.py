import os
import sqlite3

from config import learning_states, playlist_configs
from database.interaction import DatabaseInteraction

ROOT_DIR = os.path.realpath(os.path.join(os.path.dirname(__file__), '..'))
sql_file = ROOT_DIR + '\\database\\data_structure.sql'


class DatabaseConnection:
    def __init__(self, db_file):
        """ create a database (connection) to a SQLite database """
        self.db_file = db_file
        new_database = not(os.path.exists(db_file))
        self.curs, self.conn = self._get_cursor_and_connect()
        self.db_int = DatabaseInteraction(self.curs, self.conn)
        if new_database:
            self._create_database_structure()

    def _get_cursor_and_connect(self):
        conn = sqlite3.connect(self.db_file)
        curs = conn.cursor()
        curs.execute('PRAGMA foreign_keys = ON;')
        return curs, conn

    def __enter__(self):
        return self.curs, self.conn

    def __exit__(self, exception_type, exception_value, traceback):
        self.conn.close()
        del (self.curs, self.conn)

    def _create_database_structure(self):
        sql = open(sql_file)
        sql_string = sql.read()

        self.curs = self.curs.executescript(sql_string)

        for learning_state in learning_states:
            self.db_int.insert_learning_state(learning_state)
        self.conn.commit()

        for playlist_config in playlist_configs:
            self.db_int.insert_playlist_config(playlist_config)

        self.conn.commit()
