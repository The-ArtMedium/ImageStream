import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.utils import platform

# UI Definition - Solid Black background to match the "Sovereign" goal
Builder.load_string('''
<Manager>:
    MenuScreen:
        name: 'menu'
    EditorScreen:
        name: 'editor'

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        Label:
            text: 'LocalClip'
            font_size: '42sp'
            size_hint_y: 0.4
        Button:
            text: 'SELECT MASTER FOOTAGE'
            size_hint: (0.8, 0.15)
            pos_hint: {'center_x': 0.5}
            background_color: 1, 0.7, 0, 1
            on_release: app.open_file_chooser()
        Widget:
            size_hint_y: 0.2

<EditorScreen>:
    video_path: ""
    BoxLayout:
        orientation: 'vertical'
        Video:
            id: player
            source: root.video_path
            state: 'play'
            options: {'allow_stretch': True}
        Button:
            text: 'BACK'
            size_hint: (1, 0.1)
            on_release: app.root.current = 'menu'
''')

class MenuScreen(Screen): pass
class EditorScreen(Screen):
    video_path = StringProperty("")

class Manager(ScreenManager): pass

class LocalClipApp(App):
    def build(self):
        # Only request permissions if we are actually on Android
        if platform == 'android':
            Clock.schedule_once(self.ask_permissions, 1)
        return Manager()

    def ask_permissions(self, dt):
        try:
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE, 
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.MANAGE_EXTERNAL_STORAGE
            ])
        except Exception as e:
            print(f"Permission delay failed: {e}")

    def open_file_chooser(self):
        from plyer import filechooser
        filechooser.open_file(on_selection=self.load_video)

    def load_video(self, selection):
        if not selection:
            return
        
        # Strip prefixes and ensure absolute path
        raw_path = selection[0]
        path = raw_path.replace('file://', '')
        
        if os.path.exists(path):
            self.root.get_screen('editor').video_path = path
            self.root.current = 'editor'

if __name__ == '__main__':
    LocalClipApp().run()
