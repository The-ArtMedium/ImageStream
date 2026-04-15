import os
import threading
import subprocess
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.image import Image
from kivy.graphics.texture import Texture
from kivy.clock import Clock
from kivy.utils import platform

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        layout.add_widget(Label(text="[b]Local[color=f5a623]Clip[/color][/b]", markup=True, font_size='48sp', pos_hint={'center_x': 0.5, 'center_y': 0.75}))
        btn = Button(text="SELECT VIDEO", size_hint=(0.8, 0.12), pos_hint={'center_x': 0.5, 'center_y': 0.4}, background_color=(0.96, 0.65, 0.14, 1), background_normal='', color=(0, 0, 0, 1), bold=True)
        btn.bind(on_release=self.open_picker)
        layout.add_widget(btn)
        self.add_widget(layout)

    def open_picker(self, *args):
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, "android.permission.READ_MEDIA_VIDEO"])
            start_path = primary_external_storage_path()
        else:
            start_path = os.path.expanduser("~")

        content = FloatLayout()
        fc = FileChooserListView(path=start_path, filters=['*'], size_hint=(1, 0.85), pos_hint={'x': 0, 'y': 0.15})
        content.add_widget(fc)
        btn_layout = FloatLayout(size_hint=(1, 0.15), pos_hint={'x': 0, 'y': 0})
        sel_btn = Button(text="OPEN", size_hint=(0.4, 0.7), pos_hint={'x': 0.05, 'y': 0.15}, background_color=(0.96, 0.65, 0.14, 1), background_normal='', color=(0, 0, 0, 1))
        can_btn = Button(text="CANCEL", size_hint=(0.4, 0.7), pos_hint={'right': 0.95, 'y': 0.15})
        btn_layout.add_widget(sel_btn)
        btn_layout.add_widget(can_btn)
        content.add_widget(btn_layout)
        popup = Popup(title="Select Video", content=content, size_hint=(0.95, 0.9))
        
        def on_open(*args):
            if fc.selection:
                popup.dismiss()
                self.manager.get_screen('editor').video_path = fc.selection[0]
                self.manager.current = 'editor'
        sel_btn.bind(on_release=on_open)
        can_btn.bind(on_release=popup.dismiss)
        popup.open()

class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.player = None
        self.video_texture = None
        self._tick = None
        self._meta_tick = None

    def on_enter(self):
        self.setup_ui()
        if self.video_path:
            try:
                from ffpyplayer.player import MediaPlayer
                self.player = MediaPlayer(self.video_path, ff_opts={'paused': True, 'an': True})
                self._meta_tick = Clock.schedule_interval(self._check_metadata, 0.5)
            except Exception as e:
                self.status.text = f"Error: {e}"
        self._tick = Clock.schedule_interval(self._poll, 1.0/30.0)

    def setup_ui(self):
        self.clear_widgets()
        layout = FloatLayout()
        self.video_display = Image(size_hint=(0.9, 0.45), pos_hint={'center_x': 0.5, 'center_y': 0.7}, allow_stretch=True)
        layout.add_widget(self.video_display)
        self.pos_label = Label(text="▶ 00:00.00", font_size='24sp', pos_hint={'center_x': 0.5, 'center_y': 0.45})
        layout.add_widget(self.pos_label)
        self.progress = ProgressBar(max=100, value=0, size_hint=(0.9, 0.05), pos_hint={'center_x': 0.5, 'center_y': 0.42})
        layout.add_widget(self.progress)
        
        # Controls shifted down to accommodate video
        for text, delta, x in [("-5s", -5, 0.15), ("-1s", -1, 0.38), ("+1s", 1, 0.62), ("+5s", 5, 0.85)]:
            btn = Button(text=text, size_hint=(0.18, 0.08), pos_hint={'center_x': x, 'center_y': 0.34})
            btn.bind(on_release=lambda inst, d=delta: self.seek(d))
            layout.add_widget(btn)

        self.in_btn = Button(text="SET IN", size_hint=(0.4, 0.1), pos_hint={'x': 0.05, 'center_y': 0.22}, background_color=(0.2, 0.8, 0.2, 1))
        self.in_btn.bind(on_release=self.set_in)
        layout.add_widget(self.in_btn)
        self.out_btn = Button(text="SET OUT", size_hint=(0.4, 0.1), pos_hint={'right': 0.95, 'center_y': 0.22}, background_color=(0.8, 0.2, 0.2, 1))
        self.out_btn.bind(on_release=self.set_out)
        layout.add_widget(self.out_btn)

        self.status = Label(text="Ready", size_hint=(1, 0.1), pos_hint={'center_x': 0.5, 'y': 0.02})
        layout.add_widget(self.status)
        save_btn = Button(text="SAVE CLIP", size_hint=(0.9, 0.1), pos_hint={'center_x': 0.5, 'center_y': 0.1}, background_color=(0.96, 0.65, 0.14, 1), color=(0,0,0,1), bold=True)
        save_btn.bind(on_release=self.save_clip)
        layout.add_widget(save_btn)
        self.add_widget(layout)

    def _check_metadata(self, dt):
        if self.player:
            meta = self.player.get_metadata()
            if meta and meta.get('duration'):
                self.duration = meta['duration']
                self.progress.max = self.duration
                return False
        return True

    def _poll(self, dt):
        if self.player:
            pts = self.player.get_pts()
            if pts:
                self.pos_label.text = f"▶ {int(pts//60):02d}:{pts%60:05.2f}"
                self.progress.value = pts
            frame, val = self.player.get_frame()
            if val != 'eof' and frame is not None:
                img, t = frame
                w, h = img.get_size()
                if not self.video_texture or self.video_texture.size != (w, h):
                    self.video_texture = Texture.create(size=(w, h), colorfmt='rgb')
                    self.video_texture.flip_vertical()
                self.video_texture.blit_buffer(img.to_bytearray(), colorfmt='rgb', bufferfmt='ubyte')
                self.video_display.texture = self.video_texture

    def seek(self, delta):
        if self.player:
            new_pos = max(0, self.player.get_pts() + delta)
            self.player.seek(new_pos, relative=False)

    def set_in(self, *args):
        self.start_time = self.player.get_pts()
        self.in_btn.text = f"IN: {int(self.start_time):02d}s"

    def set_out(self, *args):
        self.end_time = self.player.get_pts()
        self.out_btn.text = f"OUT: {int(self.end_time):02d}s"

    def save_clip(self, *args):
        folder = os.path.join(primary_external_storage_path() if platform == 'android' else os.path.expanduser("~"), "LocalClip")
        os.makedirs(folder, exist_ok=True)
        out_path = os.path.join(folder, f"trim_{int(self.start_time)}.mp4")
        self.status.text = "Trimming... Please Wait"
        
        def run_ffmpeg():
            cmd = ["ffmpeg", "-y", "-ss", str(self.start_time), "-t", str(self.end_time - self.start_time), "-i", self.video_path, "-c", "copy", out_path]
            try:
                subprocess.run(cmd, capture_output=True)
                Clock.schedule_once(lambda dt: setattr(self.status, 'text', f"Saved: {os.path.basename(out_path)}"))
            except Exception as e:
                Clock.schedule_once(lambda dt: setattr(self.status, 'text', f"Error: {e}"))
        threading.Thread(target=run_ffmpeg).start()

    def on_leave(self):
        if self._tick: self._tick.cancel()
        if self._meta_tick: self._meta_tick.cancel()
        if self.player: self.player.close_player()

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
