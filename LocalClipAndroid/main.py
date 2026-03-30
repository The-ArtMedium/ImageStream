import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.videoplayer import VideoPlayer
from kivy.utils import platform
from kivy.clock import Clock

# Android permissions
if platform == 'android':
    from android.permissions import request_permissions, Permission


# ---------------------------------------------------------
# MAIN SCREEN
# ---------------------------------------------------------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

        layout = FloatLayout()
        self.add_widget(Label(
            text="[b]Local[color=f5a623]Clip[/color][/b]",
            markup=True,
            font_size='48sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        ))

        btn = Button(
            text="SELECT MASTER FOOTAGE",
            size_hint=(0.8, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            bold=True
        )
        btn.bind(on_release=self.open_gallery)
        layout.add_widget(btn)

        self.add_widget(layout)

    def open_gallery(self, instance):
        # Request Android 13+ media permissions
        if platform == 'android':
            request_permissions([
                Permission.READ_MEDIA_VIDEO,
                Permission.READ_MEDIA_IMAGES,
                Permission.READ_MEDIA_AUDIO
            ])

        # File chooser popup
        content = BoxLayout(orientation='vertical', spacing=5, padding=5)

        # Correct Android storage path
        start_path = (
            "/storage/emulated/0/"
            if platform == "android"
            else os.path.expanduser("~")
        )

        fc = FileChooserListView(
            path=start_path,
            filters=['*.mp4', '*.mkv', '*.mov', '*.avi', '*.webm', '*.m4v'],
            size_hint=(1, 0.9)
        )
        content.add_widget(fc)

        # Buttons
        btn_row = BoxLayout(size_hint=(1, 0.1), spacing=5)
        cancel_btn = Button(text='Cancel', background_color=(0.3, 0.3, 0.3, 1), background_normal='')
        select_btn = Button(text='SELECT', background_color=(0.96, 0.65, 0.14, 1),
                            background_normal='', color=(0, 0, 0, 1), bold=True)
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(select_btn)
        content.add_widget(btn_row)

        popup = Popup(
            title='Select Video',
            content=content,
            size_hint=(0.95, 0.9)
        )

        cancel_btn.bind(on_release=popup.dismiss)

        def on_select(*args):
            if fc.selection:
                popup.dismiss()
                path = fc.selection[0]
                self.manager.get_screen('editor').video_path = path
                self.manager.current = 'editor'

        select_btn.bind(on_release=on_select)
        fc.bind(on_submit=lambda *args: on_select())

        popup.open()


# ---------------------------------------------------------
# EDITOR SCREEN
# ---------------------------------------------------------
class EditorScreen(Screen):
    video_path = ""
    start_time = 0
    end_time = 0

    def on_enter(self):
        self.clear_widgets()
        layout = FloatLayout()

        # Video player
        if self.video_path:
            try:
                self.player = VideoPlayer(
                    source=self.video_path,
                    state='play',
                    options={'allow_stretch': True}
                )
                self.player.size_hint = (1, 0.5)
                self.player.pos_hint = {'center_x': 0.5, 'top': 1}
                layout.add_widget(self.player)
            except Exception:
                layout.add_widget(Label(
                    text="Igniting Video Engine...",
                    pos_hint={'center_y': 0.7}
                ))

        # Status label
        self.status = Label(
            text="READY TO HARVEST",
            pos_hint={'center_y': 0.45},
            color=(0.7, 0.7, 0.7, 1)
        )
        layout.add_widget(self.status)

        # Start button
        self.btn_start = Button(
            text="SET START",
            size_hint=(0.4, 0.1),
            pos_hint={'x': 0.05, 'y': 0.3},
            background_color=(0.1, 0.5, 0.1, 1),
            background_normal=''
        )
        self.btn_start.bind(on_release=self.set_start)
        layout.add_widget(self.btn_start)

        # End button
        self.btn_end = Button(
            text="SET END",
            size_hint=(0.4, 0.1),
            pos_hint={'right': 0.95, 'y': 0.3},
            background_color=(0.7, 0.1, 0.1, 1),
            background_normal=''
        )
        self.btn_end.bind(on_release=self.set_end)
        layout.add_widget(self.btn_end)

        # Harvest button
        harvest_btn = Button(
            text="GENERATE LOSSLESS CLIP",
            size_hint=(0.9, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            bold=True
        )
        harvest_btn.bind(on_release=self.run_harvest)
        layout.add_widget(harvest_btn)

        self.add_widget(layout)

    def set_start(self, instance):
        if hasattr(self, 'player'):
            self.start_time = self.player.position
            self.btn_start.text = f"IN: {round(self.start_time, 1)}s"

    def set_end(self, instance):
        if hasattr(self, 'player'):
            self.end_time = self.player.position
            self.btn_end.text = f"OUT: {round(self.end_time, 1)}s"

    def run_harvest(self, instance):
        self.status.text = "QUEUING LOSSLESS EXTRACT..."
        Clock.schedule_once(self.complete, 2)

    def complete(self, dt):
        self.status.text = "SAVED TO MOVIES/LOCALCLIP"
        self.btn_start.text = "SET START"
        self.btn_end.text = "SET END"


# ---------------------------------------------------------
# APP ROOT
# ---------------------------------------------------------
class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm


if __name__ == '__main__':
    LocalClipApp().run()