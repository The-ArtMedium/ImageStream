from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.videoplayer import VideoPlayer
from kivy.clock import Clock
from kivy.utils import platform

# Android permissions
if platform == 'android':
    from android.permissions import request_permissions, Permission

# --------------------- MAIN SCREEN ---------------------
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()

        self.title_label = Label(
            text="[b]Local[color=f5a623]Clip[/color][/b]",
            markup=True,
            font_size='48sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        )
        layout.add_widget(self.title_label)

        self.select_btn = Button(
            text="SELECT MASTER FOOTAGE",
            size_hint=(0.8,0.12),
            pos_hint={'center_x':0.5,'center_y':0.4},
            background_color=(0.96,0.65,0.14,1),
            background_normal='',
            color=(0,0,0,1),
            bold=True
        )
        self.select_btn.bind(on_release=self.open_gallery)
        layout.add_widget(self.select_btn)

        self.add_widget(layout)

    def open_gallery(self, instance):
        if platform == 'android':
            request_permissions([
                Permission.READ_MEDIA_VIDEO,
                Permission.READ_MEDIA_IMAGES,
                Permission.READ_MEDIA_AUDIO
            ])

        content = FloatLayout()
        start_path = "/storage/emulated/0/" if platform == 'android' else os.path.expanduser("~")
        self.fc = FileChooserListView(
            path=start_path,
            filters=['*.mp4','*.mkv','*.mov','*.avi','*.webm','*.m4v'],
            size_hint=(1,0.85),
            pos_hint={'x':0,'y':0.15}
        )
        content.add_widget(self.fc)

        select_btn = Button(
            text="SELECT",
            size_hint=(0.45,0.1),
            pos_hint={'x':0.05,'y':0.02},
            background_color=(0.96,0.65,0.14,1),
            background_normal='',
            color=(0,0,0,1),
            bold=True
        )
        cancel_btn = Button(
            text="CANCEL",
            size_hint=(0.45,0.1),
            pos_hint={'right':0.95,'y':0.02},
            background_color=(0.3,0.3,0.3,1),
            background_normal=''
        )
        content.add_widget(select_btn)
        content.add_widget(cancel_btn)

        popup = Popup(
            title="Select Video",
            content=content,
            size_hint=(0.95,0.9)
        )
        cancel_btn.bind(on_release=popup.dismiss)

        def on_select(*args):
            if self.fc.selection:
                popup.dismiss()
                path = self.fc.selection[0]
                # Pass video to editor
                self.manager.get_screen('editor').load_video(path)
                self.manager.current = 'editor'

        select_btn.bind(on_release=on_select)
        self.fc.bind(on_submit=lambda *args: on_select())
        popup.open()


# --------------------- EDITOR SCREEN ---------------------
class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.start_time = 0
        self.end_time = 0
        self.clips = []

    def load_video(self, path):
        self.video_path = path
        self.on_enter()

    def on_enter(self):
        self.clear_widgets()
        layout = FloatLayout()

        # Video Player
        if self.video_path:
            try:
                self.player = VideoPlayer(
                    source=self.video_path,
                    state='pause',
                    options={'allow_stretch': True},
                    size_hint=(1,0.5),
                    pos_hint={'center_x':0.5,'top':1}
                )
                layout.add_widget(self.player)
            except Exception:
                layout.add_widget(Label(text="Video engine loading...", pos_hint={'center_y':0.7}))

        # Status label
        self.status = Label(
            text="READY TO CREATE CLIPS",
            pos_hint={'center_y':0.45},
            color=(0.7,0.7,0.7,1)
        )
        layout.add_widget(self.status)

        # Start/End buttons
        self.btn_start = Button(text="SET START", size_hint=(0.4,0.1), pos_hint={'x':0.05,'y':0.3},
                                background_color=(0.1,0.5,0.1,1), background_normal='')
        self.btn_start.bind(on_release=self.set_start)
        layout.add_widget(self.btn_start)

        self.btn_end = Button(text="SET END", size_hint=(0.4,0.1), pos_hint={'right':0.95,'y':0.3},
                              background_color=(0.7,0.1,0.1,1), background_normal='')
        self.btn_end.bind(on_release=self.set_end)
        layout.add_widget(self.btn_end)

        # Add Clip button
        add_btn = Button(text