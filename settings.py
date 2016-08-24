#!/usr/bin/env python

__author__ = 'Tomas Novacik'

from kivy.uix.screenmanager import Screen


class SettingsLayout():
    pass


class SettingScreen(Screen):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)

    def on_enter(self, *args):
        pass


# eof
