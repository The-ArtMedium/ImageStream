import os
from kivy.app import App
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.utils import platform
from kivy.clock import Clock

class LocalClipApp(App):
    def build(self):
        # 1. IMMEDIATE PERMISSION TRIGGER
        # We do this first. If it doesn't trigger, nothing else matters.
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            request_permissions([
                Permission.READ_MEDIA_VIDEO,
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE
            ])

        # 2. UI INITIALIZATION
        self.root = FloatLayout()
        self.video_path = ""
        self.player = None

        self.main_btn = Button(
            text="SELECT VIDEO",
            size_hint=(0.8, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.5},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='', color=(0, 0, 0, 1)
        )
        self.main_btn.bind(on_release=self.open_picker)
        self.root.add_widget(self.main_btn)
        
        self.status = Label(text="System Initialized", pos_hint={'center_y': 0.1})
        self.root.add_widget(self.status)

        return self.root

    def open_picker(self, *args):
        # Using the standard shared path for modern Android
        if platform == 'android':
            from android.storage import primary_external_storage_path
            path = primary_external_storage_path()
        else:
            path = os.path.expanduser("~")
        
        content = FloatLayout()
        self.fc = FileChooserListView(
            path=path, 
            filters=['*.mp4'], 
            size_hint=(1, 0.85), 
            pos_hint={'top': 1},
            multiselect=False
        )
        content.add_widget(self.fc)
        
        self.popup = Popup(title="Select Video File", content=content, size_hint=(0.95, 0.95))
        
        sel_btn = Button(
            text="LOAD CLIP", 
            size_hint=(1, 0.1),
            background_color=(0.96, 0.65, 0.14, 1),
            color=(0, 0, 0, 1)
        )
        sel_btn.bind(on_release=self.confirm_selection)
        content.add_widget(sel_btn)
        self.popup.open()

    def confirm_selection(self, *args):
        if self.fc.selection:
            self.video_path = self.fc.selection[0].replace('file://', '')
            self.popup.dismiss()
            self.status.text = f"Selected: {os.path.basename(self.video_path)}"
            # Delay to ensure UI updates before ffpyplayer takes over the thread
            Clock.schedule_once(self.init_player, 0.5)

    def init_player(self, dt):
        try:
            # Late import to prevent startup crash
            from ffpyplayer.player import MediaPlayer
            if self.player:
                self.player.close_player()
            # Launching in paused mode to test the file handle
            self.player = MediaPlayer(self.video_path, ff_opts={'paused': True})
            self.status.text = "Engine Loaded Successfully"
        except Exception as e:
            self.status.text = f"Media Error: {e}"

if __name__ == '__main__':
    LocalClipApp().run()
