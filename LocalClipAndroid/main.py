# main.py — LocalClip Android
# No frame display. No threads for seek. Instant timecode. Lossless ffmpeg cut.

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
from io import BytesIO

LOCALES = {
    'en': {'select': "SELECT FOOTAGE", 'load': "LOAD", 'in': "SET IN", 'out': "SET OUT",
           'save': "SAVE LOSSLESS CLIP", 'ready': "Ready", 'saving': "Saving...",
           'close': "CLOSE", 'exit': "EXIT", 'err_time': "Check IN / OUT",
           'no_file': "No file selected", 'saved': "SAVED"},
    'es': {'select': "SELECCIONAR MASTER", 'load': "CARGAR", 'in': "MARCAR INICIO",
           'out': "MARCAR FINAL", 'save': "GUARDAR SIN PÉRDIDA", 'ready': "Listo",
           'saving': "Guardando...", 'close': "CERRAR", 'exit': "SALIR",
           'err_time': "Ver IN/OUT", 'no_file': "Sin archivo", 'saved': "GUARDADO"},
    'fr': {'select': "SÉLECTIONNER", 'load': "CHARGER", 'in': "DÉBUT", 'out': "FIN",
           'save': "ENREGISTRER SANS PERTE", 'ready': "Prêt", 'saving': "Enregistrement...",
           'close': "FERMER", 'exit': "QUITTER", 'err_time': "Vérifier IN/OUT",
           'no_file': "Aucun fichier", 'saved': "ENREGISTRÉ"},
    'pt': {'select': "SELECIONAR MASTER", 'load': "CARREGAR", 'in': "INÍCIO", 'out': "FIM",
           'save': "SALVAR SEM PERDA", 'ready': "Pronto", 'saving': "Salvando...",
           'close': "FECHAR", 'exit': "SAIR", 'err_time': "Ver IN/OUT",
           'no_file': "Sem arquivo", 'saved': "SALVO"},
    'ar': {'select': "اختر الفيديو", 'load': "تحميل", 'in': "بداية", 'out': "نهاية",
           'save': "حفظ بدون فقدان", 'ready': "جاهز", 'saving': "جاري الحفظ...",
           'close': "إغلاق", 'exit': "خروج", 'err_time': "تحقق من IN/OUT",
           'no_file': "لا يوجد ملف", 'saved': "تم الحفظ"},
    'zh': {'select': "选择素材", 'load': "加载", 'in': "设置入点", 'out': "设置出点",
           'save': "无损保存片段", 'ready': "就绪", 'saving': "正在保存...",
           'close': "关闭", 'exit': "退出", 'err_time': "检查IN/OUT",
           'no_file': "未选择文件", 'saved': "已保存"},
    'hi': {'select': "फुटेज चुनें", 'load': "लोड करें", 'in': "शुरुआत", 'out': "अंत",
           'save': "लॉसलेस क्लिप सहेजें", 'ready': "तैयार", 'saving': "सहेज रहा है...",
           'close': "बंद करें", 'exit': "बाहर", 'err_time': "IN/OUT जांचें",
           'no_file': "कोई फ़ाइल नहीं", 'saved': "सहेजा गया"},
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

# Button style helpers
BG_BLACK  = (0, 0, 0, 1)
BG_DARK   = (0.1, 0.1, 0.1, 1)
BG_MED    = (0.18, 0.18, 0.18, 1)
BG_WHITE  = (1, 1, 1, 1)
TXT_WHITE = (1, 1, 1, 1)
TXT_BLACK = (0, 0, 0, 1)


def btn(text, size_hint, pos_hint, bg=BG_MED, fg=TXT_WHITE,
        bold=False, font_size='15sp'):
    b = Button(
        text=text,
        size_hint=size_hint,
        pos_hint=pos_hint,
        background_color=bg,
        background_normal='',
        color=fg,
        bold=bold,
        font_size=font_size
    )
    return b


def get_ffmpeg_path():
    if platform == 'android':
        app_dir = os.path.dirname(os.path.abspath(__file__))
        private = os.environ.get('ANDROID_PRIVATE', '')
        candidates = [
            os.path.join(app_dir, 'bin', 'ffmpeg'),
            os.path.join(app_dir, 'ffmpeg'),
            os.path.join(private, 'bin', 'ffmpeg') if private else '',
            os.path.join(private, 'ffmpeg') if private else '',
            '/data/data/org.satdiva.localclip/files/app/bin/ffmpeg',
            '/data/data/org.satdiva.localclip/files/app/ffmpeg',
            '/data/user/0/org.satdiva.localclip/files/app/bin/ffmpeg',
            '/data/user/0/org.satdiva.localclip/files/app/ffmpeg',
        ]
        for path in candidates:
            if path and os.path.isfile(path):
                try:
                    os.chmod(path, 0o755)
                except Exception:
                    pass
                return path
        return 'ffmpeg'
    return 'ffmpeg'


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


def get_launch_count():
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.lc')
        with open(path, 'r') as f:
            return int(f.read().strip())
    except Exception:
        return 0


def increment_launch_count():
    count = get_launch_count() + 1
    try:
        path = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.lc')
        with open(path, 'w') as f:
            f.write(str(count))
    except Exception:
        pass
    return count


def fmt_ms(ms):
    """Format milliseconds as MM:SS.mmm"""
    s = ms / 1000.0
    m, sec = divmod(s, 60)
    return f"{int(m):02d}:{sec:06.3f}"


class MainScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        l = FloatLayout()
        l.canvas.before.clear()

        # Splash image full screen
        splash_path = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), 'splash-screen.png')
        if not os.path.isfile(splash_path):
            splash_path = 'splash-screen.png'

        l.add_widget(Image(
            source=splash_path,
            allow_stretch=True,
            keep_ratio=False,
            size_hint=(1, 1),
            pos_hint={'x': 0, 'y': 0}
        ))

        # SELECT button
        b = btn(L['select'],
                size_hint=(0.85, 0.09),
                pos_hint={'center_x': 0.5, 'center_y': 0.2},
                bg=BG_WHITE, fg=TXT_BLACK, bold=True, font_size='17sp')
        b.bind(on_release=self.open_picker)
        l.add_widget(b)

        # EXIT button
        e = btn(L['exit'],
                size_hint=(0.4, 0.07),
                pos_hint={'center_x': 0.5, 'center_y': 0.09},
                bg=BG_DARK, fg=TXT_WHITE, font_size='14sp')
        e.bind(on_release=lambda x: App.get_running_app().stop())
        l.add_widget(e)

        # Ko-fi small button
        k = btn("Ko-fi",
                size_hint=(0.2, 0.06),
                pos_hint={'right': 0.98, 'y': 0.01},
                bg=BG_WHITE, fg=TXT_BLACK, font_size='12sp')
        k.bind(on_release=lambda x: self._show_kofi())
        l.add_widget(k)

        self.add_widget(l)

    def on_enter(self):
        count = increment_launch_count()
        if count % 5 == 0:
            Clock.schedule_once(lambda dt: self._show_kofi(), 1.5)

    def _show_kofi(self):
        content = FloatLayout()
        content.add_widget(Label(
            text="LocalClip is free.\nIf it saves you time,\na coffee keeps it alive.",
            pos_hint={'center_x': 0.5, 'center_y': 0.65},
            font_size='15sp', halign='center', color=TXT_WHITE
        ))
        go = btn("ko-fi.com/1satdiva",
                 size_hint=(0.85, 0.2), pos_hint={'center_x': 0.5, 'center_y': 0.38},
                 bg=BG_WHITE, fg=TXT_BLACK, bold=True)
        cl = btn("Maybe later",
                 size_hint=(0.85, 0.15), pos_hint={'center_x': 0.5, 'center_y': 0.15},
                 bg=BG_DARK, fg=TXT_WHITE)
        content.add_widget(go)
        content.add_widget(cl)
        popup = Popup(title="Support LocalClip", content=content,
                      size_hint=(0.85, 0.42),
                      background_color=(0.05, 0.05, 0.05, 1))
        go.bind(on_release=lambda x: [open_kofi(), popup.dismiss()])
        cl.bind(on_release=popup.dismiss)
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
        fc = FileChooserListView(
            path=start_path,
            filters=['*.mp4', '*.mov', '*.MP4', '*.MOV'],
            size_hint=(1, 0.85),
            pos_hint={'y': 0.15}
        )
        load_b = btn(L['load'], size_hint=(0.9, 0.1),
                     pos_hint={'center_x': 0.5, 'y': 0.02},
                     bg=BG_WHITE, fg=TXT_BLACK, bold=True)
        content.add_widget(fc)
        content.add_widget(load_b)
        popup = Popup(title="LocalClip", content=content, size_hint=(0.95, 0.9))
        self._fc = fc
        self._picker_popup = popup

        def on_load(*args):
            if fc.selection:
                path = fc.selection[0].replace('file://', '')
                popup.dismiss()
                self.manager.get_screen('editor').load_video(path)
                self.manager.current = 'editor'

        load_b.bind(on_release=on_load)
        popup.open()


