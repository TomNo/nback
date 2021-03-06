# kivy configuration should precede
# any 'kivy' related import
from kivy import Config
from kivy.uix.label import Label

import about
import statistics
from basic_screen import BasicScreen
from statistics import Statistics

Config.set('kivy', 'exit_on_escape', '0')
Config.write()

import os
from kivy.properties import ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager
from kivy.config import ConfigParser
import game
import settings

# TODO add content to about page
# TODO move graphics definitions to separate kv files
# TODO anchor + box layout combination is quite common -> one class

# codes that should be handled if user want to go
# to previous screen
BACK_KEY_CODES = [27, 1001]


class MainScreen(BasicScreen):
    MENU_SPACING = 10
    MENU_SIZE_HINT = (.3, .4)
    APP_HEADING = "Dual %s-back exercise"
    HEADING_SIZE_HINT = (.3, .3)
    INFO_SIZE_HINT = (.3, .1)

    def _get_session_played(self):
        sessions_played = App.get_running_app().stats.sessions_played()
        return "Sessions played today: %s" % sessions_played

    def _get_tested_items(self):
        tested_items = App.get_running_app().stats.tested_items()
        return "Tested items today: %s" % tested_items

    def _get_overall_success(self):
        success_rate = App.get_running_app().stats.success_rate()
        return "Today success rate: %1.f%%" % success_rate

    def _format_heading(self):
        return self.APP_HEADING % self.config.get("game", "level")

    def on_enter(self, *args):
        self.heading_layout = AnchorLayout(anchor_x='center', anchor_y='top')
        heading = Label(text=self._format_heading(), font_size='55sp',
                        size_hint=self.HEADING_SIZE_HINT)
        self.heading_layout.add_widget(heading)
        self.add_widget(self.heading_layout)
        self.menu_layout = AnchorLayout()

        def to_game_screen(instance):
            self.manager.current = "game"

        def to_settings_screen(instance):
            self.manager.current = "settings"

        def to_about_screen(instance):
            self.manager.current = "about"

        def to_statistics_screen(instance):
            self.manager.current = "statistics"

        def exit(instance):
            App.get_running_app().stop()

        # information box with statistics
        self.info_layout = AnchorLayout(anchor_x='center', anchor_y='bottom')

        info_box = BoxLayout(orientation="vertical",
                             size_hint=self.INFO_SIZE_HINT)
        info_labels = [
            Label(text=self._get_session_played()),
            Label(text=self._get_tested_items()),
            Label(text=self._get_overall_success())
        ]

        for label in info_labels:
            info_box.add_widget(label)

        self.info_layout.add_widget(info_box)
        self.add_widget(self.info_layout)

        # menu with buttons to redirect to specific 'pages'
        box_layout = BoxLayout(spacing=self.MENU_SPACING,
                       size_hint=self.MENU_SIZE_HINT,
                       orientation='vertical')
        menu_btns = [
            Button(text="Start game", on_press=to_game_screen),
            Button(text="Statistics", on_press=to_statistics_screen),
            Button(text="Settings", on_press=to_settings_screen),
            Button(text="About", on_press=to_about_screen),
            Button(text="Exit", on_press=exit)
        ]

        for btn in menu_btns:
            box_layout.add_widget(btn)

        self.menu_layout.add_widget(box_layout)
        self.add_widget(self.menu_layout)

    def on_leave(self, *args):
        self.clear_widgets()


class ScreenHistoryManager(ScreenManager):
    """Keep track of visited screens and allow 'back' action."""

    screen_history = []

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        self.bind(current=self._add_screen_to_history)
        self.previous_screen = None

    def _add_screen_to_history(self, instance, screen_name):
        if not self.previous_screen:
            self.previous_screen = screen_name
        else:
            self.screen_history.append(self.previous_screen)

    def move_to_previous_screen(self):
        self.previous_screen = None
        self.current = self.screen_history.pop()


class NBackApp(App):
    SETTINGS_FILENAME = "config.ini"

    config = ObjectProperty(None)

    def build(self):
        self._load_settings()
        # TODO string should be accessed as constant
        db_dir = self.config.get('internal', 'db_path')
        db_location = os.path.join(db_dir, Statistics.DB_NAME)
        self.stats = Statistics(db_location)
        self.sm = ScreenHistoryManager()
        self.sm.add_widget(MainScreen(name='menu'))
        self.sm.add_widget(game.GameScreen(name='game'))
        self.sm.add_widget(settings.SettingScreen(name='settings'))
        self.sm.add_widget(statistics.StatisticsScreen(name='statistics'))
        self.sm.add_widget(about.AboutScreen(name='about'))
        Window.bind(on_keyboard=self._hook_keyboard)
        # return game
        return self.sm

    def add_result(self, level, position, shape, success, items_count):
        self.stats.add(level, position, shape, success, items_count)

    def _hook_keyboard(self, window, key, *args):
        if key in BACK_KEY_CODES:
            try:
                self.sm.move_to_previous_screen()
            except IndexError:
                self.stop()

    def _load_settings(self):
        self.config = ConfigParser()
        if not os.path.exists(self.SETTINGS_FILENAME):
            raise IOError("Cannot locate configuration file.")
        self.config.read(self.SETTINGS_FILENAME)


if __name__ == '__main__':
    NBackApp().run()

# eof
