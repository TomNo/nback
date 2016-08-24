# kivy configuration should precede
# any 'kivy' related import
from kivy import Config
Config.set('kivy', 'exit_on_escape', '0')
Config.write()

from kivy.app import App
from kivy.core.window import Window
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

import game
import settings

# codes that should be handled if user want to go
# to previous screen
BACK_KEY_CODES = [27, 1001]


class MenuScreen(Screen):

    def __init__(self, **kwargs):
        super(self.__class__, self).__init__(**kwargs)
        layout = BoxLayout(orientation='vertical')
        def to_game_screen(instance):
            self.manager.current = "game"

        def to_settings_screen(instance):
            self.manager.current = "settings"

        start_btn = Button(text="start game", on_press=to_game_screen)
        settings_btn = Button(text="settings", on_press=to_settings_screen)
        layout.add_widget(start_btn)
        layout.add_widget(settings_btn)
        self.add_widget(layout)


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
    def build(self):
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

if __name__ == '__main__':
    NBackApp().run()