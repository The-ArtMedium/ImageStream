import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

# --- Android Permission Handshake ---
if platform == 'android':
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_MEDIA_VIDEO
    ])

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        # Deep Black Background
        layout = FloatLayout()
        
        # Title: LocalClip
        self.add_widget(Label(
            text="[b]Local[color=f5a623]Clip[/color][/b]",
            markup=True, font_size='42sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        ))
        
        self.add_widget(Label(
            text="Lossless. Offline. Sovereign.",
            font_size='16sp', color=(0.6, 0.6, 0.6, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.68}
        ))

        # The Sovereign Action Button
        btn = Button(
            text="SELECT SOURCE VIDEO",
            size_hint=(0.8, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_color=(0.96, 0.65, 0.14, 1), # Sovereign Orange
            background_normal='',
            color=(0, 0, 0, 1), # Black text for contrast
            font_size='20sp',
            bold=True
        )
        btn.bind(on_release=self.go_to_editor)
        self.add_widget(btn)

    def go_to_editor(self, instance):
        print("Sovereign Node Activated: Moving to Editor")
        self.manager.current = 'editor'

class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        layout.add_widget(Label(text="Video Editor Node Active", pos_hint={'center_y': 0.8}))
        
        back_btn = Button(
            text="BACK",
            size_hint=(0.4, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            background_color=(0.3, 0.3, 0.3, 1)
        )
        back_btn.bind(on_release=self.go_back)
        self.add_widget(back_btn)

    def go_back(self, instance):
        self.manager.current = 'main'

class LocalClipApp(App):
    def build(self):
        # Set window color to deep black
        from kivy.core.window import Window
        Window.clearcolor = (0.02, 0.02, 0.02, 1)
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
