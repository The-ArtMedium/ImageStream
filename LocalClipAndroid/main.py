import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform
from kivy.clock import Clock

# --- Android Handshake ---
if platform == 'android':
    from android.permissions import request_permissions, Permission
    from plyer import filechooser

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        # Branding: High-Contrast for Field Use
        self.add_widget(Label(
            text="[b]Local[color=f5a623]Clip[/color][/b]",
            markup=True, font_size='48sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        ))
        
        self.add_widget(Label(
            text="LOSSLESS FIELD UTILITY",
            font_size='14sp', color=(0.5, 0.5, 0.5, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.68}
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
        self.add_widget(btn)

    def open_gallery(self, instance):
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
            filechooser.open_file(on_selection=self.handle_selection)
        else:
            # Desktop fallback for testing
            self.manager.current = 'editor'

    def handle_selection(self, selection):
        if selection:
            # Pass the file path to the Editor Node
            self.manager.get_screen('editor').video_path = selection[0]
            self.manager.current = 'editor'

class EditorScreen(Screen):
    video_path = ""
    start_time = 0
    end_time = 0

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.layout = FloatLayout()
        
        # Status Display
        self.status_label = Label(
            text="READY FOR HARVEST", 
            pos_hint={'center_y': 0.85},
            color=(0.5, 0.5, 0.5, 1)
        )
        self.layout.add_widget(self.status_label)

        # SET START Button (Green Node)
        self.btn_start = Button(
            text="SET START",
            size_hint=(0.4, 0.12),
            pos_hint={'x': 0.05, 'y': 0.35},
            background_color=(0.1, 0.6, 0.1, 1),
            background_normal=''
        )
        self.btn_start.bind(on_release=self.set_start)
        self.layout.add_widget(self.btn_start)

        # SET END Button (Red Node)
        self.btn_end = Button(
            text="SET END",
            size_hint=(0.4, 0.12),
            pos_hint={'right': 0.95, 'y': 0.35},
            background_color=(0.8, 0.1, 0.1, 1),
            background_normal=''
        )
        self.btn_end.bind(on_release=self.set_end)
        self.layout.add_widget(self.btn_end)

        # THE HARVEST ACTION (Instant Lossless Copy)
        self.harvest_btn = Button(
            text="GENERATE LOSSLESS CLIP",
            size_hint=(0.9, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.15},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            bold=True
        )
        self.harvest_btn.bind(on_release=self.trigger_harvest)
        self.layout.add_widget(self.harvest_btn)
        
        self.add_widget(self.layout)

    def set_start(self, instance):
        # In the next phase, we'll pull the real timestamp from the player
        self.start_time = 10 
        self.btn_start.text = f"START: {self.start_time}s"
        self.status_label.text = "START MARKED"

    def set_end(self, instance):
        self.end_time = 15
        self.btn_end.text = f"END: {self.end_time}s"
        self.status_label.text = "END MARKED"

    def trigger_harvest(self, instance):
        self.status_label.text = "HARVESTING... (NO RE-ENCODING)"
        # This is where the FFmpeg 'copy' command will fire
        print(f"COMMAND: ffmpeg -ss {self.start_time} -to {self.end_time} -i {self.video_path} -c copy output.mp4")
        Clock.schedule_once(self.finish_harvest, 1)

    def finish_harvest(self, dt):
        self.status_label.text = "SUCCESS: CLIP SAVED TO MOVIES"
        # Reset buttons for the NEXT harvest from the same video
        self.btn_start.text = "SET START"
        self.btn_end.text = "SET END"

class LocalClipApp(App):
    def build(self):
        from kivy.core.window import Window
        Window.clearcolor = (0.02, 0.02, 0.02, 1)
        
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
