import os
import logging
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.label import Label
from kivy.clock import Clock
from kivy.utils import platform

# Setup logging to see what's happening internally
logging.basicConfig(level=logging.DEBUG)

class LoadingScreen(Screen):
    def on_enter(self):
        # We wait 2 seconds to let Android stabilize before switching
        Clock.schedule_once(self.check_permissions, 2)

    def check_permissions(self, dt):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_MEDIA_VIDEO
            ])
        self.manager.current = 'main'

class MainScreen(Screen):
    # (The rest of your Select Video code goes here...)
    pass

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(LoadingScreen(name='loading'))
        # Adding a simple label to the loading screen
        sm.get_screen('loading').add_widget(Label(text="IGNITING ENGINES..."))
        return sm