class EditorScreen(Screen):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.video_path = ""
        self.position_ms = 0
        self.duration_ms = 0
        self.start_ms = 0
        self.end_ms = 0
        self._build_ui()

    def _build_ui(self):
        l = FloatLayout()

        # ── TIMECODE ──────────────────────────────────────────
        self.timecode = Label(
            text="00:00.000",
            font_size='52sp',
            bold=True,
            color=TXT_WHITE,
            pos_hint={'center_x': 0.5, 'center_y': 0.88}
        )
        l.add_widget(self.timecode)

        # Duration label
        self.dur_label = Label(
            text="",
            font_size='13sp',
            color=(0.5, 0.5, 0.5, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.81}
        )
        l.add_widget(self.dur_label)

        # Progress bar
        self.progress = ProgressBar(
            max=1000, value=0,
            size_hint=(0.94, 0.018),
            pos_hint={'center_x': 0.5, 'center_y': 0.765}
        )
        l.add_widget(self.progress)

        # ── SEEK ROW 1: large ─────────────────────────────────
        # -60  -30  -5  +5  +30  +60
        row1 = [("-60s", -60000), ("-30s", -30000), ("-5s", -5000),
                ("+5s", 5000), ("+30s", 30000), ("+60s", 60000)]
        for i, (t, v) in enumerate(row1):
            b = btn(t, size_hint=(0.148, 0.063),
                    pos_hint={'x': 0.018 + i * 0.164, 'center_y': 0.71},
                    bg=BG_DARK, fg=TXT_WHITE, font_size='13sp')
            b.bind(on_release=lambda x, v=v: self._seek(v))
            l.add_widget(b)

        # ── SEEK ROW 2: seconds ───────────────────────────────
        # -3s  -1s  +1s  +3s
        row2 = [("-3s", -3000), ("-1s", -1000), ("+1s", 1000), ("+3s", 3000)]
        for i, (t, v) in enumerate(row2):
            b = btn(t, size_hint=(0.22, 0.063),
                    pos_hint={'x': 0.018 + i * 0.245, 'center_y': 0.638},
                    bg=BG_MED, fg=TXT_WHITE, bold=True, font_size='14sp')
            b.bind(on_release=lambda x, v=v: self._seek(v))
            l.add_widget(b)

        # ── SEEK ROW 3: sub-second ────────────────────────────
        # -500ms  -100ms  +100ms  +500ms
        row3 = [("-500", -500), ("-100", -100), ("+100", 100), ("+500", 500)]
        for i, (t, v) in enumerate(row3):
            b = btn(t, size_hint=(0.22, 0.063),
                    pos_hint={'x': 0.018 + i * 0.245, 'center_y': 0.566},
                    bg=BG_DARK, fg=TXT_WHITE, font_size='13sp')
            b.bind(on_release=lambda x, v=v: self._seek(v))
            l.add_widget(b)

        # ── IN / OUT ──────────────────────────────────────────
        self.in_btn = btn(L['in'], size_hint=(0.47, 0.078),
                          pos_hint={'x': 0.018, 'center_y': 0.485},
                          bg=BG_WHITE, fg=TXT_BLACK, bold=True, font_size='15sp')
        self.out_btn = btn(L['out'], size_hint=(0.47, 0.078),
                           pos_hint={'right': 0.982, 'center_y': 0.485},
                           bg=BG_WHITE, fg=TXT_BLACK, bold=True, font_size='15sp')
        self.in_btn.bind(on_release=self.set_in)
        self.out_btn.bind(on_release=self.set_out)
        l.add_widget(self.in_btn)
        l.add_widget(self.out_btn)

        # IN/OUT range display
        self.range_label = Label(
            text="IN: --:--   OUT: --:--",
            font_size='13sp',
            color=(0.7, 0.7, 0.7, 1),
            pos_hint={'center_x': 0.5, 'center_y': 0.42}
        )
        l.add_widget(self.range_label)

        # ── SAVE ──────────────────────────────────────────────
        save_b = btn(L['save'], size_hint=(0.96, 0.082),
                     pos_hint={'center_x': 0.5, 'center_y': 0.345},
                     bg=BG_WHITE, fg=TXT_BLACK, bold=True, font_size='16sp')
        save_b.bind(on_release=self.save_clip)
        l.add_widget(save_b)

        # ── SAVE STATUS — large, visible ──────────────────────
        self.save_label = Label(
            text="",
            font_size='16sp',
            bold=True,
            color=TXT_WHITE,
            pos_hint={'center_x': 0.5, 'center_y': 0.278},
            halign='center'
        )
        l.add_widget(self.save_label)

        # ── BOTTOM ROW: close + kofi ──────────────────────────
        close_b = btn(L['close'], size_hint=(0.75, 0.062),
                      pos_hint={'x': 0.018, 'center_y': 0.2},
                      bg=BG_DARK, fg=TXT_WHITE, font_size='14sp')
        close_b.bind(on_release=lambda x: setattr(self.manager, 'current', 'main'))
        l.add_widget(close_b)

        kofi_b = btn("Ko-fi", size_hint=(0.18, 0.062),
                     pos_hint={'right': 0.982, 'center_y': 0.2},
                     bg=BG_WHITE, fg=TXT_BLACK, font_size='12sp')
        kofi_b.bind(on_release=lambda x: open_kofi())
        l.add_widget(kofi_b)

        self.add_widget(l)

    def load_video(self, path):
        self.video_path = path
        self.position_ms = 0
        self.start_ms = 0
        self.end_ms = 0
        self.in_btn.text = L['in']
        self.out_btn.text = L['out']
        self.range_label.text = "IN: --:--   OUT: --:--"
        self.save_label.text = f"Loading: {os.path.basename(path)}"
        self.timecode.text = "00:00.000"

        def _load():
            dur = get_video_duration_ms(path)
            Clock.schedule_once(lambda dt: self._on_loaded(dur))

        threading.Thread(target=_load, daemon=True).start()

    def _on_loaded(self, duration_ms):
        self.duration_ms = duration_ms
        self.end_ms = duration_ms
        self.progress.max = max(duration_ms, 1)
        self.dur_label.text = f"Duration: {fmt_ms(duration_ms)}"
        self.save_label.text = ""

    def _seek(self, delta_ms):
        # Instant — no threads, no waiting
        self.position_ms = max(0, min(self.duration_ms, self.position_ms + delta_ms))
        self.timecode.text = fmt_ms(self.position_ms)
        if self.duration_ms > 0:
            self.progress.value = self.position_ms

    def set_in(self, *args):
        self.start_ms = self.position_ms
        self.in_btn.text = fmt_ms(self.start_ms)
        self._update_range()

    def set_out(self, *args):
        self.end_ms = self.position_ms
        self.out_btn.text = fmt_ms(self.end_ms)
        self._update_range()

    def _update_range(self):
        i = fmt_ms(self.start_ms)
        o = fmt_ms(self.end_ms)
        dur = (self.end_ms - self.start_ms) / 1000.0
        if dur > 0:
            m, s = divmod(dur, 60)
            self.range_label.text = f"IN {i}   OUT {o}   {int(m):02d}:{s:05.2f}"
        else:
            self.range_label.text = f"IN {i}   OUT {o}"

    def save_clip(self, *args):
        if self.end_ms <= self.start_ms:
            self.save_label.text = L['err_time']
            return
        if not self.video_path:
            self.save_label.text = L['no_file']
            return

        if platform == 'android':
            base = primary_external_storage_path()
        else:
            base = os.path.expanduser("~")

        out_dir = os.path.join(base, "Movies", "LocalClip_Exports")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"clip_{int(time.time())}.mp4")
        self.save_label.text = L['saving']

        def run():
            ffmpeg = get_ffmpeg_path()
            start_s = self.start_ms / 1000.0
            dur_s   = (self.end_ms - self.start_ms) / 1000.0
            cmd = [ffmpeg, '-y',
                   '-ss', f'{start_s:.3f}',
                   '-i', self.video_path,
                   '-t', f'{dur_s:.3f}',
                   '-c', 'copy',
                   '-avoid_negative_ts', 'make_zero',
                   '-movflags', '+faststart',
                   out_file]
            try:
                result = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                if result.returncode == 0:
                    msg = f"{L['saved']}\n{os.path.basename(out_file)}"
                else:
                    # Show full error so we can debug
                    stderr = result.stderr[-200:] if result.stderr else 'no output'
                    msg = f"ERROR:\n{stderr}"
            except FileNotFoundError:
                tried = get_ffmpeg_path()
                msg = f"ffmpeg not found.\nTried: {tried}"
            except subprocess.TimeoutExpired:
                msg = "Timeout. File too large?"
            except Exception as e:
                msg = f"Error: {str(e)[:100]}"

            Clock.schedule_once(lambda dt: setattr(self.save_label, 'text', msg))

        threading.Thread(target=run, daemon=True).start()


class LocalClipApp(App):
    def build(self):
        from kivy.core.window import Window
        Window.clearcolor = (0, 0, 0, 1)
        sm = ScreenManager()
        sm.add_widget(MainScreen(name='main'))
        sm.add_widget(EditorScreen(name='editor'))
        return sm


if __name__ == '__main__':
    LocalClipApp().run()
