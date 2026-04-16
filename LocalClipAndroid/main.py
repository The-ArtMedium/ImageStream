import os
import webbrowser
import subprocess
import threading
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        # Title
        layout.add_widget(Label(
            text="[b]Local[color=f5a623]Clip[/color][/b]",
            markup=True, font_size='48sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        ))
        
        # Main Action Button
        btn = Button(
            text="SELECT VIDEO",
            size_hint=(0.8, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.45},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='', color=(0, 0, 0, 1), bold=True
        )
        btn.bind(on_release=self.open_picker)
        layout.add_widget(btn)

        # Support Note & Button
        note = Label(
            text="If this tool helps you, consider supporting the work:",
            font_size='12sp', color=(0.7, 0.7, 0.7, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.18}
        )
        layout.add_widget(note)

        support_btn = Button(
            text="SUPPORT ON KO-FI",
            size_hint=(0.5, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            background_color=(0.2, 0.6, 1, 1),
            background_normal='', color=(1, 1, 1, 1)
        )
        support_btn.bind(on_release=lambda x: webbrowser.open("https://ko-fi.com/1satdiva"))
        layout.add_widget(support_btn)

        self.add_widget(layout)

    def open_picker(self, *args):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            from android.storage import primary_external_storage_path
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.MANAGE_EXTERNAL_STORAGE,
                "android.permission.READ_MEDIA_VIDEO"
            ])
            start_path = primary_external_storage_path()
        else:
            start_path = os.path.expanduser("~")

        content = FloatLayout()
        fc = FileChooserListView(path=start_path, filters=['*.mp4'], size_hint=(1, 0.85), pos_hint={'x': 0, 'y': 0.15})
        content.add_widget(fc)
        popup = Popup(title="Select Video", content=content, size_hint=(0.95, 0.9))
        
        def on_open(*args):
            if fc.selection:
                popup.dismiss()
                self.manager.get_screen('editor').video_path = fc.selection[0].replace('file://', '')
                self.manager.current = 'editor'

        sel_btn = Button(text="OPEN", size_hint=(0.4, 0.1), pos_hint={'x': 0.05, 'y': 0.02}, background_color=(0.96, 0.65, 0.14, 1), color=(0,0,0,1))
        sel_btn.bind(on_release=on_open)
        content.add_widget(sel_btn)
        popup.open()

class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.player = None

    def on_enter(self):
        self.setup_ui()
        # Delay for Tablet Virtual RAM to stabilize
        Clock.schedule_once(self.load_engine, 1.0)

    def load_engine(self, dt):
        try:
            from ffpyplayer.player import MediaPlayer
            self.player = MediaPlayer(self.video_path, ff_opts={'paused': True, 'an': True})
        except Exception as e:
            self.status.text = f"Hardware Error: {e}"

    def setup_ui(self):
        self.clear_widgets()
        layout = FloatLayout()
        self.status = Label(text="Ready", pos_hint={'center_y': 0.1})
        layout.add_widget(self.status)
        back_btn = Button(text="← BACK", size_hint=(0.2, 0.07), pos_hint={'x': 0.02, 'top': 0.98})
        back_btn.bind(on_release=lambda *a: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)
        self.add_widget(layout)

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
