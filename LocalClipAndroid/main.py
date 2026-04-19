# main.py
import os, subprocess, threading, time
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

# Global Translation Dictionary
LOCALES = {
    'en': {'select': "SELECT MASTER FOOTAGE", 'load': "LOAD MOVIE", 'in': "SET IN", 'out': "SET OUT", 'save': "SAVE LOSSLESS CLIP", 'ready': "Ready", 'saving': "Saving...", 'close': "CLOSE MASTER", 'exit': "EXIT APP", 'err_time': "Check IN/OUT"},
    'es': {'select': "SELECCIONAR MAESTRO", 'load': "CARGAR PELÍCULA", 'in': "MARCAR INICIO", 'out': "MARCAR FINAL", 'save': "GUARDAR SIN PÉRDIDA", 'ready': "Listo", 'saving': "Guardando...", 'close': "CERRAR MAESTRO", 'exit': "SALIR", 'err_time': "Ver IN/OUT"},
    'fr': {'select': "SÉLECTIONNER LE MASTER", 'load': "CHARGER LE FILM", 'in': "DÉBUT", 'out': "FIN", 'save': "ENREGISTRER SANS PERTE", 'ready': "Prêt", 'saving': "Enregistrement...", 'close': "FERMER LE MASTER", 'exit': "QUITTER", 'err_time': "Vérifier IN/OUT"},
    'pt': {'select': "SELECIONAR MASTER", 'load': "CARREGAR FILME", 'in': "DEFINIR INÍCIO", 'out': "DEFINIR FIM", 'save': "SALVAR SEM PERDA", 'ready': "Pronto", 'saving': "Salvando...", 'close': "FECHAR MASTER", 'exit': "SAIR", 'err_time': "Ver IN/OUT"},
    'ar': {'select': "اختر الفيديو الأساسي", 'load': "تحميل الفيلم", 'in': "تعيين البداية", 'out': "تعيين النهاية", 'save': "حفظ بدون فقدان", 'ready': "جاهز", 'saving': "جاري الحفظ...", 'close': "إغلاق الفيديو", 'exit': "إغلاق التطبيق", 'err_time': "تحقق من IN/OUT"},
    'zh': {'select': "选择母带素材", 'load': "加载视频", 'in': "设置入点", 'out': "设置出点", 'save': "无损保存片段", 'ready': "就绪", 'saving': "正在保存...", 'close': "关闭母带", 'exit': "退出应用", 'err_time': "检查IN/OUT"},
    'hi': {'select': "मास्टर फुटेज चुनें", 'load': "मूवी लोड करें", 'in': "शुरुआत सेट करें", 'out': "अंत सेट करें", 'save': "लॉसलेस क्लिप सहेजें", 'ready': "तैयार", 'saving': "सहेज रहा है...", 'close': "मास्टर बंद करें", 'exit': "ऐप बंद करें", 'err_time': "IN/OUT जांचें"}
}

try:
    import locale
    sys_lang = locale.getdefaultlocale()[0][:2]
    L = LOCALES.get(sys_lang, LOCALES['en'])
except:
    L = LOCALES['en']

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        layout.add_widget(Image(source='splash-screen.png', allow_stretch=True, keep_ratio=True))
        
        btn = Button(text=L['select'], size_hint=(0.8, 0.12), pos_hint={'center_x': 0.5, 'center_y': 0.25},
                     background_color=(0.96, 0.65, 0.14, 1), background_normal='', color=(0, 0, 0, 1), bold=True)
        btn.bind(on_release=self.open_picker)
        layout.add_widget(btn)

        exit_btn = Button(text=L['exit'], size_hint=(0.4, 0.08), pos_hint={'center_x': 0.5, 'center_y': 0.1},
                          background_color=(0.2, 0.2, 0.2, 1), color=(1, 1, 1, 1))
        exit_btn.bind(on_release=lambda x: App.get_running_app().stop())
        layout.add_widget(exit_btn)
        self.add_widget(layout)

    def open_picker(self, *args):
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE, Permission.WRITE_EXTERNAL_STORAGE, "android.permission.READ_MEDIA_VIDEO"])
            start_path = primary_external_storage_path()
        else:
            start_path = os.path.expanduser("~")
        content = FloatLayout()
        self.fc = FileChooserListView(path=start_path, filters=['*.mp4', '*.mov'], size_hint=(1, 0.85), pos_hint={'y': 0.15})
        load_btn = Button(text=L['load'], size_hint=(0.9, 0.1), pos_hint={'center_x': 0.5, 'y': 0.02},
                          background_color=(0.96, 0.65, 0.14, 1), background_normal='', color=(0, 0, 0, 1), bold=True)
        content.add_widget(self.fc)
        content.add_widget(load_btn)
        self.popup = Popup(title="LocalClip Search", content=content, size_hint=(0.95, 0.9))
        load_btn.bind(on_release=self.on_load)
        self.popup.open()

    def on_load(self, *args):
        if self.fc.selection:
            path = self.fc.selection[0].replace('file://', '')
            self.popup.dismiss()
            self.manager.get_screen('editor').video_path = path
            self.manager.current = 'editor'

