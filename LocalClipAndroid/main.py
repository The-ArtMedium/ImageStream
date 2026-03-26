import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.utils import get_color_from_hex, platform
from kivy.metrics import dp, sp

# --- ANDROID PERMISSIONS BLOCK ---
# This ensures the app can access your high-bitrate video in the field.
if platform == 'android':
    from android.permissions import request_permissions, Permission

class HomeScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        # UI: Dark, Minimalist, High-Contrast
        # Designed for high-glare environments (stadiums/fields)
        with layout.canvas.before:
            from kivy.graphics import Color, Rectangle
            Color(*get_color_from_hex("#050505")) # Deep Black
            self.rect = Rectangle(pos=layout.pos, size=layout.size)
            layout.bind(pos=self.update_rect, size=self.update_rect)

        # Branding: The "Sovereign" Logo
        label = Label(
            text="Local[color=#f5a623]Clip[/color]", 
            markup=True,
            font_size=sp(48), 
            bold=True,
            pos_hint={'center_x': .5, 'center_y': .7}
        )
        
        tagline = Label(
            text="Lossless. Offline. Sovereign.",
            font_size=sp(16),
            color=(0.6, 0.6, 0.6, 1),
            pos_hint={'center_x': .5, 'center_y': .62}
        )
        
        # The Primary Action Node
        btn = Button(
            text="SELECT SOURCE VIDEO",
            size_hint=(None, None),
            size=(dp(260), dp(65)),
            pos_hint={'center_x': .5, 'center_y': .4},
            background_color=get_color_from_hex("#f5a623"),
            background_normal='', # Disables the default grey tint
            color=(0, 0, 0, 1),   # Black text on orange button
            bold=True
        )
        
        layout.add_widget(label)
        layout.add_widget(tagline)
        layout.add_widget(btn)
        self.add_widget(layout)

    def update_rect(self, instance, value):
        self.rect.pos = instance.pos
        self.rect.size = instance.size

class LocalClipApp(App):
    def build(self):
        # Requesting "The Keys" to the storage
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
    # Start the Node
    LocalClipApp().run()
