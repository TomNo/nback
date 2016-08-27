#!/usr/bin/env python
import unittest

from kivy.core.window import Window
from kivy.properties import NumericProperty
from kivy.uix.anchorlayout import AnchorLayout

__author__ = 'Tomas Novacik'

import random
import mock

from kivy.clock import Clock
from kivy.graphics import Color, Rectangle
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from basic_screen import BasicScreen

# TODO too much code duplication
# reformat using test generating approach
class TestGameEvaluation(unittest.TestCase):

    PREV_POSITION = 1
    PREV_SHAPE = 2
    GUI_DT = 10

    def setUp(self):
        self.game = GameLayout()
        self.game._set_config_vals = mock.MagicMock()
        self.game.build()
        self.game.positions = [self.PREV_POSITION]
        self.game.shapes = [self.PREV_SHAPE]
        self.game.a_shape = self.PREV_SHAPE
        self.game.a_position = self.PREV_POSITION

    def _game_eval(self):
        # eval must be called with some delta time
        self.game._evaluate(self.GUI_DT)

    def test_mistake_shape_clicked(self):
        self.game.a_shape = self.PREV_SHAPE + 1
        self.game.n_clicked = True
        self._game_eval()
        self.assertTrue(self.game.n_err)

    def test_mistake_shape_not_clicked(self):
        self.game.a_shape = self.PREV_SHAPE
        self.game.n_clicked = False
        self._game_eval()
        self.assertTrue(self.game.n_err)

    def test_mistake_position_clicked(self):
        self.game.a_position = self.PREV_POSITION + 1
        self.game.p_clicked = True
        self._game_eval()
        self.assertTrue(self.game.p_err)

    def test_mistake_position_not_clicked(self):
        self.game.a_position = self.PREV_POSITION
        self.game.p_clicked = False
        self._game_eval()
        self.assertTrue(self.game.p_err)

    def test_success_position_clicked(self):
        self.game.a_position = self.PREV_POSITION
        self.game.p_clicked = True
        self._game_eval()
        self.assertFalse(self.game.p_err)

    def test_success_position_not_clicked(self):
        self.game.a_position = self.PREV_POSITION + 1
        self.game.p_clicked = False
        self._game_eval()
        self.assertFalse(self.game.p_err)

    def test_success_shape_clicked(self):
        self.game.a_shape = self.PREV_SHAPE
        self.game.n_clicked = True
        self._game_eval()
        self.assertFalse(self.game.n_err)

    def test_success_shape_not_clicked(self):
        self.game.a_shape = self.PREV_SHAPE + 1
        self.game.n_clicked = False
        self._game_eval()
        self.assertFalse(self.game.n_err)


class GameScreen(BasicScreen):

    def __init__(self, *args, **kwargs):
        super(GameScreen, self).__init__(*args, **kwargs)
        with self.canvas.before:
            Color(0.6, 0.65, 0.65)
            self.rect = Rectangle(size=self.size, pos=self.pos)

        self.bind(size=self._update_rect, pos=self._update_rect)

    def _update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

    def on_enter(self, *args):
        self.game = GameLayout()
        self.add_widget(self.game)
        self.game.build()
        self.game.start()

    def on_leave(self, *args):
        Clock.unschedule(self.game.step)
        self.remove_widget(self.game)
        self.game = None


class CellLabel(Label):
    pass

GREEN = (0,1,0,1)
RED = (1,0,0,1)


