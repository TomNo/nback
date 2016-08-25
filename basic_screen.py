#!/usr/bin/env python
from kivy.app import App

__author__ = 'Tomas Novacik'

from kivy.uix.screenmanager import Screen

class BasicScreen(Screen):
    """Adds configuration property to every screen object on initialization."""

    def __init__(self, *args, **kwargs):
        super(BasicScreen, self).__init__(*args, **kwargs)
        self.config = App.get_running_app().config
# eof
