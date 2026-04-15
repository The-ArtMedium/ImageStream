import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.utils import platform

# Your UI - Solid Black, Bold Orange
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
            background_color: 0.98, 0.69, 0.23, 1
            color: 0, 0, 0, 1
            on_release: app.open_file_chooser()
        Widget:
            size_hint_y: 0.2

<EditorScreen>:
    BoxLayout:
        orientation: 'vertical'
        Video:
            id: player
            source: root.video_path
            state: 'play'
            options: {'allow_stretch': True}
        Button:
            text: 'BACK'
            size_hint_y: 0.1
            on_release: app.root.current = 'menu'
''')

class MenuScreen(Screen): pass
class EditorScreen(Screen):
    video_path = StringProperty("")

class Manager(ScreenManager): pass

class LocalClipApp(App):
    def build(self):
        return Manager()

    def open_file_chooser(self):
        # We wrap the call in Clock to prevent the "Selection Crash"
        # This gives the UI a chance to "breath" before opening the system picker
        Clock.schedule_once(self._trigger_picker, 0.1)

    def _trigger_picker(self, dt):
        try:
            from plyer import filechooser
            filechooser.open_file(on_selection=self.load_video)
        except Exception as e:
            print(f"Sovereign Error: Picker failed - {e}")

    def load_video(self, selection):
        if selection:
            # Absolute path only for the engine
            path = selection[0].replace('file://', '')
            if os.path.exists(path):
                self.root.get_screen('editor').video_path = path
                self.root.current = 'editor'

if __name__ == '__main__':
    LocalClipApp().run()
