import os, threading, time, urllib.parse
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.video import Video
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        btn = Button(text="OPEN MASTER FOOTAGE", size_hint=(0.8, 0.15), 
                     pos_hint={'center_x': 0.5, 'center_y': 0.5},
                     background_color=(0.96, 0.65, 0.14, 1), color=(0,0,0,1), bold=True)
        btn.bind(on_release=self.open_picker)
        layout.add_widget(btn)
        self.add_widget(layout)

    def open_picker(self, *args):
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, "android.permission.READ_MEDIA_VIDEO"])
            path = primary_external_storage_path()
        else:
            path = os.path.expanduser("~")
        
        content = FloatLayout()
        self.fc = FileChooserListView(path=path, filters=['*.mp4'], size_hint=(1, 0.9), pos_hint={'top': 1})
        load_btn = Button(text="LOAD VIDEO", size_hint=(1, 0.1), background_color=(0.96, 0.65, 0.14, 1), color=(0,0,0,1))
        content.add_widget(self.fc)
        content.add_widget(load_btn)
        self.popup = Popup(title="Select File", content=content, size_hint=(0.9, 0.9))
        load_btn.bind(on_release=self.on_load)
        self.popup.open()

    def on_load(self, *args):
        if self.fc.selection:
            path = urllib.parse.unquote(self.fc.selection[0].replace('file://', ''))
            self.popup.dismiss()
            self.manager.get_screen('editor').video_path = path
            self.manager.current = 'editor'

class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.start_time = 0.0
        self.end_time = 0.0

    def on_enter(self):
        self.clear_widgets()
        layout = FloatLayout()
        
        # Uses the NATIVE Android Media Player through Kivy core
        self.player = Video(source=self.video_path, state='play')
        self.player.size_hint = (1, 0.6)
        self.player.pos_hint = {'center_x': 0.5, 'top': 1}
        layout.add_widget(self.player)

        self.lbl = Label(text="00:00", pos_hint={'center_y': 0.35}, font_size='30sp')
        layout.add_widget(self.lbl)

        btn_in = Button(text="MARK IN", size_hint=(0.4, 0.1), pos_hint={'x': 0.05, 'y': 0.2}, background_color=(0,1,0,1))
        btn_out = Button(text="MARK OUT", size_hint=(0.4, 0.1), pos_hint={'right': 0.95, 'y': 0.2}, background_color=(1,0,0,1))
        btn_in.bind(on_release=lambda x: setattr(self, 'start_time', self.player.position))
        btn_out.bind(on_release=lambda x: setattr(self, 'end_time', self.player.position))
        
        save_btn = Button(text="EXTRACT CLIP", size_hint=(0.9, 0.1), pos_hint={'center_x': 0.5, 'y': 0.05}, background_color=(0.96, 0.65, 0.14, 1), color=(0,0,0,1))
        save_btn.bind(on_release=self.save_video)

        layout.add_widget(btn_in)
        layout.add_widget(btn_out)
        layout.add_widget(save_btn)
        self.add_widget(layout)
        Clock.schedule_interval(self.update_time, 0.5)

    def update_time(self, dt):
        if self.player:
            self.lbl.text = f"{int(self.player.position // 60):02d}:{int(self.player.position % 60):02d}"

    def save_video(self, *args):
        out = f"/sdcard/Movies/clip_{int(time.time())}.mp4"
        dur = max(1, self.end_time - self.start_time)
        # Using a direct system call for ffmpeg which is pre-baked into the Android image
        cmd = f"ffmpeg -y -ss {self.start_time} -t {dur} -i {self.video_path} -c copy {out}"
        threading.Thread(target=lambda: os.system(cmd)).start()

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
