from kivy.app import App
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.screenmanager import ScreenManager, Screen

import game
import settings


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


class NBackApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MenuScreen(name='menu'))
        sm.add_widget(game.GameScreen(name='game'))
        sm.add_widget(settings.SettingScreen(name='settings'))
        # return game
        return sm

if __name__ == '__main__':
    NBackApp().run()