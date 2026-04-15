import os, threading, subprocess
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
        
        # BRANDING: Matching your "Lossless. Offline. Sovereign." vision
        layout.add_widget(Label(
            text="[b]Local[color=f5a623]Clip[/color][/b]", 
            markup=True, font_size='48sp', 
            pos_hint={'center_x': 0.5, 'center_y': 0.7}
        ))
        layout.add_widget(Label(
            text="Lossless. Offline. Sovereign.", 
            font_size='16sp', 
            pos_hint={'center_x': 0.5, 'center_y': 0.63}, 
            color=(0.7, 0.7, 0.7, 1)
        ))
        
        btn = Button(
            text="SELECT MASTER FOOTAGE", 
            size_hint=(0.85, 0.12), 
            pos_hint={'center_x': 0.5, 'center_y': 0.4}, 
            background_color=(0.96, 0.65, 0.14, 1), 
            background_normal='', 
            color=(0, 0, 0, 1), 
            bold=True
        )
        btn.bind(on_release=self.open_picker)
        layout.add_widget(btn)
        self.add_widget(layout)

    def open_picker(self, *args):
        start_path = primary_external_storage_path() if platform == 'android' else os.path.expanduser("~")
        content = FloatLayout()
        
        # The selector window
        fc = FileChooserListView(
            path=start_path, 
            filters=['*.mp4', '*.mkv', '*.mov'], 
            size_hint=(1, 0.9), 
            pos_hint={'x': 0, 'y': 0.1}
        )
        content.add_widget(fc)
        
        popup = Popup(title="Select Video to Witness", content=content, size_hint=(0.95, 0.95))
        
        sel_btn = Button(
            text="OPEN VIDEO", 
            size_hint=(0.9, 0.08), 
            pos_hint={'center_x': 0.5, 'y': 0.01}, 
            background_color=(0.96, 0.65, 0.14, 1), 
            background_normal='', 
            color=(0, 0, 0, 1)
        )
        content.add_widget(sel_btn)

        def on_open(*args):
            if fc.selection:
                # REINFORCED HANDOFF: Converting path to a clean string
                selected_path = str(fc.selection[0])
                popup.dismiss()
                
                # Force the Editor Screen to receive the path
                editor = self.manager.get_screen('editor')
                editor.video_path = selected_path
                
                # Switch screens immediately
                self.manager.current = 'editor'
        
        sel_btn.bind(on_release=on_open)
        popup.open()

class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.player = None
        self.video_texture = None
        self.start_time = 0
        self.end_time = 0

    def on_enter(self):
        self.setup_ui()
        if self.video_path:
            # Wake up the FFmpeg engine
            from ffpyplayer.player import MediaPlayer
            self.player = MediaPlayer(self.video_path, ff_opts={'paused': True, 'an': True})
            Clock.schedule_interval(self._poll, 1.0/30.0)

    def setup_ui(self):
        self.clear_widgets()
        layout = FloatLayout()
        
        # PORTRAIT OPTIMIZED STACK (The "TV" on top)
        self.video_display = Image(
            size_hint=(1, 0.45), 
            pos_hint={'center_x': 0.5, 'top': 1}, 
            allow_stretch=True
        )
        layout.add_widget(self.video_display)

        # Timer and Progress
        self.pos_label = Label(
            text="▶ 00:00.00", 
            font_size='36sp', 
            pos_hint={'center_x': 0.5, 'center_y': 0.53}
        )
        layout.add_widget(self.pos_label)

        self.progress = ProgressBar(
            max=100, value=0, 
            size_hint=(0.9, 0.05), 
            pos_hint={'center_x': 0.5, 'center_y': 0.48}
        )
        layout.add_widget(self.progress)
        
        # Precision Nudge Buttons
        for text, delta, x in [("-5s", -5, 0.18), ("-1s", -1, 0.39), ("+1s", 1, 0.61), ("+5s", 5, 0.82)]:
            btn = Button(text=text, size_hint=(0.18, 0.07), pos_hint={'center_x': x, 'center_y': 0.4})
            btn.bind(on_release=lambda inst, d=delta: self.seek(d))
            layout.add_widget(btn)

        # Selection Buttons
        self.in_btn = Button(
            text="SET IN", 
            size_hint=(0.45, 0.08), 
            pos_hint={'x': 0.03, 'center_y': 0.3}, 
            background_color=(0.2, 0.8, 0.2, 1)
        )
        self.in_btn.bind(on_release=self.set_in)
        layout.add_widget(self.in_btn)

        self.out_btn = Button(
            text="SET OUT", 
            size_hint=(0.45, 0.08), 
            pos_hint={'right': 0.97, 'center_y': 0.3}, 
            background_color=(0.8, 0.2, 0.2, 1)
        )
        self.out_btn.bind(on_release=self.set_out)
        layout.add_widget(self.out_btn)

        # The Sovereign Save
        save_btn = Button(
            text="SAVE LOSSLESS CLIP", 
            size_hint=(0.9, 0.1), 
            pos_hint={'center_x': 0.5, 'center_y': 0.15}, 
            background_color=(0.96, 0.65, 0.14, 1), 
            color=(0,0,0,1), 
            bold=True
        )
        save_btn.bind(on_release=self.save_clip)
        layout.add_widget(save_btn)

        self.status = Label(text="Ready", size_hint=(1, 0.05), pos_hint={'center_x': 0.5, 'y': 0.02})
        layout.add_widget(self.status)

        self.add_widget(layout)

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
            new_time = max(0, self.player.get_pts() + delta)
            self.player.seek(new_time, relative=False)

    def set_in(self, *args):
        self.start_time = self.player.get_pts()
        self.in_btn.text = f"IN: {int(self.start_time)}s"

    def set_out(self, *args):
        self.end_time = self.player.get_pts()
        self.out_btn.text = f"OUT: {int(self.end_time)}s"

    def save_clip(self, *args):
        # Save to a dedicated LocalClip folder
        root = primary_external_storage_path() if platform == 'android' else os.path.expanduser("~")
        folder = os.path.join(root, "LocalClip")
        if not os.path.exists(folder):
            os.makedirs(folder)
            
        out_path = os.path.join(folder, f"witness_trim_{int(self.start_time)}.mp4")
        self.status.text = "Trimming Sovereignty... Please Wait"
        
        def run_ffmpeg():
            duration = max(0.1, self.end_time - self.start_time)
            cmd = ["ffmpeg", "-y", "-ss", str(self.start_time), "-t", str(duration), "-i", self.video_path, "-c", "copy", out_path]
            subprocess.run(cmd, capture_output=True)
            Clock.schedule_once(lambda dt: setattr(self.status, 'text', f"Saved to LocalClip/ folder"))
        
        threading.Thread(target=run_ffmpeg).start()

    def on_leave(self):
        if self.player:
            self.player.close_player()

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
