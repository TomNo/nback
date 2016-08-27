#!/usr/bin/env python
from kivy.uix.label import Label

from basic_screen import BasicScreen

__author__ = 'Tomas Novacik'


class AboutScreen(BasicScreen):

    def on_enter(self):
        self.info_text = Label(text="bla")
        self.add_widget(self.info_text)

    def on_exit(self):
        self.remove_widget(self.info_text)
        del self.info_text


# eof
