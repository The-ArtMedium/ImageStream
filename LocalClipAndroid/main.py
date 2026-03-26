import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex, platform
from kivy.metrics import dp, sp

if platform == 'android':
    from android.permissions import request_permissions, Permission

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        # UI for the Field Professional
        label = Label(
            text="Local[color=#f5a623]Clip[/color]", 
            markup=True,
            font_size=sp(42), 
            pos_hint={'center_x': .5, 'center_y': .7}
        )
        tagline = Label(
            text="Lossless. Offline. Sovereign.",
            font_size=sp(16),
            color=(0.7, 0.7, 0.7, 1),
            pos_hint={'center_x': .5, 'center_y': .6}
        )
        
        btn = Button(
            text="PICK VIDEO",
            size_hint=(None, None),
            size=(dp(240), dp(60)),
            pos_hint={'center_x': .5, 'center_y': .4},
            background_color=get_color_from_hex("#f5a623"),
            background_normal=''
        )
        
        layout.add_widget(label)
        layout.add_widget(tagline)
        layout.add_widget(btn)
        self.add_widget(layout)

class LocalClipApp(App):
    def build(self):
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_MEDIA_VIDEO
            ])
        sm = ScreenManager()
        sm.add_widget(HomeScreen(name='home'))
        return sm

if __name__ == "__main__":
    LocalClipApp().run()
