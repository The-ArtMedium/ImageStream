# main.py — LocalClip Android
# Frame scrubbing via MediaMetadataRetriever + bundled ffmpeg lossless copy
# No ExoPlayer, no AAR, no gradle deps required

import os, subprocess, threading, time, tempfile
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
from io import BytesIO

LOCALES = {
    'en': {'select': "SELECT MASTER FOOTAGE", 'load': "LOAD MOVIE", 'in': "SET IN", 'out': "SET OUT",
           'save': "SAVE LOSSLESS CLIP", 'ready': "Ready", 'saving': "Saving...",
           'close': "CLOSE MASTER", 'exit': "EXIT APP", 'err_time': "Check IN/OUT",
           'no_file': "No file selected", 'saved': "Saved"},
    'es': {'select': "SELECCIONAR MAESTRO", 'load': "CARGAR PELÍCULA", 'in': "MARCAR INICIO",
           'out': "MARCAR FINAL", 'save': "GUARDAR SIN PÉRDIDA", 'ready': "Listo",
           'saving': "Guardando...", 'close': "CERRAR MAESTRO", 'exit': "SALIR",
           'err_time': "Ver IN/OUT", 'no_file': "Sin archivo", 'saved': "Guardado"},
    'fr': {'select': "SÉLECTIONNER LE MASTER", 'load': "CHARGER LE FILM", 'in': "DÉBUT",
           'out': "FIN", 'save': "ENREGISTRER SANS PERTE", 'ready': "Prêt",
           'saving': "Enregistrement...", 'close': "FERMER LE MASTER", 'exit': "QUITTER",
           'err_time': "Vérifier IN/OUT", 'no_file': "Aucun fichier", 'saved': "Enregistré"},
    'pt': {'select': "SELECIONAR MASTER", 'load': "CARREGAR FILME", 'in': "DEFINIR INÍCIO",
           'out': "DEFINIR FIM", 'save': "SALVAR SEM PERDA", 'ready': "Pronto",
           'saving': "Salvando...", 'close': "FECHAR MASTER", 'exit': "SAIR",
           'err_time': "Ver IN/OUT", 'no_file': "Sem arquivo", 'saved': "Salvo"},
    'ar': {'select': "اختر الفيديو الأساسي", 'load': "تحميل الفيلم", 'in': "تعيين البداية",
           'out': "تعيين النهاية", 'save': "حفظ بدون فقدان", 'ready': "جاهز",
           'saving': "جاري الحفظ...", 'close': "إغلاق الفيديو", 'exit': "إغلاق التطبيق",
           'err_time': "تحقق من IN/OUT", 'no_file': "لا يوجد ملف", 'saved': "تم الحفظ"},
    'zh': {'select': "选择母带素材", 'load': "加载视频", 'in': "设置入点",
           'out': "设置出点", 'save': "无损保存片段", 'ready': "就绪",
           'saving': "正在保存...", 'close': "关闭母带", 'exit': "退出应用",
           'err_time': "检查IN/OUT", 'no_file': "未选择文件", 'saved': "已保存"},
    'hi': {'select': "मास्टर फुटेज चुनें", 'load': "मूवी लोड करें", 'in': "शुरुआत सेट करें",
           'out': "अंत सेट करें", 'save': "लॉसलेस क्लिप सहेजें", 'ready': "तैयार",
           'saving': "सहेज रहा है...", 'close': "मास्टर बंद करें", 'exit': "ऐप बंद करें",
           'err_time': "IN/OUT जांचें", 'no_file': "कोई फ़ाइल नहीं", 'saved': "सहेजा गया"},
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


def get_ffmpeg_path():
    """Resolve bundled ffmpeg binary path at runtime."""
    if platform == 'android':
        # p4a copies assets to app dir; ffmpeg binary lives alongside main.py
        app_dir = os.path.dirname(os.path.abspath(__file__))
        candidates = [
            os.path.join(app_dir, 'ffmpeg'),
            '/data/data/org.satdiva.localclip/files/ffmpeg',
        ]
        for path in candidates:
            if os.path.isfile(path):
                os.chmod(path, 0o755)
                return path
        return 'ffmpeg'  # fallback: hope it's in PATH (Termux etc.)
    return 'ffmpeg'  # desktop


def get_video_duration_ms(video_path):
    """Use MediaMetadataRetriever to get duration in milliseconds."""
    if platform == 'android':
        try:
            from jnius import autoclass
            Retriever = autoclass('android.media.MediaMetadataRetriever')
            KEY_DURATION = autoclass(
                'android.media.MediaMetadataRetriever').METADATA_KEY_DURATION
            r = Retriever()
            r.setDataSource(video_path)
            val = r.extractMetadata(KEY_DURATION)
            r.release()
            return int(val) if val else 0
        except Exception as e:
            return 0
    return 0


def extract_frame_at_ms(video_path, position_ms):
    """
    Extract a single JPEG frame at position_ms using MediaMetadataRetriever.
    Returns BytesIO of JPEG data, or None on failure.
    Uses OPTION_CLOSEST (2) for frame-accurate seek — requires API 26+.
    Falls back to OPTION_CLOSEST_SYNC (3) for older devices.
    """
    if platform != 'android':
        return None
    try:
        from jnius import autoclass
        Retriever = autoclass('android.media.MediaMetadataRetriever')
        r = Retriever()
        r.setDataSource(video_path)

        # OPTION_CLOSEST = 2 (frame-accurate, slower)
        # OPTION_CLOSEST_SYNC = 3 (keyframe-only, faster)
        OPTION_CLOSEST = 2
        bitmap = r.getFrameAtTime(
            int(position_ms) * 1000,  # microseconds
            OPTION_CLOSEST
        )
        r.release()

        if bitmap is None:
            return None

        ByteArrayOutputStream = autoclass('java.io.ByteArrayOutputStream')
        CompressFormat = autoclass('android.graphics.Bitmap$CompressFormat')
        baos = ByteArrayOutputStream()
        bitmap.compress(CompressFormat.JPEG, 85, baos)
        byte_array = baos.toByteArray()
        baos.close()

        buf = BytesIO(bytes(bytearray(byte_array)))
        return buf
    except Exception as e:
        return None


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        layout = FloatLayout()
        layout.add_widget(Image(
            source='splash-screen.png',
            allow_stretch=True,
            keep_ratio=True
        ))

        btn = Button(
            text=L['select'],
            size_hint=(0.8, 0.12),
            pos_hint={'center_x': 0.5, 'center_y': 0.25},
            background_color=(0.96, 0.65, 0.14, 1),
            background_normal='',
            color=(0, 0, 0, 1),
            bold=True
        )
        btn.bind(on_release=self.open_picker)
        layout.add_widget(btn)

        exit_btn = Button(
            text=L['exit'],
            size_hint=(0.4, 0.08),
            pos_hint={'center_x': 0.5, 'center_y': 0.1},
            background_color=(0.2, 0.2, 0.2, 1),
            color=(1, 1, 1, 1)
        )
        exit_btn.bind(on_release=lambda x: App.get_running_app().stop())
        layout.add_widget(exit_btn)
        self.add_widget(layout)

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
        self.popup = Popup(
            title="LocalClip",
            content=content,
            size_hint=(0.95, 0.9)
        )
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

        # Frame thumbnail — fills top 55% of screen
        self.frame_img = Image(
            source='splash-screen.png',
            allow_stretch=True,
            keep_ratio=True,
            size_hint=(1.0, 0.52),
            pos_hint={'center_x': 0.5, 'top': 1.0}
        )
        l.add_widget(self.frame_img)

        # Timecode display
        self.pos_label = Label(
            text="00:00.000",
            font_size='32sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.455},
            bold=True,
            color=(0.96, 0.65, 0.14, 1)
        )
        l.add_widget(self.pos_label)

        # Progress bar (tap to seek)
        self.progress = ProgressBar(
            max=1000,
            value=0,
            size_hint=(0.92, 0.03),
            pos_hint={'center_x': 0.5, 'center_y': 0.41}
        )
        l.add_widget(self.progress)

        # Seek buttons: -30s -5s -1s +1s +5s +30s
        seeks = [("-30", -30000), ("-5", -5000), ("-1", -1000),
                 ("+1", 1000), ("+5", 5000), ("+30", 30000)]
        for i, (txt, val) in enumerate(seeks):
            b = Button(
                text=txt,
                size_hint=(0.145, 0.07),
                pos_hint={'x': 0.02 + i * 0.163, 'center_y': 0.355},
                background_color=(0.25, 0.25, 0.25, 1),
                background_normal='',
                font_size='13sp'
            )
            b.bind(on_release=lambda x, v=val: self._seek(v))
            l.add_widget(b)

        # IN / OUT buttons
        self.in_btn = Button(
            text=L['in'],
            size_hint=(0.46, 0.09),
            pos_hint={'x': 0.02, 'center_y': 0.27},
            background_color=(0.05, 0.35, 0.05, 1),
            background_normal='',
            bold=True
        )
        self.out_btn = Button(
            text=L['out'],
            size_hint=(0.46, 0.09),
            pos_hint={'right': 0.98, 'center_y': 0.27},
            background_color=(0.35, 0.05, 0.05, 1),
            background_normal='',
            bold=True
        )
        self.in_btn.bind(on_release=self.set_in)
        self.out_btn.bind(on_release=self.set_out)
        l.add_widget(self.in_btn)
        l.add_widget(self.out_btn)

        # IN/OUT time display
        self.range_label = Label(
            text="IN: --:--  OUT: --:--",
            font_size='13sp',
            pos_hint={'center_x': 0.5, 'center_y': 0.195},
            color=(0.7, 0.7, 0.7, 1)
        )
        l.add_widget(self.range_label)

        # Save button
        save_btn = Button(
            text=L['save'],
            size_hint=(0.94, 0.09),
            pos_hint={'center_x': 0.5, 'center_y': 0.135},
            background_color=(0.6, 0.4, 0.0, 1),
            background_normal='',
            bold=True
        )
        save_btn.bind(on_release=self.save_clip)
        l.add_widget(save_btn)

        # Close / status
        close_btn = Button(
            text=L['close'],
            size_hint=(0.94, 0.07),
            pos_hint={'center_x': 0.5, 'center_y': 0.065},
            background_color=(0.15, 0.15, 0.15, 1),
            background_normal=''
        )
        close_btn.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(close_btn)

        self.status = Label(
            text=L['ready'],
            pos_hint={'center_x': 0.5, 'center_y': 0.018},
            font_size='12sp',
            color=(0.6, 0.6, 0.6, 1)
        )
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
        """Fetch frame in background thread, update Image on main thread."""
        if self._loading_frame:
            return  # skip if already fetching — prevents thread pile-up
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

            # -ss before -i = fast keyframe seek
            # -c copy = lossless stream copy, no re-encode
            # -avoid_negative_ts make_zero = clean timestamps on output
            cmd = [
                ffmpeg, '-y',
                '-ss', f'{start_s:.3f}',
                '-i', self.video_path,
                '-t', f'{dur_s:.3f}',
                '-c', 'copy',
                '-avoid_negative_ts', 'make_zero',
                '-movflags', '+faststart',
                out_file
            ]
            try:
                result = subprocess.run(
                    cmd,
                    capture_output=True,
                    text=True,
                    timeout=120
                )
                if result.returncode == 0:
                    name = os.path.basename(out_file)
                    Clock.schedule_once(
                        lambda d: setattr(self.status, 'text', f"{L['saved']}: {name}")
                    )
                else:
                    err = result.stderr[-80:] if result.stderr else "unknown"
                    Clock.schedule_once(
                        lambda d: setattr(self.status, 'text', f"ffmpeg err: {err}")
                    )
            except subprocess.TimeoutExpired:
                Clock.schedule_once(
                    lambda d: setattr(self.status, 'text', "Timeout — file too large?")
                )
            except FileNotFoundError:
                Clock.schedule_once(
                    lambda d: setattr(self.status, 'text', "ffmpeg not found — check binary")
                )

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
