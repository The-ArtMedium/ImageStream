import os, subprocess, threading, time, urllib.parse
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.popup import Popup
from kivy.uix.video import Video
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.clock import Clock
from kivy.utils import platform

# Global Translation Dictionary
LOCALES = {
    'en': {'select': "SELECT MASTER", 'load': "LOAD", 'in': "SET IN", 'out': "SET OUT", 'save': "SAVE", 'ready': "Ready", 'saving': "Saving...", 'close': "CLOSE"},
    'es': {'select': "SELECCIONAR", 'load': "CARGAR", 'in': "INICIO", 'out': "FINAL", 'save': "GUARDAR", 'ready': "Listo", 'saving': "Guardando...", 'close': "CERRAR"}
}
L = LOCALES.get('en')

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        btn = Button(text=L['select'], size_hint=(0.8, 0.12), pos_hint={'center_x': 0.5, 'center_y': 0.25},
                     background_color=(0.96, 0.65, 0.14, 1), bold=True)
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
        self.fc = FileChooserListView(path=start_path, filters=['*.mp4', '*.mov'], size_hint=(1, 0.85), pos_hint={'y': 0.15})
        load_btn = Button(text=L['load'], size_hint=(0.9, 0.1), pos_hint={'center_x': 0.5, 'y': 0.02}, background_color=(0.96, 0.65, 0.14, 1))
        content.add_widget(self.fc)
        content.add_widget(load_btn)
        self.popup = Popup(title="Search", content=content, size_hint=(0.95, 0.9))
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
        self.player = None
        self.start_time = 0.0
        self.end_time = 0.0

    def on_enter(self):
        self.setup_ui()

    def setup_ui(self):
        self.clear_widgets()
        l = FloatLayout()
        
        # Core Video Engine
        self.player = Video(source=self.video_path, state='play', options={'allow_stretch': True})
        self.player.size_hint = (1, 0.5)
        self.player.pos_hint = {'center_x': 0.5, 'top': 1}
        l.add_widget(self.player)

        self.pos_label = Label(text="00:00", font_size='30sp', pos_hint={'center_y': 0.45})
        l.add_widget(self.pos_label)
        
        self.in_btn = Button(text=L['in'], size_hint=(0.4, 0.1), pos_hint={'x': 0.05, 'y': 0.3}, background_color=(0.1, 0.3, 0.1, 1))
        self.out_btn = Button(text=L['out'], size_hint=(0.4, 0.1), pos_hint={'right': 0.95, 'y': 0.3}, background_color=(0.3, 0.1, 0.1, 1))
        self.in_btn.bind(on_release=lambda x: setattr(self, 'start_time', self.player.position))
        self.out_btn.bind(on_release=lambda x: setattr(self, 'end_time', self.player.position))
        l.add_widget(self.in_btn)
        l.add_widget(self.out_btn)

        save_btn = Button(text=L['save'], size_hint=(0.9, 0.1), pos_hint={'center_x': 0.5, 'y': 0.15}, background_color=(0.4, 0.3, 0.1, 1))
        save_btn.bind(on_release=self.save_clip)
        l.add_widget(save_btn)

        self.status = Label(text=L['ready'], pos_hint={'y': 0.05})
        l.add_widget(self.status)
        self.add_widget(l)
        Clock.schedule_interval(self._update_label, 0.5)

    def _update_label(self, dt):
        if self.player:
            self.pos_label.text = f"{int(self.player.position // 60):02d}:{int(self.player.position % 60):02d}"

    def save_clip(self, *args):
        base = primary_external_storage_path() if platform == 'android' else os.path.expanduser("~")
        out_file = os.path.join(base, "Movies", f"clip_{int(time.time())}.mp4")
        self.status.text = L['saving']
        def run():
            dur = max(1, self.end_time - self.start_time)
            cmd = ["ffmpeg", "-y", "-ss", str(self.start_time), "-t", str(dur), "-i", self.video_path, "-c", "copy", out_file]
            subprocess.run(cmd)
            Clock.schedule_once(lambda d: setattr(self.status, 'text', f"Saved to Movies"))
        threading.Thread(target=run).start()

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
