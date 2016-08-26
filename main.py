# kivy configuration should precede
# any 'kivy' related import
import os

from kivy import Config
from kivy.properties import ObjectProperty
from kivy.uix.anchorlayout import AnchorLayout
from kivy.uix.gridlayout import GridLayout

Config.set('kivy', 'exit_on_escape', '0')
Config.write()

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.config import ConfigParser

import game
import settings

# codes that should be handled if user want to go
# to previous screen
BACK_KEY_CODES = [27, 1001]


class MenuScreen(Screen):

    MENU_SPACING = 10
    MENU_SIZE_HINT = (.1, .1)

    def on_enter(self, *args):
        self.menu_layout = AnchorLayout()

        box_layout = BoxLayout(spacing=self.MENU_SPACING,
                               size_hint = self.MENU_SIZE_HINT,
                               orientation='vertical')

        def to_game_screen(instance):
            self.manager.current = "game"

        def to_settings_screen(instance):
            self.manager.current = "settings"

        start_btn = Button(text="Start game", on_press=to_game_screen)
        settings_btn = Button(text="Settings", on_press=to_settings_screen)
        box_layout.add_widget(start_btn)
        box_layout.add_widget(settings_btn)
        self.menu_layout.add_widget(box_layout)
        self.add_widget(self.menu_layout)

    def on_leave(self, *args):
        self.remove_widget(self.menu_layout)
        del self.menu_layout


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
        self.sm = ScreenHistoryManager()
        self.sm.add_widget(MenuScreen(name='menu'))
        self.sm.add_widget(game.GameScreen(name='game'))
        self.sm.add_widget(settings.SettingScreen(name='settings'))
        Window.bind(on_keyboard=self._hook_keyboard)
        # return game
        return self.sm

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