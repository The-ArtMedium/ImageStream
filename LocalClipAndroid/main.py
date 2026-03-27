from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.utils import platform

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        self.add_widget(Label(
            text="[b]Local[color=f5a623]Clip[/color][/b]",
            markup=True, font_size='42sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.75}
        ))
        btn = Button(
            text="SELECT SOURCE VIDEO",
            size_hint=(0.8, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.4},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            font_size='20sp',
            bold=True
        )
        btn.bind(on_release=self.go_to_editor)
        self.add_widget(btn)

    def go_to_editor(self, instance):
        self.manager.current = 'editor'

class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        
        # Action Area
        self.add_widget(Label(text="[ HARVEST NODE ]", pos_hint={'center_y': 0.6}, color=(0.4, 0.4, 0.4, 1)))

        # Trimming Tools
        self.add_widget(Button(text="SET START", size_hint=(0.4, 0.1), pos_hint={'x': 0.05, 'y': 0.25}, background_color=(0.2, 0.5, 0.2, 1)))
        self.add_widget(Button(text="SET END", size_hint=(0.4, 0.1), pos_hint={'right': 0.95, 'y': 0.25}, background_color=(0.7, 0.2, 0.2, 1)))
        
        # The Final Clip Action
        harvest_btn = Button(
            text="GENERATE LOSSLESS CLIP",
            size_hint=(0.9, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            background_color=(0.96, 0.65, 0.14, 1),
            color=(0, 0, 0, 1),
            bold=True
        )
        self.add_widget(harvest_btn)

class LocalClipApp(App):
    def build(self):
        if platform == 'android':
            from android.permissions import request_permissions, Permission
            # We are using only the strictly necessary permissions to stop the "Harmful" block
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE])
        
        from kivy.core.window import Window
        Window.clearcolor = (0.02, 0.02, 0.02, 1)
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()