class GameLayout(GridLayout):

    GAME_CONFIG_SECTION = "game"
    POSITION_MATCH_KEYBIND = ord('a')
    SHAPE_MATCH_KEYBIND = ord('f')
    CLEAR_INTERVAL = 0.2
    EVALUATE_INTERVAL = 0.3
    DEFAULT_BUTTON_COLOR = (0.8, 0.8, 0.8, 1)
    BTN_SIZE_HINT = (0.3, 0.3)
    SHAPES = range(1,10)
    POSITIONS = range(9)
    STATS_POPUP_SIZE_HINT = (.35, .35)
    INFO_LABEL_SIZE_HINT = (.1, .1)
    GRID_SIZE = 9

    iter = NumericProperty(None)
    p_errors = NumericProperty(None)
    s_errors = NumericProperty(None)

    def _get_config(self, opt_name):
        return self.parent.config.get(self.GAME_CONFIG_SECTION, opt_name)

    def _set_config_vals(self):
        self.history = int(self._get_config("level"))
        self.max_iter = int(self._get_config("max_iter"))
        self.step_duration = float(self._get_config("step_duration"))

    def _action_keys(self, window, key, *args):
        # bind to 'position match' and 'shape match'
        if key == self.POSITION_MATCH_KEYBIND and not self.p_clicked:
            self.p_btn.trigger_action()
        elif key == self.SHAPE_MATCH_KEYBIND and not self.n_clicked:
            self.n_btn.trigger_action()

    def build(self):
        self._set_config_vals()
        self.cols = 3
        self.rows = 5
        self.spacing = 5

        def create_info_label():
            return Label(size_hint=self.INFO_LABEL_SIZE_HINT)

        position_info = create_info_label()
        shape_info = create_info_label()
        overall_info = create_info_label()

        def update_position_info(instance, value):
            position_info.text = "Incorrect positions: %s" % value

        self.bind(p_errors=update_position_info)

        def update_shape_info(instance, value):
            shape_info.text = "Incorrect shapes: %s" % value

        self.bind(s_errors=update_shape_info)

        def update_overall_info(instance, value):
            overall_info.text = "%s / %s" %(value, self.max_iter)

        self.bind(iter=update_overall_info)

        self.add_widget(position_info)
        self.add_widget(shape_info)
        self.add_widget(overall_info)

        self.cells = []
        for _ in xrange(self.GRID_SIZE):
            label = CellLabel()
            self.cells.append(label)
            self.add_widget(label)

        self.p_btn = Button(text="A: Position match",
                            size_hint=self.BTN_SIZE_HINT,
                            on_release=self.position_callback)
        self.add_widget(self.p_btn)
        self.n_btn = Button(text="F: Shape match", size_hint=self.BTN_SIZE_HINT,
                            on_release=self.shape_callback)

        self.add_widget(self.n_btn)
        # disable buttons at the start
        self.p_btn.disabled = True
        self.n_btn.disabled = True

    def position_callback(self, instance):
        self.p_clicked = True

    def shape_callback(self, instance):
        self.n_clicked = True

    def rand_shape(self):
        return random.choice(self.SHAPES + self.shapes)

    def rand_position(self):
        return random.choice(self.POSITIONS + self.positions)

    def new_cell(self):
        self.a_shape, self.a_position = self.rand_shape(), self.rand_position()
        self.actual_cell = self.cells[self.a_position]
        self.actual_cell.text = str(self.a_shape)
        self.p_clicked = False
        self.n_clicked = False

    def start(self):
        self.iter = 0
        self.s_errors = 0
        self.p_errors = 0

        self.p_clicked = False
        self.n_clicked = False

        self.positions = []
        self.shapes = []

        self.new_cell()
        Clock.schedule_interval(self.step, self.step_duration)
        self._schedule_cell_clearing()

    def _evaluate(self, dt):
        # using xor
        self.p_err = (self.positions[0] == self.a_position) != self.p_clicked
        self.n_err = (self.shapes[0] == self.a_shape) != self.n_clicked

        self.p_errors += self.p_err
        self.s_errors += self.n_err

        # change buttons background color depending on success/fail
        if self.positions[0] == self.a_position or self.p_clicked:
            self.p_btn.background_color = RED if self.p_err else GREEN
        if self.shapes[0] == self.a_shape or self.n_clicked:
            self.n_btn.background_color = RED if self.n_err else GREEN


    def display_statistics(self):
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(Label(text=self.get_stats(), font_size='20sp'))
        def to_menu(instance):
            popup.dismiss()
            self.parent.manager.move_to_previous_screen()
        anchor_layout = AnchorLayout(anchor_x='right', anchor_y='center')
        btn = Button(text="ok", on_press=to_menu,
                     size_hint=self.BTN_SIZE_HINT)
        anchor_layout.add_widget(btn)
        layout.add_widget(anchor_layout)
        popup = Popup(title='Game finished',
            content=layout, auto_dismiss=True,
            size_hint=self.STATS_POPUP_SIZE_HINT)
        popup.open()

    def _clear_cell(self, dt):
        self.actual_cell.text = ""

    def _schedule_cell_clearing(self):
        Clock.schedule_once(self._clear_cell,
                            self.step_duration - self.CLEAR_INTERVAL)

    def step(self, dt):
        self.iter += 1

        if self.iter >= self.history and self.iter < self.max_iter:
            Clock.schedule_once(self._evaluate, dt - self.EVALUATE_INTERVAL)

        if self.iter >= self.max_iter:
            Clock.unschedule(self.step)
            Window.unbind(on_keyboard=self._action_keys)
            self.p_btn.disabled = True
            self.n_btn.disabled = True
            self.display_statistics()
            return
        else:
            self._schedule_cell_clearing()

        if len(self.positions) >= self.history:
            del(self.positions[0])
            del(self.shapes[0])

        self.positions.append(self.a_position)
        self.shapes.append(self.a_shape)
        self.new_cell()

        # enable buttons if it make sense to click
        if self.iter >= self.history:
            self.p_btn.background_color = self.DEFAULT_BUTTON_COLOR
            self.n_btn.background_color = self.DEFAULT_BUTTON_COLOR
            self.p_btn.disabled = False
            self.n_btn.disabled = False
            Window.bind(on_keyboard=self._action_keys)

    def get_stats(self):
        total_iters = self.iter - self.history
        c_position = (1 - self.p_errors / total_iters) * 100
        c_shape = (1 - self.s_errors / total_iters) * 100
        all_errors = self.p_errors + self.s_errors
        s_rate = 1 - (all_errors / (2 * total_iters))
        s_rate *= 100
        return "Samples count: %s\n"\
               "Correct positions: %.2f%%\n"\
               "Correct shapes: %.2f%%\n"\
               "Overall success: %.2f%%" % (total_iters,
                                          c_position,
                                          c_shape,
                                          s_rate)
# eof
