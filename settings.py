#!/usr/bin/env python
from kivy.properties import ObjectProperty
from kivy.uix.settings import Settings

__author__ = 'Tomas Novacik'

import os
from kivy.uix.screenmanager import Screen
from kivy.config import ConfigParser


class NBackSettings(Settings):
    SETTINGS_FILENAME = "config.ini"
    GAME_SETTINGS_PANEL = "game_settings.json"

    config_parser = ObjectProperty(None)

    def load_settings(self):
        self.config_parser = ConfigParser()
        if not os.path.exists(self.SETTINGS_FILENAME):
            raise IOError("Cannot locate configuration file.")
        self.config_parser.read(self.SETTINGS_FILENAME)
        self.add_json_panel("Game settings", self.config_parser,
                            self.GAME_SETTINGS_PANEL)

    def on_config_change(self, *args):
        self.config_parser.write()
        super(self.__class__, self).on_config_change(*args)

    def on_close(self, *args):
        self.parent.manager.move_to_previous_screen()

class SettingScreen(Screen):
    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    def on_enter(self, *args):
        self.settings = NBackSettings()
        self.settings.load_settings()
        self.add_widget(self.settings)

    def on_leave(self, *args):
        pass

# eof
