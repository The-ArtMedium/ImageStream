import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.core.window import Window
from kivy.utils import platform

# Android Specific Permissions
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
        layout = FloatLayout(canvas_bg_color=(0.02, 0.02, 0.02, 1))
        
        # Title: LocalClip
        self.add_widget(Label(
            text="[b]Local[color=f5a623]Clip[/color][/b]",
            markup=True, font_size='40sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.7}
        ))
        
        self.add_widget(Label(
            text="Lossless. Offline. Sovereign.",
            font_size='14sp', color=(0.5, 0.5, 0.5, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.62}
        ))

        # The Button that now "Acts"
        btn = Button(
            text="SELECT SOURCE VIDEO",
            size_hint=(0.7, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            font_size='18sp',
            bold=True
        )
        btn.bind(on_release=self.open_file_picker)
        self.add_widget(btn)

    def open_file_picker(self, instance):
        # This is where the "Nerves" connect
        print("Opening Sovereign Vault...")
        # In a full build, this triggers the Kivy FileChooser or Android Intent
        # For now, we ensure the console logs the attempt to debug the 'nothing'
        self.manager.current = 'editor'

class EditorScreen(Screen):
    # Placeholder for the Trimming UI
    pass

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