class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.player = None
        self.poll_event = None
        self.position = 0.0
        self.duration = 0.0
        self.start_time = 0.0
        self.end_time = 0.0

    def on_enter(self):
        self.setup_ui()
        Clock.schedule_once(self.deferred_load, 1.2)

    def on_leave(self):
        if self.poll_event:
            self.poll_event.cancel()
        self.close_and_exit()

    def deferred_load(self, dt):
        self.status.text = f"Loading: {os.path.basename(self.video_path)}"
        try:
            if platform == 'android':
                from kvdroid.tools.exoplayer import ExoPlayer
                self.player = ExoPlayer()
                media_item = ExoPlayer.media_item_from_file(self.video_path)
                self.player.set_media_item(media_item)
                self.player.prepare()
                
                Clock.schedule_once(self._set_metadata, 0.8)
                self.poll_event = Clock.schedule_interval(self._poll, 0.2)
                self.status.text = L['ready']
            else:
                self.status.text = "Desktop mode not configured"
        except Exception as e:
            self.status.text = f"Player error: {str(e)[:50]}"

    def _set_metadata(self, dt):
        if self.player and platform == 'android':
            try:
                self.duration = self.player.get_duration() / 1000.0
                self.progress.max = self.duration
                self.end_time = self.duration
            except: pass

    def setup_ui(self):
        self.clear_widgets()
        l = FloatLayout()
        self.pos_label = Label(text="00:00.00", font_size='40sp', pos_hint={'center_x': 0.5, 'center_y': 0.75}, bold=True)
        self.progress = ProgressBar(max=100, size_hint=(0.9, 0.05), pos_hint={'center_x': 0.5, 'center_y': 0.68})
        l.add_widget(self.pos_label)
        l.add_widget(self.progress)

        seeks = [("-5s", -5), ("-1s", -1), ("+1s", 1), ("+5s", 5)]
        for i, (txt, val) in enumerate(seeks):
            b = Button(text=txt, size_hint=(0.2, 0.08), pos_hint={'x': 0.05 + (i*0.23), 'y': 0.55}, background_color=(0.3, 0.3, 0.3, 1))
            b.bind(on_release=lambda x, v=val: self._seek(v))
            l.add_widget(b)

        self.in_btn = Button(text=L['in'], size_hint=(0.45, 0.1), pos_hint={'x': 0.04, 'y': 0.42}, background_color=(0.1, 0.3, 0.1, 1), bold=True)
        self.out_btn = Button(text=L['out'], size_hint=(0.45, 0.1), pos_hint={'right': 0.96, 'y': 0.42}, background_color=(0.3, 0.1, 0.1, 1), bold=True)
        self.in_btn.bind(on_release=self.set_in)
        self.out_btn.bind(on_release=self.set_out)
        l.add_widget(self.in_btn)
        l.add_widget(self.out_btn)

        save_btn = Button(text=L['save'], size_hint=(0.92, 0.1), pos_hint={'center_x': 0.5, 'y': 0.28}, background_color=(0.4, 0.3, 0.1, 1), bold=True)
        save_btn.bind(on_release=self.save_clip)
        l.add_widget(save_btn)

        close_btn = Button(text=L['close'], size_hint=(0.92, 0.08), pos_hint={'center_x': 0.5, 'y': 0.16}, background_color=(0.2, 0.2, 0.2, 1))
        close_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(close_btn)

        self.status = Label(text=L['ready'], pos_hint={'center_x': 0.5, 'y': 0.05}, font_size='14sp')
        l.add_widget(self.status)
        self.add_widget(l)

    def set_in(self, *args):
        self.start_time = self.position
        self.in_btn.text = f"IN: {self._fmt(self.start_time)}"

    def set_out(self, *args):
        self.end_time = self.position
        self.out_btn.text = f"OUT: {self._fmt(self.end_time)}"

    def _seek(self, delta):
        if self.player and platform == 'android':
            new_pos = max(0, min(self.duration, self.position + delta))
            self.player.seek_to(int(new_pos * 1000))

    def close_and_exit(self, *args):
        if self.player and platform == 'android':
            self.player.release()
            self.player = None

    def _poll(self, dt):
        if self.player and platform == 'android':
            try:
                self.position = self.player.get_current_position() / 1000.0
                self.pos_label.text = self._fmt(self.position)
                self.progress.value = self.position
            except: pass

    def save_clip(self, *args):
        if self.end_time <= self.start_time:
            self.status.text = L['err_time']
            return
        base = primary_external_storage_path() if platform == 'android' else os.path.expanduser("~")
        out_dir = os.path.join(base, "Movies", "LocalClip_Exports")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"clip_{int(time.time())}.mp4")
        self.status.text = L['saving']
        def run():
            dur = self.end_time - self.start_time
            cmd = ["ffmpeg", "-y", "-ss", str(self.start_time), "-t", str(dur), "-i", self.video_path, "-c", "copy", out_file]
            subprocess.run(cmd)
            Clock.schedule_once(lambda d: setattr(self.status, 'text', f"Saved: {os.path.basename(out_file)}"))
        threading.Thread(target=run).start()

    def _fmt(self, s):
        m, sec = divmod(s, 60)
        return f"{int(m):02d}:{sec:05.2f}"

class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm

if __name__ == '__main__':
    LocalClipApp().run()