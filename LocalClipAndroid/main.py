import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty
from android.permissions import request_permissions, Permission

# The UI - Clean, Black, Focused
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
            font_size: '40sp'
            size_hint_y: 0.3
        Button:
            text: 'SELECT MASTER FOOTAGE'
            size_hint: (0.8, 0.15)
            pos_hint: {'center_x': 0.5}
            background_color: 1, 0.7, 0, 1
            on_release: app.open_file_chooser()

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

class MenuScreen(Screen):
    pass

class EditorScreen(Screen):
    video_path = StringProperty("")

class Manager(ScreenManager):
    pass

class LocalClipApp(App):
    def build(self):
        # Requesting access to your equestrian archives immediately
        request_permissions([
            Permission.READ_EXTERNAL_STORAGE,
            Permission.WRITE_EXTERNAL_STORAGE,
            Permission.MANAGE_EXTERNAL_STORAGE
        ])
        return Manager()

    def open_file_chooser(self):
        from plyer import filechooser
        filechooser.open_file(on_selection=self.load_video)

    def load_video(self, selection):
        if selection:
            # Clean Android path pollution
            path = selection[0].replace('file://', '')
            
            if os.path.exists(path):
                # Witnessing begins here
                self.root.get_screen('editor').video_path = path
                self.root.current = 'editor'
            else:
                print(f"Sovereign Error: File at {path} not found.")

if __name__ == '__main__':
    LocalClipApp().run()
