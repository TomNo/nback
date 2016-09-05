#!/usr/bin/env python

__author__ = 'Tomas Novacik'

import sqlite3 as lite
import unittest

# TODO tests

class TestStatistic(unittest.TestCase):

    TEST_DB_NAME = "test_statistics.sqlite3"
    NAME_COL = 1

    def setUp(self):
        self.stats = Statistics(self.TEST_DB_NAME)

    def tearDown(self):
        # remove db file
        import os
        if os.path.exists(self.TEST_DB_NAME):
            os.remove(self.TEST_DB_NAME)

    def test_db_init(self):
        """Initial db should contain table and basic columns"""
        # get column names
        cols = self.stats.connection.execute("PRAGMA table_info(%s);"
                                             % self.stats.TABLE_NAME).fetchall()
        col_names = {row[self.NAME_COL] for row in cols}
        self.assertEqual(col_names, set(self.stats.TABLE_COLS))

    def test_db_operation(self):
        """Inserted items into db should be equal to gathered items"""
        test_item = [3, 0.8, 0.9, 0.7]
        self.stats.add(*test_item)
        actual_item = self.stats.get(test_item[0])
        self.assertEquals(test_item[1:], list(actual_item[0]))


class Statistics(object):
    """Store overall statistics """

    # db constants
    DB_NAME = "statistics.sqlite3"
    TABLE_NAME = "statistics"
    POSITION_COL = "position"
    SHAPE_COL = "shape"
    SUCCESS_COL = "success"
    LEVEL_COL = "level"
    DATE_COL = "date"
    TABLE_COLS = [POSITION_COL, SHAPE_COL, SUCCESS_COL, LEVEL_COL, DATE_COL]

    def __init__(self, db_name = DB_NAME):
        self.db_name = db_name
        self.connection = lite.connect(self.db_name)
        if not self._table_exists(self.TABLE_NAME):
            self._create_statistics_table()


    def _table_exists(self, table_name):
        query = "SELECT name FROM sqlite_master WHERE type=? AND name=?"
        result = self.connection.execute(query, ("table", table_name))
        return bool(result.fetchone())


    def _create_statistics_table(self):
        """Create statistics table that contains current timestamp as id,
        nback level, position success rate, shape success rate,
        overall success rate"""
        q = "CREATE TABLE %s (%s date PRIMARY KEY default current_timestamp,"\
            "%s integer, %s real, %s real, %s real)"
        q %= (self.TABLE_NAME, self.DATE_COL, self.LEVEL_COL, self.POSITION_COL,
              self.SHAPE_COL, self.SUCCESS_COL)
        self.connection.execute(q)
        self.connection.commit()

    def add(self, level, position, shape, success):
        """Add game results"""
        q = "INSERT INTO %s (%s, %s, %s, %s)" \
            " values (?, ?, ?, ?)"
        q %= (self.TABLE_NAME, self.LEVEL_COL, self.POSITION_COL,
              self.SHAPE_COL, self.SUCCESS_COL)
        self.connection.execute(q, (level, position, shape, success))
        self.connection.commit()

    def get(self, level):
        """Gather new statistics for given n-back level"""
        q = "SELECT %s, %s, %s FROM %s where %s = ?"
        q %= (self.POSITION_COL, self.SHAPE_COL, self.SUCCESS_COL,
              self.TABLE_NAME, self.LEVEL_COL)
        cur = self.connection.execute(q, (level,))
        return cur.fetchall()

# eof
