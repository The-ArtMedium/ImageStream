# main.py
import os, subprocess, threading, time
from urllib.parse import unquote
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.image import Image
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

def _base():
    return primary_external_storage_path() if platform == 'android' else os.path.expanduser("~")

# ───────────────────────────────────────────────
# MAIN SCREEN — select once, then stay in editor
# ───────────────────────────────────────────────
class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        layout.add_widget(Image(
            source='Splash-screen.png',
            allow_stretch=True, keep_ratio=True
        ))
        btn = Button(
            text="SELECT MASTER VIDEO",
            size_hint=(0.8, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.2},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='', color=(0, 0, 0, 1), bold=True
        )
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
            start_path = _base()
        else:
            start_path = os.path.expanduser("~")

        content = FloatLayout()
        self.fc = FileChooserListView(
            path=start_path,
            filters=['*.mp4', '*.mkv', '*.mov'],
            size_hint=(1, 0.85), pos_hint={'y': 0.15}
        )
        load_btn = Button(
            text="LOAD MOVIE",
            size_hint=(0.9, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='', color=(0, 0, 0, 1), bold=True
        )
        content.add_widget(self.fc)
        content.add_widget(load_btn)
        self.popup = Popup(
            title="Search Sanctuary",
            content=content, size_hint=(0.95, 0.9)
        )
        load_btn.bind(on_release=self.on_load)
        self.popup.open()

    def on_load(self, *args):
        if self.fc.selection:
            # FIX #7: unquote handles URI-encoded paths (spaces etc.)
            path = unquote(self.fc.selection[0].replace('file://', ''))
            self.popup.dismiss()
            self.manager.get_screen('editor').load_master(path)
            self.manager.current = 'editor'


# ───────────────────────────────────────────────
# EDITOR SCREEN — one-way door, clip many times
# ───────────────────────────────────────────────
class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.player = None
        self.position = 0.0
        self.duration = 0.0
        self.start_time = 0.0
        self.end_time = 0.0
        self._poll_event = None
        self._clip_count = 0
        self._ui_ready = False

    def load_master(self, path):
        """Called once from MainScreen. Stores path for deferred_load."""
        self.video_path = path
        self.start_time = 0.0
        self.end_time = 0.0
        self.position = 0.0
        self.duration = 0.0
        self._clip_count = 0

    def on_enter(self):
        # Only build UI once — subsequent clips don't rebuild
        if not self._ui_ready:
            self._build_ui()
        else:
            self._reset_markers()

        # FIX #4: close any existing player before opening new one
        self._close_player()
        self.status.text = "Loading master..."
        # 1.2s handshake prevents GPU crash on modern Android
        Clock.schedule_once(self._deferred_load, 1.2)

    def _deferred_load(self, dt):
        try:
            from ffpyplayer.player import MediaPlayer
            self.player = MediaPlayer(
                self.video_path,
                ff_opts={'paused': True, 'an': True, 'nodisp': True}
            )
            # FIX #1: store clock event so we can cancel it on leave
            self._poll_event = Clock.schedule_interval(self._poll, 0.3)
            # FIX #3: read duration after brief settle
            Clock.schedule_once(self._read_duration, 1.5)
            self.status.text = "Engine loaded — Ready"
        except Exception as e:
            self.status.text = f"Load failed: {e}"

    def _read_duration(self, dt):
        """Pull duration from player metadata and set progress max."""
        if self.player:
            meta = self.player.get_metadata()
            if meta and meta.get('duration'):
                self.duration = meta['duration']
                self.end_time = self.duration
                self.progress.max = self.duration
                fname = os.path.basename(self.video_path)
                self.status.text = f"Ready — {fname}"

    def _build_ui(self):
        self.clear_widgets()
        l = FloatLayout()

        # FIX #6: center_x added
        self.pos_label = Label(
            text="▶ 00:00.00", font_size='32sp', bold=True,
            pos_hint={'center_x': 0.5, 'center_y': 0.82}
        )
        l.add_widget(self.pos_label)

        self.dur_label = Label(
            text="", font_size='13sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.76}
        )
        l.add_widget(self.dur_label)

        self.progress = ProgressBar(
            max=100, size_hint=(0.9, 0.04),
            pos_hint={'center_x': 0.5, 'center_y': 0.70}
        )
        l.add_widget(self.progress)

        # Nudge buttons — navigate without scrubber
        for txt, val, xpos in [("-5s", -5, 0.1), ("-1s", -1, 0.35), ("+1s", 1, 0.6), ("+5s", 5, 0.85)]:
            b = Button(
                text=txt, size_hint=(0.2, 0.07),
                pos_hint={'center_x': xpos, 'center_y': 0.62},
                background_color=(0.25, 0.25, 0.25, 1)
            )
            b.bind(on_release=lambda inst, v=val: self._nudge(v))
            l.add_widget(b)

        # FIX #10: button text updates to confirm the set time
        self.in_btn = Button(
            text="SET IN", size_hint=(0.44, 0.1),
            pos_hint={'x': 0.04, 'center_y': 0.50},
            background_color=(0.1, 0.4, 0.1, 1), bold=True
        )
        self.out_btn = Button(
            text="SET OUT", size_hint=(0.44, 0.1),
            pos_hint={'right': 0.96, 'center_y': 0.50},
            background_color=(0.4, 0.1, 0.1, 1), bold=True
        )
        self.in_btn.bind(on_release=self._set_in)
        self.out_btn.bind(on_release=self._set_out)
        l.add_widget(self.in_btn)
        l.add_widget(self.out_btn)

        # SAVE — stays on screen after save, ready for next clip
        save_btn = Button(
            text="SAVE LOSSLESS CLIP",
            size_hint=(0.92, 0.11),
            pos_hint={'center_x': 0.5, 'center_y': 0.36},
            background_color=(0.96, 0.65, 0.14, 1),
            color=(0, 0, 0, 1), bold=True
        )
        save_btn.bind(on_release=self.save_clip)
        l.add_widget(save_btn)

        # Clip counter — shows how many clips saved from this master
        self.clip_label = Label(
            text="Clips saved: 0", font_size='13sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.27}
        )
        l.add_widget(self.clip_label)

        self.status = Label(
            text="Ready", font_size='13sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.20}
        )
        l.add_widget(self.status)

        # CLOSE MASTER — only when truly done with this file
        close_btn = Button(
            text="CLOSE MASTER / SELECT NEW",
            size_hint=(0.92, 0.09),
            pos_hint={'center_x': 0.5, 'center_y': 0.10},
            background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1)
        )
        close_btn.bind(on_release=self._close_master)
        l.add_widget(close_btn)

        self.add_widget(l)
        self._ui_ready = True

    def _nudge(self, delta):
        if self.player:
            self.position = max(0, min(self.duration, self.position + delta))
            # positional arg — avoids ffpyplayer keyword API uncertainty
            self.player.seek(self.position, False)

    def _set_in(self, *args):
        self.start_time = self.position
        self.in_btn.text = f"IN  {self._fmt(self.start_time)}"

    def _set_out(self, *args):
        self.end_time = self.position
        self.out_btn.text = f"OUT  {self._fmt(self.end_time)}"

    def _reset_markers(self):
        """After each save — reset IN/OUT ready for next clip, same master."""
        self.start_time = 0.0
        self.end_time = self.duration
        self.in_btn.text = "SET IN"
        self.out_btn.text = "SET OUT"

    def _poll(self, dt):
        if self.player:
            pts = self.player.get_pts()
            if pts and pts > 0:
                self.position = pts
                self.pos_label.text = f"▶ {self._fmt(pts)}"
                self.progress.value = min(pts, self.progress.max)
                if self.duration > 0:
                    self.dur_label.text = f"{self._fmt(pts)} / {self._fmt(self.duration)}"

    def save_clip(self, *args):
        # FIX #2: validate before doing anything
        if self.end_time <= self.start_time:
            self.status.text = "Set OUT point after IN point first"
            return
        dur = self.end_time - self.start_time
        if dur < 0.1:
            self.status.text = "Clip too short — adjust markers"
            return

        out_dir = os.path.join(_base(), "Movies", "LocalClip_Exports")
        os.makedirs(out_dir, exist_ok=True)

        # FIX #5: time.time() — unique, no session collision
        out_file = os.path.join(out_dir, f"clip_{int(time.time())}.mp4")

        self.status.text = "Cutting lossless..."

        def run():
            cmd = [
                "ffmpeg", "-y",
                "-ss", str(self.start_time),
                "-t", str(dur),
                "-i", self.video_path,
                "-c", "copy",
                out_file
            ]
            result = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
            if result.returncode == 0:
                self._clip_count += 1
                def on_done(dt):
                    self.status.text = f"Saved: {os.path.basename(out_file)}"
                    self.clip_label.text = f"Clips saved: {self._clip_count}"
                    # Vision: reset markers, stay in editor, same master
                    self._reset_markers()
                Clock.schedule_once(on_done, 0)
            else:
                err = result.stderr.decode('utf-8', errors='replace')[-100:]
                Clock.schedule_once(
                    lambda dt: setattr(self.status, 'text', f"Failed: {err}"), 0
                )

        threading.Thread(target=run, daemon=True).start()

    def _close_player(self):
        if self._poll_event:
            self._poll_event.cancel()
            self._poll_event = None
        if self.player:
            try:
                self.player.close_player()
            except Exception:
                pass
            self.player = None

    def _close_master(self, *args):
        """User is done with this master. Clean up and go back to picker."""
        self._close_player()
        self._ui_ready = False  # force UI rebuild for next master
        self.manager.current = 'main'

    def on_leave(self):
        # FIX #1: always cancel poll clock on leave
        self._close_player()

    def _fmt(self, secs):
        m, s = divmod(secs, 60)
        return f"{int(m):02d}:{s:05.2f}"


# ───────────────────────────────────────────────
class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
