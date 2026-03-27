import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

# --- The Handshake: This is what makes the button WORK ---
def request_android_permissions():
    from android.permissions import request_permissions, Permission
    request_permissions([
        Permission.READ_EXTERNAL_STORAGE,
        Permission.WRITE_EXTERNAL_STORAGE,
        Permission.READ_MEDIA_VIDEO
    ])

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        # UI: Deep Black & Sovereign Orange
        self.add_widget(Label(
            text="[b]Local[color=f5a623]Clip[/color][/b]",
            markup=True, font_size='42sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        ))
        
        # The Button that triggers the Action
        btn = Button(
            text="SELECT SOURCE VIDEO",
            size_hint=(0.8, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            font_size='20sp',
            bold=True
        )
        btn.bind(on_release=self.go_to_editor)
        self.add_widget(btn)

    def go_to_editor(self, instance):
        # This print logs to 'buildozer logcat' so we can see it working
        print("ACTION: Moving to Editor Node")
        self.manager.current = 'editor'

class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.add_widget(Label(text="Editor Active", pos_hint={'center_y': 0.5}))

class LocalClipApp(App):
    def build(self):
        if platform == 'android':
            request_android_permissions()
        
        from kivy.core.window import Window
        Window.clearcolor = (0.02, 0.02, 0.02, 1)
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
