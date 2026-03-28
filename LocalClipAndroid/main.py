from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.boxlayout import BoxLayout
from kivy.utils import platform

class DiagnosticApp(App):
    def build(self):
        self.lbl = Label(text="DIAGNOSTIC MODE: ACTIVE")
        btn = Button(text="TEST STORAGE HANDSHAKE", size_hint=(1, .2))
        btn.bind(on_release=self.check_access)
        
        layout = BoxLayout(orientation='vertical')
        layout.add_widget(self.lbl)
        layout.add_widget(btn)
        return layout

    def check_access(self, instance):
        if platform == 'android':
            try:
                from android.permissions import request_permissions, Permission
                request_permissions([Permission.READ_MEDIA_VIDEO, Permission.READ_EXTERNAL_STORAGE])
                self.lbl.text = "PERMISSION REQUEST SENT"
            except Exception as e:
                self.lbl.text = f"CRASH PREVENTED: {str(e)}"
        else:
            self.lbl.text = "NOT ON ANDROID"

if __name__ == '__main__':
    DiagnosticApp().run()
