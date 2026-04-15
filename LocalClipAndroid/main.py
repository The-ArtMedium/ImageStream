import os
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

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

# ───────────────────────────────────────────────
# MAIN SCREEN
# ───────────────────────────────────────────────
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        layout.add_widget(Label(
            text="[b]Local[color=f5a623]Clip[/color][/b]",
            markup=True, font_size='48sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        ))
        btn = Button(
            text="SELECT VIDEO",
            size_hint=(0.8, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='', color=(0, 0, 0, 1), bold=True
        )
        btn.bind(on_release=self.open_picker)
        layout.add_widget(btn)
        self.add_widget(layout)

    def open_picker(self, *args):
        # FIX: Added MANAGE_EXTERNAL_STORAGE for Android 13+ support
        if platform == 'android':
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
        fc = FileChooserListView(
            path=start_path,
            filters=['*.mp4', '*.mkv', '*.mov', '*.avi'],
            size_hint=(1, 0.85), pos_hint={'x': 0, 'y': 0.15}
        )
        content.add_widget(fc)

        btn_layout = FloatLayout(size_hint=(1, 0.15), pos_hint={'x':0, 'y':0})
        sel_btn = Button(text="OPEN", size_hint=(0.4, 0.7), pos_hint={'x': 0.05, 'y': 0.15},
                         background_color=(0.96, 0.65, 0.14, 1), background_normal='', color=(0, 0, 0, 1))
        can_btn = Button(text="CANCEL", size_hint=(0.4, 0.7), pos_hint={'right': 0.95, 'y': 0.15})
        
        btn_layout.add_widget(sel_btn)
        btn_layout.add_widget(can_btn)
        content.add_widget(btn_layout)

        popup = Popup(title="Select Video", content=content, size_hint=(0.95, 0.9))
        
        def on_open(*args):
            if fc.selection:
                popup.dismiss()
                # Ensure the path is clean for ffpyplayer
                clean_path = fc.selection[0].replace('file://', '')
                self.manager.get_screen('editor').video_path = clean_path
                self.manager.current = 'editor'

        sel_btn.bind(on_release=on_open)
        can_btn.bind(on_release=popup.dismiss)
        popup.open()

# ───────────────────────────────────────────────
# EDITOR SCREEN
# ───────────────────────────────────────────────
class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.duration = 0.0
        self.position = 0.0
        self.start_time = 0.0
        self.end_time = 0.0
        self.player = None
        self._tick = None
        self._meta_clock = None

    def on_enter(self):
        self.setup_ui()
        try:
            from ffpyplayer.player import MediaPlayer
            # Fix: Added 'an': True (no audio) to prevent engine crash on some files
            self.player = MediaPlayer(self.video_path, ff_opts={'paused': True, 'an': True})
            self._meta_clock = Clock.schedule_interval(self._check_metadata, 0.5)
        except Exception as e:
            self.status.text = f"Load Error: {e}"

        self._tick = Clock.schedule_interval(self._poll, 0.3)

    def setup_ui(self):
        self.clear_widgets()
        layout = FloatLayout()

        self.pos_label = Label(text="▶ 00:00.00", font_size='32sp', pos_hint={'center_x': 0.5, 'center_y': 0.8})
        layout.add_widget(self.pos_label)

        self.dur_label = Label(text="Loading...", font_size='14sp', pos_hint={'center_x': 0.5, 'center_y': 0.74})
        layout.add_widget(self.dur_label)

        self.progress = ProgressBar(max=100, value=0, size_hint=(0.9, 0.05), pos_hint={'center_x': 0.5, 'center_y': 0.68})
        layout.add_widget(self.progress)

        for text, delta, x_pos in [("-5s", -5, 0.1), ("-1s", -1, 0.35), ("+1s", 1, 0.6), ("+5s", 5, 0.85)]:
            btn = Button(text=text, size_hint=(0.2, 0.08), pos_hint={'center_x': x_pos, 'center_y': 0.58})
            btn.bind(on_release=lambda inst, d=delta: self.seek(d))
            layout.add_widget(btn)

        self.in_btn = Button(text="SET IN", size_hint=(0.4, 0.1), pos_hint={'x': 0.05, 'center_y': 0.45}, background_color=(0.2, 0.8, 0.2, 1))
        self.in_btn.bind(on_release=self.set_in)
        layout.add_widget(self.in_btn)

        self.out_btn = Button(text="SET OUT", size_hint=(0.4, 0.1), pos_hint={'right': 0.95, 'center_y': 0.45}, background_color=(0.8, 0.2, 0.2, 1))
        self.out_btn.bind(on_release=self.set_out)
        layout.add_widget(self.out_btn)

        self.status = Label(text="Ready", size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'y': 0.05})
        layout.add_widget(self.status)

        save_btn = Button(text="SAVE CLIP", size_hint=(0.9, 0.12), pos_hint={'center_x': 0.5, 'center_y': 0.2},
                          background_color=(0.96, 0.65, 0.14, 1), color=(0,0,0,1), bold=True)
        save_btn.bind(on_release=self.save_clip)
        layout.add_widget(save_btn)

        back_btn = Button(text="← BACK", size_hint=(0.2, 0.07), pos_hint={'x': 0.02, 'top': 0.98})
        back_btn.bind(on_release=lambda *a: setattr(self.manager, 'current', 'main'))
        layout.add_widget(back_btn)

        self.add_widget(layout)

    def _check_metadata(self, dt):
        if self.player:
            meta = self.player.get_metadata()
            if meta and meta.get('duration'):
                self.duration = meta['duration']
                self.end_time = self.duration
                self.dur_label.text = f"Duration: {self._fmt(self.duration)}"
                self.progress.max = self.duration
                return False
        return True

    def _poll(self, dt):
        if self.player:
            pts = self.player.get_pts()
            if pts:
                self.position = pts
                self.pos_label.text = f"▶ {self._fmt(pts)}"
                self.progress.value = pts

    def seek(self, delta):
        if self.duration > 0:
            self.position = max(0, min(self.duration, self.position + delta))
            if self.player:
                self.player.seek(self.position, relative=False)

    def set_in(self, *args):
        self.start_time = self.position
        self.in_btn.text = f"IN: {self._fmt(self.start_time)}"

    def set_out(self, *args):
        self.end_time = self.position
        self.out_btn.text = f"OUT: {self._fmt(self.end_time)}"

    def save_clip(self, *args):
        if self.end_time <= self.start_time:
            self.status.text = "Error: End must be after Start"
            return
        
        folder = os.path.join(primary_external_storage_path() if platform == 'android' else os.path.expanduser("~"), "LocalClip")
        os.makedirs(folder, exist_ok=True)
        out_path = os.path.join(folder, f"clip_{int(self.start_time)}.mp4")
        self.status.text = "Processing..."
        
        def run_ffmpeg():
            cmd = ["ffmpeg", "-y", "-ss", str(self.start_time), "-t", str(self.end_time - self.start_time),
                   "-i", self.video_path, "-c", "copy", out_path]
            try:
                proc = subprocess.run(cmd, capture_output=True, text=True)
                Clock.schedule_once(lambda dt: self._set_status("Success" if proc.returncode == 0 else "FFmpeg Error"))
            except Exception as e:
                Clock.schedule_once(lambda dt: self._set_status(f"Error: {e}"))

        threading.Thread(target=run_ffmpeg).start()

    def _set_status(self, text):
        self.status.text = text

    def on_leave(self):
        if self._tick: self._tick.cancel()
        if self._meta_clock: self._meta_clock.cancel()
        if self.player:
            self.player.close_player()
            self.player = None

    def _fmt(self, secs):
        m, s = divmod(secs, 60)
        return f"{int(m):02d}:{s:05.2f}"

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
