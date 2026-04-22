# main.py — LocalClip Android
# Frame scrubbing via MediaMetadataRetriever + bundled ffmpeg lossless copy
# No ExoPlayer, no AAR, no gradle deps required

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
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from io import BytesIO

LOCALES = {
    'en': {'select': "SELECT MASTER FOOTAGE", 'load': "LOAD MOVIE", 'in': "SET IN", 'out': "SET OUT",
           'save': "SAVE LOSSLESS CLIP", 'ready': "Ready", 'saving': "Saving...",
           'close': "CLOSE MASTER", 'exit': "EXIT APP", 'err_time': "Check IN/OUT",
           'no_file': "No file selected", 'saved': "Saved",
           'kofi': "Support on Ko-fi", 'kofi_msg': "LocalClip is free.\nIf it saves you time, a coffee helps keep it alive.",
           'kofi_btn': "ko-fi.com/1satdiva", 'kofi_close': "Maybe later"},
    'es': {'select': "SELECCIONAR MAESTRO", 'load': "CARGAR PELÍCULA", 'in': "MARCAR INICIO",
           'out': "MARCAR FINAL", 'save': "GUARDAR SIN PÉRDIDA", 'ready': "Listo",
           'saving': "Guardando...", 'close': "CERRAR MAESTRO", 'exit': "SALIR",
           'err_time': "Ver IN/OUT", 'no_file': "Sin archivo", 'saved': "Guardado",
           'kofi': "Apoya en Ko-fi", 'kofi_msg': "LocalClip es gratis.\nSi te ahorra tiempo, un café ayuda.",
           'kofi_btn': "ko-fi.com/1satdiva", 'kofi_close': "Quizás después"},
    'fr': {'select': "SÉLECTIONNER LE MASTER", 'load': "CHARGER LE FILM", 'in': "DÉBUT",
           'out': "FIN", 'save': "ENREGISTRER SANS PERTE", 'ready': "Prêt",
           'saving': "Enregistrement...", 'close': "FERMER LE MASTER", 'exit': "QUITTER",
           'err_time': "Vérifier IN/OUT", 'no_file': "Aucun fichier", 'saved': "Enregistré",
           'kofi': "Soutenir sur Ko-fi", 'kofi_msg': "LocalClip est gratuit.\nUn café aide à le maintenir.",
           'kofi_btn': "ko-fi.com/1satdiva", 'kofi_close': "Peut-être plus tard"},
    'pt': {'select': "SELECIONAR MASTER", 'load': "CARREGAR FILME", 'in': "DEFINIR INÍCIO",
           'out': "DEFINIR FIM", 'save': "SALVAR SEM PERDA", 'ready': "Pronto",
           'saving': "Salvando...", 'close': "FECHAR MASTER", 'exit': "SAIR",
           'err_time': "Ver IN/OUT", 'no_file': "Sem arquivo", 'saved': "Salvo",
           'kofi': "Apoiar no Ko-fi", 'kofi_msg': "LocalClip é grátis.\nUm café ajuda a mantê-lo vivo.",
           'kofi_btn': "ko-fi.com/1satdiva", 'kofi_close': "Talvez depois"},
    'ar': {'select': "اختر الفيديو الأساسي", 'load': "تحميل الفيلم", 'in': "تعيين البداية",
           'out': "تعيين النهاية", 'save': "حفظ بدون فقدان", 'ready': "جاهز",
           'saving': "جاري الحفظ...", 'close': "إغلاق الفيديو", 'exit': "إغلاق التطبيق",
           'err_time': "تحقق من IN/OUT", 'no_file': "لا يوجد ملف", 'saved': "تم الحفظ",
           'kofi': "ادعم على Ko-fi", 'kofi_msg': "LocalClip مجاني.\nقهوة صغيرة تساعد في الاستمرار.",
           'kofi_btn': "ko-fi.com/1satdiva", 'kofi_close': "ربما لاحقاً"},
    'zh': {'select': "选择母带素材", 'load': "加载视频", 'in': "设置入点",
           'out': "设置出点", 'save': "无损保存片段", 'ready': "就绪",
           'saving': "正在保存...", 'close': "关闭母带", 'exit': "退出应用",
           'err_time': "检查IN/OUT", 'no_file': "未选择文件", 'saved': "已保存",
           'kofi': "在Ko-fi支持", 'kofi_msg': "LocalClip是免费的。\n一杯咖啡帮助维持运营。",
           'kofi_btn': "ko-fi.com/1satdiva", 'kofi_close': "也许以后"},
    'hi': {'select': "मास्टर फुटेज चुनें", 'load': "मूवी लोड करें", 'in': "शुरुआत सेट करें",
           'out': "अंत सेट करें", 'save': "लॉसलेस क्लिप सहेजें", 'ready': "तैयार",
           'saving': "सहेज रहा है...", 'close': "मास्टर बंद करें", 'exit': "ऐप बंद करें",
           'err_time': "IN/OUT जांचें", 'no_file': "कोई फ़ाइल नहीं", 'saved': "सहेजा गया",
           'kofi': "Ko-fi पर समर्थन करें", 'kofi_msg': "LocalClip मुफ़्त है।\nएक कॉफ़ी इसे जीवित रखती है।",
           'kofi_btn': "ko-fi.com/1satdiva", 'kofi_close': "शायद बाद में"},
}

