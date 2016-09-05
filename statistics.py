#!/usr/bin/env python
from mock import MagicMock

__author__ = 'Tomas Novacik'

import datetime
import unittest
import sqlite3 as lite


class TestStatistic(unittest.TestCase):

    TEST_DB_NAME = "test_statistics.sqlite3"
    NAME_COL = 1
    ITEM_COUNT_COL = 4
    TEST_ITEM = [3, 0.8, 0.9, 0.7, 20]

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

    def test_db_basic_operation(self):
        """Inserted items into db should be equal to gathered items"""
        self.stats.add(*self.TEST_ITEM)
        actual_item = self.stats.get(self.TEST_ITEM[0])
        self.assertEquals(self.TEST_ITEM[1:-1], list(actual_item[0]))

    def test_session_played(self):
        """Test that session played correctly work as expected"""
        played_sessions = 10
        test_item = [3, 0.8, 0.9, 0.7, 20]
        # insert correct items
        for i in xrange(played_sessions):
            self.stats.add(*test_item)

        # insert sessions from different day
        dummy_year = 1990
        for i in xrange(played_sessions):
            dummy_date = datetime.datetime(dummy_year, 1, 1)
            self.stats.add(*test_item, date=dummy_date)
            dummy_year += 1
        self.assertEqual(self.stats.session_played(), played_sessions)

    def test_item_tested(self):
        total_items = 0
        # insert items with current date
        for i in xrange(10):
            self.stats.add(*self.TEST_ITEM)
            total_items += self.TEST_ITEM[self.ITEM_COUNT_COL]

        # insert items with some other date
        dummy_year = 1990
        for i in xrange(10):
            dummy_date = datetime.datetime(dummy_year, 1, 1)
            self.stats.add(*self.TEST_ITEM, date=dummy_date)
            dummy_year += 1
        self.assertEqual(self.stats.items_tested(), total_items)

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
    COUNT_COL = "count"
    TABLE_COLS = [ DATE_COL, LEVEL_COL, POSITION_COL, SHAPE_COL, SUCCESS_COL,
                  COUNT_COL]

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
        overall success rate and items displayed during session"""
        q = "CREATE TABLE %s (%s date PRIMARY KEY default current_timestamp,"\
            "%s integer, %s real, %s real, %s real, %s integer)"
        q %= tuple([self.TABLE_NAME] + self.TABLE_COLS)
        self.connection.execute(q)
        self.connection.commit()

    def add(self, level, position, shape, success, item_count, date=None):
        """Add game results"""
        if date is None:
            date = datetime.datetime.now()
        q = "INSERT INTO %s (%s, %s, %s, %s, %s, %s)" \
            " values (?, ?, ?, ?, ?, ?)"
        q %= tuple([self.TABLE_NAME] + self.TABLE_COLS)
        self.connection.execute(q, (date, level, position, shape, success,
                                    item_count))
        self.connection.commit()

    def get(self, level):
        """Gather new statistics for given n-back level"""
        q = "SELECT %s, %s, %s FROM %s where %s == ?"
        q %= (self.POSITION_COL, self.SHAPE_COL, self.SUCCESS_COL,
              self.TABLE_NAME, self.LEVEL_COL)
        cur = self.connection.execute(q, (level,))
        return cur.fetchall()

    def session_played(self, date=None):
        """Returns how many sessions have been played on given day"""
        if date is None:
            date = datetime.date.today().isoformat()
        q = "select COUNT(*) from %s" \
            " where date >= date(?) AND date <  date(?, '+1 day')"
        q %= self.TABLE_NAME
        cur = self.connection.execute(q, (date, date))
        return cur.fetchone()[0]

    def items_tested(self, date=None):
        """Returns how many items were tested on given day"""
        if date is None:
            date = datetime.date.today().isoformat()
        q = "select SUM(%s) from %s" \
            " where date >= date(?) AND date <  date(?, '+1 day')"
        q %= (self.COUNT_COL, self.TABLE_NAME)
        cur = self.connection.execute(q, (date, date))
        return cur.fetchone()[0]

# eof
