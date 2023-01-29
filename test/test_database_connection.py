import unittest
import os
import database.connection as db_conn
from database.information import DatabaseInformation
import test.data_for_tests as data


class TestDatabaseCreation(unittest.TestCase):
    db_conn = None
    db_inf = None
    db_file = 'test.db'

    @classmethod
    def setUpClass(cls) -> None:
        cls.db_conn = db_conn.DatabaseConnection(cls.db_file)
        cls.db_inf = DatabaseInformation(cls.db_conn.curs)

    @classmethod
    def tearDownClass(cls) -> None:
        """Delete database"""
        del cls.db_conn
        del cls.db_inf
        os.remove(cls.db_file)

    def test_Creation(self):
        self.assertTrue(os.path.exists(self.db_file))

    def test_CreateTables(self):
        """Create a database structure and test if all tables that should exist are created"""
        tables_in_db = self.db_inf.get_names(types='table')
        self.assertSetEqual(tables_in_db, data.database_tables)

    def test_CreateViews(self):
        views_in_db = self.db_inf.get_names(types='view')
        self.assertSetEqual(views_in_db, data.database_views)

    def test_FilledTables(self):
        for table in data.database_tables:
            if table in ('learning_state', 'playlist_config', 'playlist'):
                count_table = self.db_inf.count_rows(table)
                self.assertGreater(count_table, 0)
            else:
                count_table = self.db_inf.count_rows(table)
                self.assertEqual(count_table, 0, msg=f'Problem with table {table}')