try:
    import locale
    sys_lang = locale.getdefaultlocale()[0][:2]
    L = LOCALES.get(sys_lang, LOCALES['en'])
except Exception:
    L = LOCALES['en']

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

KOFI_URL = "https://ko-fi.com/1satdiva"


def get_app_dir():
    if platform == 'android':
        d = os.environ.get('ANDROID_APP_PATH', '')
        if not d:
            d = os.path.dirname(os.path.abspath(__file__))
        return d
    return os.path.dirname(os.path.abspath(__file__))


def get_ffmpeg_path():
    if platform == 'android':
        app_dir = get_app_dir()
        candidates = [
            os.path.join(app_dir, 'bin', 'ffmpeg'),
            os.path.join(app_dir, 'ffmpeg'),
            '/data/data/org.satdiva.localclip/files/bin/ffmpeg',
            '/data/data/org.satdiva.localclip/files/ffmpeg',
            '/data/user/0/org.satdiva.localclip/files/bin/ffmpeg',
            '/data/user/0/org.satdiva.localclip/files/ffmpeg',
        ]
        for path in candidates:
            if os.path.isfile(path):
                try:
                    os.chmod(path, 0o755)
                except Exception:
                    pass
                return path
        return 'ffmpeg'
    return 'ffmpeg'


def get_launch_count():
    path = os.path.join(get_app_dir(), '.lc')
    try:
        with open(path, 'r') as f:
            return int(f.read().strip())
    except Exception:
        return 0


def increment_launch_count():
    path = os.path.join(get_app_dir(), '.lc')
    count = get_launch_count() + 1
    try:
        with open(path, 'w') as f:
            f.write(str(count))
    except Exception:
        pass
    return count


def get_video_duration_ms(video_path):
    if platform == 'android':
        try:
            from jnius import autoclass
            Retriever = autoclass('android.media.MediaMetadataRetriever')
            r = Retriever()
            r.setDataSource(video_path)
            val = r.extractMetadata(Retriever.METADATA_KEY_DURATION)
            r.release()
            return int(val) if val else 0
        except Exception:
            return 0
    return 0


def extract_frame_at_ms(video_path, position_ms):
    if platform != 'android':
        return None
    try:
        from jnius import autoclass
        Retriever = autoclass('android.media.MediaMetadataRetriever')
        r = Retriever()
        r.setDataSource(video_path)
        # OPTION_CLOSEST = 2 (frame-accurate, API 26+)
        bitmap = r.getFrameAtTime(int(position_ms) * 1000, 2)
        r.release()
        if bitmap is None:
            return None
        ByteArrayOutputStream = autoclass('java.io.ByteArrayOutputStream')
        CompressFormat = autoclass('android.graphics.Bitmap$CompressFormat')
        baos = ByteArrayOutputStream()
        bitmap.compress(CompressFormat.JPEG, 85, baos)
        buf = BytesIO(bytes(bytearray(baos.toByteArray())))
        baos.close()
        return buf
    except Exception:
        return None


