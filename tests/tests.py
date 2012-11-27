import unittest
import psycopg2
import os

import goose


class TestLoad(unittest.TestCase):

    def setUp(self):
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

        self.goose = goose.Goose(self.conn)

    def tearDown(self):
        self.cursor.close()
        self.conn.close()

    def test_loads_data(self):
        fixture = os.path.join(
            os.path.dirname(__file__), 'fixtures',
            'initial_data.csv')
        self.goose.load(self.table, fixture, ('isbn', 'price', 'stock'))
        sql = "SELECT COUNT(*) FROM %s" % self.table
        self.cursor.execute(sql)
        row = self.cursor.fetchone()
        self.assertEqual(16, row[0])
