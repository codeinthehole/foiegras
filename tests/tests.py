import unittest
import psycopg2
import os

import foiegras


class TestLoad(unittest.TestCase):

    def setUp(self):
        # TODO: move creds out of source control
        HOST = "localhost"
        DBNAME = "goose"
        USER = "dwinterbottom"
        self.conn = psycopg2.connect(
            "host=%s dbname=%s user=%s" % (HOST, DBNAME, USER))
        self.cursor = self.conn.cursor()

        # Create table for loading data into
        self.table = 'stock'
        self.cursor.execute("DROP TABLE IF EXISTS %s" % self.table)
        sql = (
            "CREATE TABLE %s ( "
            "    id serial PRIMARY KEY, "
            "    isbn VARCHAR(13) UNIQUE, "
            "    price NUMERIC(12), "
            "    stock INTEGER "
            ")") % (self.table,)
        self.cursor.execute(sql)
        self.conn.commit()

        self.goose = foiegras.Goose(self.conn)

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

    def fixture_path(self, filename):
        return os.path.join(
            os.path.dirname(__file__), 'fixtures',
            filename)

    # Custom asserations

    def assertNumRows(self, expected):
        sql = "SELECT COUNT(*) FROM %s" % self.table
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        self.assertEqual(expected, row[0])

    def assertStockLevel(self, isbn, stock):
        self.cursor.execute(
            "SELECT stock FROM stock WHERE isbn = %s", (isbn,))
        row = self.cursor.fetchone()
        self.assertEqual(stock, row[0])

    # Actual tests

    def test_loads_data(self):
        self.goose.load(self.table,
                        self.fixture_path('initial_data.csv'),
                        ('isbn', 'price', 'stock'))
        self.assertNumRows(16)

    def test_updates_on_duplicates(self):
        self.goose.load(self.table,
                        self.fixture_path('initial_data.csv'),
                        ('isbn', 'price', 'stock'))
        self.goose.load(self.table,
                        self.fixture_path('initial_data.csv'),
                        ('isbn', 'price', 'stock'))
        self.assertNumRows(16)

    def test_inserts_new_records(self):
        self.goose.load(self.table,
                        self.fixture_path('initial_data.csv'),
                        ('isbn', 'price', 'stock'))
        self.goose.load(self.table,
                        self.fixture_path('extra_data.csv'),
                        ('isbn', 'price', 'stock'))
        self.assertNumRows(20)

    def test_partial_update(self):
        self.goose.load(self.table,
                        self.fixture_path('initial_data.csv'),
                        ('isbn', 'price', 'stock'))
        self.assertStockLevel("9780002201438", 10)

        self.goose.load(self.table,
                        self.fixture_path('update.csv'),
                        ('isbn', 'price', 'stock'))
        self.assertStockLevel("9780002201438", 20)

    def test_partial_update_with_ignore(self):
        self.goose.load(self.table,
                        self.fixture_path('initial_data.csv'),
                        ('isbn', 'price', 'stock'))
        self.assertStockLevel("9780002201438", 10)

        self.goose.load(self.table,
                        self.fixture_path('update.csv'),
                        ('isbn', 'price', 'stock'),
                        replace_duplicates=False)
        self.assertStockLevel("9780002201438", 10)

    def test_loads_using_custom_delimiter(self):
        self.goose.load(self.table,
                        self.fixture_path('pipe_separated.csv'),
                        ('isbn', 'price', 'stock'),
                        delimiter="|")
        self.assertNumRows(16)

    def test_allows_header_to_be_ignored(self):
        self.goose.load(self.table,
                        self.fixture_path('with_header.csv'),
                        ('isbn', 'price', 'stock'),
                        has_header=True)
        self.assertNumRows(4)

