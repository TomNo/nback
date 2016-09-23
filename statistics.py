#!/usr/bin/env python
from kivy.app import App
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.label import Label
from kivy.uix.spinner import Spinner

# it is necessary to patch the graph package and set stencil_buffer to false
# otherwise points are not visible
from kivy.garden.graph import Graph, MeshLinePlot

Graph._with_stencilbuffer = False

from basic_screen import BasicScreen

__author__ = 'Tomas Novacik'

import datetime
import inspect
import unittest
import sqlite3 as lite


class TestStatistic(unittest.TestCase):

    TEST_DB_NAME = "test_statistics.sqlite3"
    NAME_COL = 1
    LEVEL_COL = 0
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

    def test_played_levels(self):
        # no items
        self.assertEqual(len(self.stats.played_levels()), 0)
        expected_levels = set(range(1,6))
        for _ in xrange(2):
            for i in expected_levels:
                # add 5 items with different levels
                item = [y for y in self.TEST_ITEM]
                item[self.LEVEL_COL] = i
                self.stats.add(*item)
        self.assertEqual(self.stats.played_levels(), expected_levels)

    def test_success_rates_no_items(self):
        # no items
        self.assertEqual(len(self.stats.success_rates()), 0)

    def test_success_rates_all_items(self):
        expected_rates = [0.1, 0.2, 0.4, 0.5, 0.3]
        for i in expected_rates:
            test_item = [y for y in self.TEST_ITEM]
            test_item[self.SUCCESS_RATE_COL] = i
            self.stats.add(*test_item)
        self.assertEqual(self.stats.success_rates(), expected_rates)

    def test_success_rates_specific_level(self):
        test_rates = [0.1, 0.2, 0.4, 0.5, 0.3]
        test_level = 3
        span = range(1,3)
        for addition in span:
            for index, item in enumerate(test_rates):
                test_item = [y for y in self.TEST_ITEM]
                test_item[self.LEVEL_COL] = index + addition
                test_item[self.SUCCESS_RATE_COL] = item
                self.stats.add(*test_item)
        expected_rates = [test_rates[test_level - i] for i in span]
        self.assertEqual(self.stats.success_rates(level=test_level),
                         expected_rates)


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

    def success_rates(self, level=None):
        q = "select %s from %s where %s = ? ORDER BY %s ASC"
        params = None
        values = None
        # if level is None select all success rates for any level
        if level is None:
            params = (self.SUCCESS_COL, self.TABLE_NAME, 1,
                      self.DATE_COL)
            values = (1,)
        else:
            params = (self.SUCCESS_COL, self.TABLE_NAME, self.LEVEL_COL,
                      self.DATE_COL)
            values = (level, )
        q %= params
        rates = [i[0] for i in self.connection.execute(q, values).fetchall()]
        return rates

    def played_levels(self):
        """Gathers from db the overall set of different levels played."""
        q = "select distinct %s from %s"
        q %= (self.LEVEL_COL, self.TABLE_NAME)
        rows = self.connection.execute(q)
        levels = [row[0] for row in rows.fetchall()]
        return set(levels)

class SuccessGraph(object):

    PLOT_LINE_COLOR = [1, 0, 0, 1]
    DEFAULT_LEVEL = "Overall"

    X_LABEL = "sessions"
    Y_LABEL = "success rates"

    Y_MAX_VAL = 100

    HISTORY_MAX = 200

    def __init__(self):
        self._plot = MeshLinePlot(color=self.PLOT_LINE_COLOR)
        self._graph = Graph(xlabel=self.X_LABEL, ylabel=self.Y_LABEL,
                            x_ticks_major=25, x_ticks_minor=5,
                            y_ticks_major=10, y_ticks_minor=2, y_grid=True,
                            y_grid_label=True, x_grid_label=True, padding=10,
                            xmin=0, ymin=0, ymax=self.Y_MAX_VAL,
                            xmax=self.HISTORY_MAX)
        self._graph.add_plot(self._plot)
        self.display_level(self.DEFAULT_LEVEL)

    def display_level(self, level):
        if self.DEFAULT_LEVEL == level:
            level = None
        else:
            level = int(level)
        success_rates =  App.get_running_app().stats.success_rates(level)
        self._plot.points = [(x, y) for x, y in enumerate(success_rates)]

    def get_view(self):
        return self._graph

class StatisticsScreen(BasicScreen):

    HEADING_TEXT = "Statistics"
    HEADING_FONT_SIZE = "55sp"
    HEADING_SIZE_HINT = (1, 0.05)

    STATISTICS_SIZE_HINT = (1, 0.2)
    STATISTICS_INFO_TEXT = "Select 'N'- back level in order \nto display specific" \
                           " statistics:"
    STATISTICS_INFO_FONT_SIZE = "15sp"
    STATISTICS_INFO_SIZE_HINT = (0.65, .1)

    STATISTICS_ANCHOR_SIZE_HINT = (0.3, 1)

    SPINNER_SIZE_HINT = (1, 0.1)

    def _build_heading_view(self):
        """Adds screen heading"""
        anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center',
                                     size_hint=self.HEADING_SIZE_HINT)
        heading_label = Label(text=self.HEADING_TEXT,
                              font_size=self.HEADING_FONT_SIZE)
        anchor_layout.add_widget(heading_label)
        return anchor_layout


    def _build_statistics_view(self):
        """Adds spinner and graph with default values for overall progress"""
        box_layout = BoxLayout(orientation='horizontal',
                               size_hint=self.STATISTICS_SIZE_HINT)

        self.graph = SuccessGraph()
        box_layout.add_widget(self.graph.get_view())

        level_played = App.get_running_app().stats.played_levels()
        level_played = [str(lvl) for lvl in level_played]

        spinner_choices = [SuccessGraph.DEFAULT_LEVEL] + level_played

        anchor_layout = AnchorLayout(anchor_y='top', anchor_x="center",
                                     size_hint=self.STATISTICS_ANCHOR_SIZE_HINT)


        selection_layout = BoxLayout(orientation="vertical",
                                     size_hint=self.STATISTICS_INFO_SIZE_HINT,
                                     spacing=30)

        info_label = Label(text=self.STATISTICS_INFO_TEXT,
                           font_size=self.STATISTICS_INFO_FONT_SIZE)

        spinner = Spinner(text=SuccessGraph.DEFAULT_LEVEL,
                          values=spinner_choices,
                          size_hint=self.SPINNER_SIZE_HINT)

        selection_layout.add_widget(info_label)
        selection_layout.add_widget(spinner)

        anchor_layout.add_widget(selection_layout)

        box_layout.add_widget(anchor_layout)

        def show_success_rate_statistics(spinner, text):
            self.graph.display_level(text)
        spinner.bind(text=show_success_rate_statistics)
        return box_layout

    def on_enter(self, *args):
        box_layout = BoxLayout(orientation="vertical")
        for widget in [self._build_heading_view(), self._build_statistics_view()]:
            box_layout.add_widget(widget)
        anchor_layout = AnchorLayout(anchor_x='center', anchor_y='center')
        anchor_layout.add_widget(box_layout)
        self.add_widget(anchor_layout)


    def on_leave(self, *args):
        self.clear_widgets()

# eof
