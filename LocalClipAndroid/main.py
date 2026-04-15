import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.lang import Builder
from kivy.properties import StringProperty
from kivy.clock import Clock

# The "Sovereign" UI Design
Builder.load_string('''
<Manager>:
    MenuScreen:
        name: 'menu'
    EditorScreen:
        name: 'editor'

<MenuScreen>:
    BoxLayout:
        orientation: 'vertical'
        canvas.before:
            Color:
                rgba: 0, 0, 0, 1
            Rectangle:
                pos: self.pos
                size: self.size
        
        Label:
            text: '[b]LocalClip[/b]'
            markup: True
            font_size: '40sp'
            size_hint_y: 0.3
            color: 1, 1, 1, 1

        Button:
            text: 'SELECT MASTER FOOTAGE'
            size_hint: (0.8, 0.2)
            pos_hint: {'center_x': 0.5}
            background_color: 1, 0.7, 0, 1
            on_release: app.open_file_chooser()

<EditorScreen>:
    video_path: ""
    BoxLayout:
        orientation: 'vertical'
        
        VideoPlayer:
            id: player
            source: root.video_path
            state: 'play'
            options: {'eos': 'loop'}
        
        BoxLayout:
            size_hint_y: 0.2
            Button:
                text: 'BACK'
                on_release: app.root.current = 'menu'
''')

class MenuScreen(Screen):
    pass

class EditorScreen(Screen):
    video_path = StringProperty("")

    def on_video_path(self, instance, value):
        # This triggers the moment the path is handed over
        if value:
            self.ids.player.source = value
            self.ids.player.state = 'play'

class Manager(ScreenManager):
    pass

class LocalClipApp(App):
    def build(self):
        return Manager()

    def open_file_chooser(self):
        # Note: In a full implementation, you'd use a FileChooser icon or Plyer.
        # For now, we assume your selection logic is calling 'load_video'
        from plyer import filechooser
        filechooser.open_file(on_selection=self.load_video)

    def load_video(self, selection):
        if not selection:
            return

        try:
            # 1. Capture the raw selection from the Android node
            raw_path = selection[0]
            
            # 2. Path Cleaning: Remove Android's 'file://' prefix if present
            if raw_path.startswith('file://'):
                video_path = raw_path[7:]
            else:
                video_path = os.path.abspath(raw_path)
            
            # 3. The "Witness" Check: Does the file actually exist at this path?
            if os.path.exists(video_path):
                print(f"Path Verified: {video_path}")
                
                # Hand the path to the Editor and switch screens
                editor = self.root.get_screen('editor')
                editor.video_path = video_path
                self.root.current = 'editor'
            else:
                print(f"Sovereign Error: File not found at {video_path}")
                
        except Exception as e:
            # This prevents the "Shut Off". It will print the error to the log instead of crashing.
            print(f"Engine Failure: {str(e)}")

if __name__ == '__main__':
    LocalClipApp().run()
