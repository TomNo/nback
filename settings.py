#!/usr/bin/env python
from kivy.uix.settings import Settings

from basic_screen import BasicScreen

__author__ = 'Tomas Novacik'


class NBackSettings(Settings):
    GAME_SETTINGS_PANEL = "game_settings.json"

    def __init__(self,*args, **kwargs):
        super(self.__class__, self).__init__(*args, **kwargs)

    def create_panels(self, config):
        self.add_json_panel("Game settings", config,
                            self.GAME_SETTINGS_PANEL)

    def on_config_change(self, *args):
        self.parent.config.write()
        super(self.__class__, self).on_config_change(*args)

    def on_close(self, *args):
        self.parent.manager.move_to_previous_screen()

class SettingScreen(BasicScreen):

    def on_enter(self, *args):
        self.settings = NBackSettings()
        self.settings.create_panels(self.config)
        self.add_widget(self.settings)

    def on_leave(self, *args):
        self.remove_widget(self.settings)
        del self.settings

# eof
