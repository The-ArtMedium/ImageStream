import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.clock import Clock
from kivy.utils import platform

# THE UI: Black & Orange High-Contrast Architecture
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
            font_size: '48sp'
            color: 1, 1, 1, 1
            size_hint_y: 0.4
            
        Button:
            text: 'SELECT MASTER FOOTAGE'
            size_hint: (0.8, 0.15)
            pos_hint: {'center_x': 0.5}
            background_normal: ''
            background_color: 0.98, 0.69, 0.23, 1
            color: 0, 0, 0, 1
            font_size: '18sp'
            bold: True
            on_release: app.open_file_chooser()
            
        Widget:
            size_hint_y: 0.2

<EditorScreen>:
    video_path: ""
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        Video:
            id: vid
            source: root.video_path
            state: 'play'
            options: {'allow_stretch': True, 'eos': 'loop'}
            
        BoxLayout:
            size_hint_y: 0.15
            padding: 10
            spacing: 10
            Button:
                text: 'BACK'
                background_color: 0.2, 0.2, 0.2, 1
                color: 1, 1, 1, 1
                on_release: app.root.current = 'menu'
''')

class MenuScreen(Screen): pass
class EditorScreen(Screen):
    video_path = StringProperty("")

class Manager(ScreenManager): pass

class LocalClipApp(App):
    def build(self):
        # Trigger permission dialog 1 second after startup
        if platform == 'android':
            Clock.schedule_once(self.ask_permissions, 1)
        return Manager()

    def ask_permissions(self, dt):
        try:
            from android.permissions import request_permissions, Permission
            # Specifically requesting access for your video archives
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.MANAGE_EXTERNAL_STORAGE,
                Permission.READ_MEDIA_VIDEO
            ])
        except Exception as e:
            print(f"Sovereign Error: Permission Dialog Failed - {e}")

    def open_file_chooser(self):
        from plyer import filechooser
        # Opens the native Android picker
        filechooser.open_file(on_selection=self.load_video)

    def load_video(self, selection):
        if selection:
            # Strip the file:// prefix so FFmpeg can read the path
            path = selection[0].replace('file://', '')
            if os.path.exists(path):
                editor = self.root.get_screen('editor')
                editor.video_path = path
                self.root.current = 'editor'
            else:
                print(f"Path Witness Failed: {path}")

if __name__ == '__main__':
    LocalClipApp().run()