def open_kofi():
    try:
        if platform == 'android':
            from jnius import autoclass
            Intent = autoclass('android.content.Intent')
            Uri = autoclass('android.net.Uri')
            PythonActivity = autoclass('org.kivy.android.PythonActivity')
            intent = Intent(Intent.ACTION_VIEW, Uri.parse(KOFI_URL))
            PythonActivity.mActivity.startActivity(intent)
        else:
            import webbrowser
            webbrowser.open(KOFI_URL)
    except Exception:
        pass


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self._build_ui()

    def _build_ui(self):
        layout = FloatLayout()

        splash = Image(
            source='splash-screen.png',
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        )
        layout.add_widget(splash)

        btn = Button(
            text=L['select'],
            size_hint=(0.8, 0.1),
            pos_hint={'center_x': 0.5, 'center_y': 0.22},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            bold=True,
            font_size='16sp'
        )
        btn.bind(on_release=self.open_picker)
        layout.add_widget(btn)

        exit_btn = Button(
            text=L['exit'],
            size_hint=(0.4, 0.07),
            pos_hint={'center_x': 0.5, 'center_y': 0.09},
            background_color=(0.15, 0.15, 0.15, 1),
            background_normal='',
            color=(1, 1, 1, 1),
            font_size='13sp'
        )
        exit_btn.bind(on_release=lambda x: App.get_running_app().stop())
        layout.add_widget(exit_btn)

        kofi_btn = Button(
            text="☕",
            size_hint=(0.12, 0.07),
            pos_hint={'right': 0.98, 'y': 0.01},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            font_size='18sp'
        )
        kofi_btn.bind(on_release=lambda x: self._show_kofi_popup())
        layout.add_widget(kofi_btn)

        self.add_widget(layout)

    def on_enter(self):
        count = increment_launch_count()
        if count % 5 == 0:
            Clock.schedule_once(lambda dt: self._show_kofi_popup(), 1.5)

    def _show_kofi_popup(self):
        content = FloatLayout()
        msg = Label(
            text=L['kofi_msg'],
            pos_hint={'center_x': 0.5, 'center_y': 0.65},
            font_size='15sp',
            halign='center',
            text_size=(Window.width * 0.75, None)
        )
        go_btn = Button(
            text=L['kofi_btn'],
            size_hint=(0.85, 0.2),
            pos_hint={'center_x': 0.5, 'center_y': 0.38},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            bold=True
        )
        close_btn = Button(
            text=L['kofi_close'],
            size_hint=(0.85, 0.15),
            pos_hint={'center_x': 0.5, 'center_y': 0.15},
            background_color=(0.2, 0.2, 0.2, 1),
            background_normal=''
        )
        content.add_widget(msg)
        content.add_widget(go_btn)
        content.add_widget(close_btn)
        popup = Popup(
            title=L['kofi'],
            content=content,
            size_hint=(0.85, 0.4)
        )
        go_btn.bind(on_release=lambda x: [open_kofi(), popup.dismiss()])
        close_btn.bind(on_release=popup.dismiss)
        popup.open()

    def open_picker(self, *args):
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE,
                Permission.WRITE_EXTERNAL_STORAGE,
                "android.permission.READ_MEDIA_VIDEO"
            ])
            start_path = primary_external_storage_path()
        else:
            start_path = os.path.expanduser("~")

        content = FloatLayout()
        self.fc = FileChooserListView(
            path=start_path,
            filters=['*.mp4', '*.mov', '*.MP4', '*.MOV'],
            size_hint=(1, 0.85),
            pos_hint={'y': 0.15}
        )
        load_btn = Button(
            text=L['load'],
            size_hint=(0.9, 0.1),
            pos_hint={'center_x': 0.5, 'y': 0.02},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            bold=True
        )
        content.add_widget(self.fc)
        content.add_widget(load_btn)
        self.popup = Popup(title="LocalClip", content=content, size_hint=(0.95, 0.9))
        load_btn.bind(on_release=self.on_load)
        self.popup.open()

    def on_load(self, *args):
        if self.fc.selection:
            path = self.fc.selection[0].replace('file://', '')
            self.popup.dismiss()
            editor = self.manager.get_screen('editor')
            editor.load_video(path)
            self.manager.current = 'editor'


