#!/usr/bin/env python
from kivy.core.window import Window

__author__ = 'Tomas Novacik'

from random import randint

from kivy.clock import Clock
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.gridlayout import GridLayout
from kivy.uix.label import Label
from kivy.uix.popup import Popup

from basic_screen import BasicScreen


class Statistics(object):

    def __init__(self):
        self.p_errors = 0.0
        self.n_errors = 0.0
        self.iters = 0.0

    def add_result(self, pos, num):
        self.iters += 1
        self.p_errors += pos
        self.n_errors += num

    def __str__(self):
        c_pos = (1 - self.p_errors / self.iters) * 100
        c_num = (1 - self.n_errors / self.iters) * 100
        s_rate = 1 - ((self.p_errors + self.n_errors) / (2 * self.iters))
        s_rate *= 100
        return "Samples count: %s\n"\
               "Correct positions: %.2f%%\n"\
               "Correct numbers: %.2f%%\n"\
               "Overall success: %.2f%%" % (self.iters,
                                          c_pos,
                                          c_num,
                                          s_rate)


class GameScreen(BasicScreen):

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

GREEN = (0,1,0)
RED = (1,0,0)

class GameLayout(GridLayout):

    GAME_CONFIG_SECTION = "game"

    def _get_config(self, opt_name):
        return self.parent.config.get(self.GAME_CONFIG_SECTION, opt_name)

    def _set_config_vals(self):
        self.history = int(self._get_config("level"))
        self.max_iter = int(self._get_config("max_iter"))
        self.step_duration = float(self._get_config("step_duration"))

    def _action_keys(self, window, key, *args):
        # bind to 'position match' and 'shape match'
        if key == ord('a') and not self.p_clicked:
            self.p_btn.trigger_action()
        elif key == ord('f') and not self.n_clicked:
            self.n_btn.trigger_action()

    def build(self):
        self._set_config_vals()
        self.cols = 3
        self.rows = 4
        self.spacing = 10
        self.p_clicked = False
        self.n_clicked = False
        self.stats = Statistics()

        self.cells = []
        for _ in xrange(self.cols * self.rows - 3):
            label = CellLabel()
            self.cells.append(label)
            self.add_widget(label)

        self.p_btn = Button(text="A: Position match", on_release=self.pos_callback)
        self.add_widget(self.p_btn)
        self.n_btn = Button(text="F: Shape match", on_release=self.num_callback)

        self.add_widget(self.n_btn)
        # disable buttons at the start
        self.p_btn.disabled = True
        self.n_btn.disabled = True

    def pos_callback(self, instance):
        self.p_clicked = True
        instance.disabled = True

    def num_callback(self, instance):
        self.n_clicked = True
        instance.disabled = True

    def rand_num(self):
        return randint(0, 8)

    def new_cell(self):
        self.a_num, self.a_pos = self.rand_num(), self.rand_num()
        self.a_cell = self.cells[self.a_pos]
        self.a_cell.text = str(self.a_num)
        self.p_clicked = False
        self.n_clicked = False

    def start(self):
        self.new_cell()
        self.iter = 0
        self.pos_list = []
        self.num_list = []
        Clock.schedule_interval(self.step, self.step_duration)

    def evaluate(self):
        # using xor
        p_err = self.pos_list[0] == self.a_pos ^ self.p_clicked
        n_err = self.num_list[0] == self.a_num ^ self.n_clicked
        self.stats.add_result(p_err, n_err)

        if self.pos_list[0] == self.a_pos or self.p_clicked \
            or self.num_list[0] == self.a_num or self.n_clicked:
            self.p_btn.background_color = RED if p_err else GREEN
            self.n_btn.background_color = RED if n_err else GREEN


    def display_statistics(self):
        layout = BoxLayout(orientation="vertical")
        layout.add_widget(Label(text=str(self.stats)))
        def to_menu(instance):
            popup.dismiss()
            self.parent.manager.move_to_previous_screen()
        btn = Button(text="okay", on_press=to_menu, size=(100,100))
        layout.add_widget(btn)
        popup = Popup(title='Game finished',
            content=layout, auto_dismiss=False,
            size_hint=(None, None), size=(200, 200))
        popup.open()

    def step(self, dt):
        if self.iter >= self.history:
            self.evaluate()
        self.a_cell.text = ""

        if self.iter >= self.max_iter:
            Clock.unschedule(self.step)
            Window.unbind(on_keyboard=self._action_keys)
            self.p_btn.disabled = True
            self.n_btn.disabled = True
            self.display_statistics()
            return

        if len(self.pos_list) > self.history:
            del(self.pos_list[0])
            del(self.num_list[0])

        self.pos_list.append(self.a_pos)
        self.num_list.append(self.a_num)
        self.new_cell()

        # enable buttons if it make sense to click
        if self.iter >= self.history - 1:
            self.p_btn.disabled = False
            self.n_btn.disabled = False
            Window.bind(on_keyboard=self._action_keys)
        self.iter += 1

# eof
