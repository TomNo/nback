#!/usr/bin/env python
from mock import MagicMock

__author__ = 'Tomas Novacik'

import datetime
import inspect
import unittest
import sqlite3 as lite


class TestStatistic(unittest.TestCase):

    TEST_DB_NAME = "test_statistics.sqlite3"
    NAME_COL = 1
    ITEM_COUNT_COL = 4
    SUCCESS_RATE_COL = 3
    TEST_ITEM = [3, 0.8, 0.9, 0.7, 20]
    DUMMY_YEAR = 1990
    DUMMY_DAY = 1
    DUMMY_MONTH = 1
    DUMMY_DATE = datetime.datetime(DUMMY_YEAR, DUMMY_MONTH, DUMMY_DAY)

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

    def test_sessions_played(self):
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
        self.assertEqual(self.stats.sessions_played(), played_sessions)

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
        self.assertEqual(self.stats.tested_items(), total_items)

    def test_success_rate(self):
        # no items
        self.assertEqual(self.stats.success_rate(), 0)

        rows = [
            [3, 0.8, 0.9, 0.7, 20],
            [3, 0.8, 0.9, 0.8, 21],
            [3, 0.8, 0.9, 0.6, 19],
            [3, 0.8, 0.9, 0.5, 31]
        ]
        # rows that should be part of computation
        for row in rows:
            self.stats.add(*row)

        # row that should be excluded from computation
        self.stats.add(*rows[0], date=self.DUMMY_DATE)

        expected_success_rate = 0.0
        items_count = 0.0
        for row in rows:
            expected_success_rate += row[self.SUCCESS_RATE_COL] *\
                                     row[self.ITEM_COUNT_COL]
            items_count += row[self.ITEM_COUNT_COL]

        expected_success_rate /= items_count
        self.assertEqual(self.stats.success_rate(), expected_success_rate)


DATE_ARG = "date"

def set_date_if_not_set(fn):
    """Automatically sets the date argument of a function/method
    to current date if not set."""
    def wrapper(*args, **kwargs):
        # check that date arg is present
        arg_names = inspect.getargspec(fn)[0]
        try:
            date_position = arg_names.index(DATE_ARG)
        except ValueError:
            raise ValueError("This function cannot be decorated as it does not"
                             " have date arg in its definition.")

        if DATE_ARG not in kwargs and len(args) <= date_position:
            kwargs[DATE_ARG] = datetime.datetime.now()
        return fn(*args, **kwargs)
    return wrapper


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

    @set_date_if_not_set
    def add(self, level, position, shape, success, item_count, date=None):
        """Add game results"""
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

    @set_date_if_not_set
    def sessions_played(self, date=None):
        """Returns how many sessions have been played on given day"""
        q = "select COUNT(*) from %s" \
            " where date >= date(?) AND date <  date(?, '+1 day')"
        q %= self.TABLE_NAME
        cur = self.connection.execute(q, (date, date))
        return cur.fetchone()[0]

    @set_date_if_not_set
    def tested_items(self, date=None):
        """Returns how many items were tested on given day"""
        q = "select SUM(%s) from %s" \
            " where date >= date(?) AND date <  date(?, '+1 day')"
        q %= (self.COUNT_COL, self.TABLE_NAME)
        cur = self.connection.execute(q, (date, date)).fetchone()[0]
        result = 0 if cur is None else cur
        return result

    @set_date_if_not_set
    def success_rate(self, date=None):
        q = "select %s, %s from %s" \
            " where date >= date(?) AND date <  date(?, '+1 day')"
        q %= (self.COUNT_COL, self.SUCCESS_COL, self.TABLE_NAME)
        rows = self.connection.execute(q, (date, date)).fetchall()
        success = 0.0
        item_count = 0.0
        if rows:
            for row in rows:
                success += row[0] * row[1]
                item_count += row[0]
            success /= item_count
        return success
# eof
