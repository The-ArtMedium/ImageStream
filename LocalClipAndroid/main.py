import os, subprocess, threading, time, urllib.parse
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.clock import Clock
from kivy.utils import platform
from kivy.uix.widget import Widget

# NEW (ExoPlayer bridge)
from jnius import autoclass
from android.runnable import run_on_ui_thread

# Global Translation Dictionary
LOCALES = {
    'en': {'select': "SELECT MASTER", 'load': "LOAD", 'in': "SET IN", 'out': "SET OUT", 'save': "SAVE", 'ready': "Ready", 'saving': "Saving...", 'close': "CLOSE"},
}
L = LOCALES.get('en')

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        btn = Button(text=L['select'], size_hint=(0.8, 0.12),
                     pos_hint={'center_x': 0.5, 'center_y': 0.25})
        btn.bind(on_release=self.open_picker)
        layout.add_widget(btn)

        self.add_widget(layout)

    def open_picker(self, *args):
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                "android.permission.READ_MEDIA_VIDEO"
            ])
            start_path = primary_external_storage_path()
        else:
            start_path = os.path.expanduser("~")

        content = FloatLayout()
        self.fc = FileChooserListView(
            path=start_path,
            filters=['*.mp4', '*.mov'],
            size_hint=(1, 0.85),
            pos_hint={'y': 0.15}
        )

        load_btn = Button(text=L['load'],
                          size_hint=(0.9, 0.1),
                          pos_hint={'center_x': 0.5, 'y': 0.02})

        content.add_widget(self.fc)
        content.add_widget(load_btn)

        self.popup = Popup(title="Search",
                           content=content,
                           size_hint=(0.95, 0.9))

        load_btn.bind(on_release=self.on_load)
        self.popup.open()

    def on_load(self, *args):
        if self.fc.selection:
            path = urllib.parse.unquote(
                self.fc.selection[0].replace('file://', '')
            )
            self.popup.dismiss()
            self.manager.get_screen('editor').video_path = path
            self.manager.current = 'editor'


class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""

    def on_enter(self):
        self.setup_ui()
        self.init_exoplayer()

    def setup_ui(self):
        self.clear_widgets()
        layout = FloatLayout()

        # Placeholder where video will appear
        self.video_container = Widget(
            size_hint=(1, 0.5),
            pos_hint={'top': 1}
        )
        layout.add_widget(self.video_container)

        # Simple label so you see UI still works
        self.status = Label(text="Loading video...",
                            pos_hint={'y': 0.1})
        layout.add_widget(self.status)

        self.add_widget(layout)

    @run_on_ui_thread
    def init_exoplayer(self):
        PythonActivity = autoclass('org.kivy.android.PythonActivity')
        activity = PythonActivity.mActivity

        ExoPlayerBuilder = autoclass(
            'com.google.android.exoplayer2.ExoPlayer$Builder')
        PlayerView = autoclass(
            'com.google.android.exoplayer2.ui.PlayerView')
        MediaItem = autoclass(
            'com.google.android.exoplayer2.MediaItem')
        Uri = autoclass('android.net.Uri')
        LayoutParams = autoclass(
            'android.view.ViewGroup$LayoutParams')

        self.exo_player = ExoPlayerBuilder(activity).build()

        uri = Uri.parse("file://" + self.video_path)
        media_item = MediaItem.fromUri(uri)

        self.exo_player.setMediaItem(media_item)
        self.exo_player.prepare()
        self.exo_player.play()

        self.player_view = PlayerView(activity)
        self.player_view.setPlayer(self.exo_player)

        params = LayoutParams(
            LayoutParams.MATCH_PARENT,
            LayoutParams.MATCH_PARENT
        )

        activity.addContentView(self.player_view, params)


class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm


if __name__ == '__main__':
    LocalClipApp().run()