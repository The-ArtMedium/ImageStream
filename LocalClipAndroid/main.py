import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.utils import platform
from kivy.clock import Clock

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        btn = Button(text="SELECT VIDEO", size_hint=(0.8, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.5})
        btn.bind(on_release=self.open_picker)
        layout.add_widget(btn)
        self.add_widget(layout)

    def open_picker(self, *args):
        # DIRECT PATH: We don't guess. We go to the user's storage.
        path = "/storage/emulated/0/DCIM" if platform == 'android' else os.path.expanduser("~")
        
        content = FloatLayout()
        self.fc = FileChooserListView(path=path, filters=['*.mp4'], size_hint=(1, 0.9), pos_hint={'top': 1})
        content.add_widget(self.fc)
        
        self.popup = Popup(title="Files", content=content, size_hint=(0.9, 0.9))
        sel_btn = Button(text="OPEN", size_hint=(1, 0.1))
        sel_btn.bind(on_release=self.load_video)
        content.add_widget(sel_btn)
        self.popup.open()

    def load_video(self, *args):
        if self.fc.selection:
            # CLEAN PATH: No file:// prefixes, just the raw string.
            vp = self.fc.selection[0].replace('file://', '')
            self.popup.dismiss()
            self.manager.get_screen('editor').video_path = vp
            self.manager.current = 'editor'

class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.player = None

    def on_enter(self):
        # 2-second hard pause to let the hardware "breathe" before loading the video engine
        Clock.schedule_once(self.start_engine, 2.0)

    def start_engine(self, dt):
        try:
            from ffpyplayer.player import MediaPlayer
            self.player = MediaPlayer(self.video_path)
        except Exception as e:
            print(f"HARDWARE FAIL: {e}")

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

    def on_start(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([Permission.READ_MEDIA_VIDEO, Permission.WRITE_EXTERNAL_STORAGE])

if __name__ == '__main__':
    LocalClipApp().run()
