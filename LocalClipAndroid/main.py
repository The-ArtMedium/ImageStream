import os
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.button import Button
from kivy.uix.label import Label

os.environ["SDL_AUDIODRIVER"] = "android"

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
            color=(0, 0, 0, 1), bold=True
        )
        btn.bind(on_release=lambda x: print("Button pressed"))
        layout.add_widget(btn)
        self.add_widget(layout)

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()