class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.position_ms = 0
        self.duration_ms = 0
        self.start_ms = 0
        self.end_ms = 0
        self._frame_thread = None
        self._loading_frame = False
        self.setup_ui()

    def setup_ui(self):
        self.clear_widgets()
        l = FloatLayout()

        self.frame_img = Image(
            source='splash-screen.png',
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1.0, 0.46),
            pos_hint={'center_x': 0.5, 'top': 1.0}
        )
        l.add_widget(self.frame_img)

        self.pos_label = Label(
            text="00:00.000",
            font_size='26sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.515},
            bold=True,
            color=(0.96, 0.65, 0.14, 1)
        )
        l.add_widget(self.pos_label)

        self.progress = ProgressBar(
            max=1000,
            value=0,
            size_hint=(0.92, 0.02),
            pos_hint={'center_x': 0.5, 'center_y': 0.478}
        )
        l.add_widget(self.progress)

        # Row 1: large — -60 -30 -5 +5 +30 +60
        seeks_r1 = [("-60", -60000), ("-30", -30000), ("-5", -5000),
                    ("+5", 5000), ("+30", 30000), ("+60", 60000)]
        for i, (txt, val) in enumerate(seeks_r1):
            b = Button(text=txt, size_hint=(0.145, 0.057),
                       pos_hint={'x': 0.02 + i * 0.163, 'center_y': 0.432},
                       background_color=(0.2, 0.2, 0.2, 1), background_normal='', font_size='12sp')
            b.bind(on_release=lambda x, v=val: self._seek(v))
            l.add_widget(b)

        # Row 2: medium — -1s +1s
        seeks_r2 = [("-1s", -1000), ("+1s", 1000)]
        for i, (txt, val) in enumerate(seeks_r2):
            b = Button(text=txt, size_hint=(0.3, 0.057),
                       pos_hint={'x': 0.02 + i * 0.5, 'center_y': 0.368},
                       background_color=(0.28, 0.28, 0.12, 1), background_normal='',
                       bold=True, font_size='13sp')
            b.bind(on_release=lambda x, v=val: self._seek(v))
            l.add_widget(b)

        # Row 3: fine — -500ms -100ms +100ms +500ms
        seeks_r3 = [("-500", -500), ("-100", -100), ("+100", 100), ("+500", 500)]
        for i, (txt, val) in enumerate(seeks_r3):
            b = Button(text=txt, size_hint=(0.22, 0.057),
                       pos_hint={'x': 0.02 + i * 0.245, 'center_y': 0.304},
                       background_color=(0.12, 0.25, 0.28, 1), background_normal='', font_size='11sp')
            b.bind(on_release=lambda x, v=val: self._seek(v))
            l.add_widget(b)

        # IN / OUT
        self.in_btn = Button(text=L['in'], size_hint=(0.46, 0.075),
                             pos_hint={'x': 0.02, 'center_y': 0.235},
                             background_color=(0.05, 0.38, 0.05, 1), background_normal='', bold=True)
        self.out_btn = Button(text=L['out'], size_hint=(0.46, 0.075),
                              pos_hint={'right': 0.98, 'center_y': 0.235},
                              background_color=(0.38, 0.05, 0.05, 1), background_normal='', bold=True)
        self.in_btn.bind(on_release=self.set_in)
        self.out_btn.bind(on_release=self.set_out)
        l.add_widget(self.in_btn)
        l.add_widget(self.out_btn)

        self.range_label = Label(text="IN: --:--  OUT: --:--", font_size='11sp',
                                 pos_hint={'center_x': 0.5, 'center_y': 0.175},
                                 color=(0.7, 0.7, 0.7, 1))
        l.add_widget(self.range_label)

        save_btn = Button(text=L['save'], size_hint=(0.94, 0.075),
                          pos_hint={'center_x': 0.5, 'center_y': 0.118},
                          background_color=(0.6, 0.4, 0.0, 1), background_normal='', bold=True)
        save_btn.bind(on_release=self.save_clip)
        l.add_widget(save_btn)

        close_btn = Button(text=L['close'], size_hint=(0.78, 0.057),
                           pos_hint={'x': 0.02, 'center_y': 0.048},
                           background_color=(0.15, 0.15, 0.15, 1), background_normal='')
        close_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(close_btn)

        kofi_btn = Button(text="☕", size_hint=(0.14, 0.057),
                          pos_hint={'right': 0.98, 'center_y': 0.048},
                          background_color=(0.96, 0.65, 0.14, 1), background_normal='',
                          color=(0, 0, 0, 1), font_size='16sp')
        kofi_btn.bind(on_release=lambda x: open_kofi())
        l.add_widget(kofi_btn)

        self.status = Label(text=L['ready'], pos_hint={'center_x': 0.5, 'center_y': 0.012},
                            font_size='10sp', color=(0.5, 0.5, 0.5, 1))
        l.add_widget(self.status)
        self.add_widget(l)

    def load_video(self, path):
        self.video_path = path
        self.position_ms = 0
        self.start_ms = 0
        self.end_ms = 0
        self.in_btn.text = L['in']
        self.out_btn.text = L['out']
        self.range_label.text = "IN: --:--  OUT: --:--"
        self.status.text = f"Loading: {os.path.basename(path)}"

        def _load():
            dur = get_video_duration_ms(path)
            Clock.schedule_once(lambda dt: self._on_loaded(dur))

        threading.Thread(target=_load, daemon=True).start()

    def _on_loaded(self, duration_ms):
        self.duration_ms = duration_ms
        self.end_ms = duration_ms
        self.progress.max = max(duration_ms, 1)
        self.status.text = L['ready']
        self._fetch_frame(0)

    def _seek(self, delta_ms):
        new_pos = max(0, min(self.duration_ms, self.position_ms + delta_ms))
        if new_pos == self.position_ms:
            return
        self.position_ms = new_pos
        self.pos_label.text = self._fmt(self.position_ms)
        self.progress.value = self.position_ms
        self._fetch_frame(self.position_ms)

    def _fetch_frame(self, position_ms):
        if self._loading_frame:
            return
        self._loading_frame = True

        def _run():
            buf = extract_frame_at_ms(self.video_path, position_ms)
            Clock.schedule_once(lambda dt: self._display_frame(buf))

        self._frame_thread = threading.Thread(target=_run, daemon=True)
        self._frame_thread.start()

    def _display_frame(self, buf):
        self._loading_frame = False
        if buf is None:
            return
        try:
            buf.seek(0)
            core_img = CoreImage(buf, ext='jpg')
            self.frame_img.texture = core_img.texture
        except Exception as e:
            self.status.text = f"Frame err: {str(e)[:40]}"

    def set_in(self, *args):
        self.start_ms = self.position_ms
        self.in_btn.text = f"IN: {self._fmt(self.start_ms)}"
        self._update_range_label()

    def set_out(self, *args):
        self.end_ms = self.position_ms
        self.out_btn.text = f"OUT: {self._fmt(self.end_ms)}"
        self._update_range_label()

    def _update_range_label(self):
        i = self._fmt(self.start_ms) if self.start_ms else "--:--"
        o = self._fmt(self.end_ms) if self.end_ms else "--:--"
        dur_s = (self.end_ms - self.start_ms) / 1000.0
        if dur_s > 0:
            self.range_label.text = f"IN: {i}  OUT: {o}  ({self._fmt_s(dur_s)})"
        else:
            self.range_label.text = f"IN: {i}  OUT: {o}"

    def save_clip(self, *args):
        if self.end_ms <= self.start_ms:
            self.status.text = L['err_time']
            return
        if not self.video_path:
            self.status.text = L['no_file']
            return

        if platform == 'android':
            base = primary_external_storage_path()
        else:
            base = os.path.expanduser("~")

        out_dir = os.path.join(base, "Movies", "LocalClip_Exports")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"clip_{int(time.time())}.mp4")
        self.status.text = L['saving']

        def run():
            ffmpeg = get_ffmpeg_path()
            start_s = self.start_ms / 1000.0
            dur_s = (self.end_ms - self.start_ms) / 1000.0
            cmd = [ffmpeg, '-y',
                   '-ss', f'{start_s:.3f}',
                   '-i', self.video_path,
                   '-t', f'{dur_s:.3f}',
                   '-c', 'copy',
                   '-avoid_negative_ts', 'make_zero',
                   '-movflags', '+faststart',
                   out_file]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=120)
                if result.returncode == 0:
                    name = os.path.basename(out_file)
                    Clock.schedule_once(lambda d: setattr(self.status, 'text', f"{L['saved']}: {name}"))
                else:
                    err = result.stderr[-100:] if result.stderr else "unknown"
                    Clock.schedule_once(lambda d: setattr(self.status, 'text', f"ffmpeg err: {err}"))
            except subprocess.TimeoutExpired:
                Clock.schedule_once(lambda d: setattr(self.status, 'text', "Timeout — file too large?"))
            except FileNotFoundError:
                Clock.schedule_once(lambda d: setattr(self.status, 'text', "ffmpeg not found — check binary"))

        threading.Thread(target=run, daemon=True).start()

    def _fmt(self, ms):
        s = ms / 1000.0
        m, sec = divmod(s, 60)
        return f"{int(m):02d}:{sec:06.3f}"

    def _fmt_s(self, s):
        m, sec = divmod(s, 60)
        return f"{int(m):02d}:{sec:06.3f}"


class LocalClipApp(App):
    def build(self):
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm


if __name__ == '__main__':
    LocalClipApp().run()
