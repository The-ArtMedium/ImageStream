"""
LocalClip — Android Video Trimmer
Part of the ImageStream Mobile Suite — The Art Medium

Non-destructive lossless video trimming.
Drag handles + manual time input.
Output to LocalClip_Exports/ — originals never touched.
Feeds directly into LocalEdit workflow.

Languages: English · Español · Français · Português · العربية · 中文 · हिन्दी

Dependencies:
  kivy
  ffpyplayer      (video preview)
  python-ffmpeg   (lossless export via ffmpeg stream copy)

Build:
  buildozer android debug
"""

import os
import threading
from pathlib import Path
from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.relativelayout import RelativeLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.textinput import TextInput
from kivy.uix.slider import Slider
from kivy.uix.popup import Popup
from kivy.uix.filechooser import FileChooserListView
from kivy.uix.progressbar import ProgressBar
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line, RoundedRectangle
from kivy.metrics import dp, sp
from kivy.core.window import Window
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty, BooleanProperty
from kivy.utils import get_color_from_hex

try:
    from ffpyplayer.player import MediaPlayer
    PREVIEW_AVAILABLE = True
except ImportError:
    PREVIEW_AVAILABLE = False

# ── PALETTE ──────────────────────────────────────────────
BG      = get_color_from_hex("#0a0a0a")
BG2     = get_color_from_hex("#111111")
BG3     = get_color_from_hex("#1a1a1a")
BG4     = get_color_from_hex("#222222")
ACCENT  = get_color_from_hex("#f5a623")
ACCENT2 = get_color_from_hex("#e8941a")
GREEN   = get_color_from_hex("#4ade80")
GREEN2  = get_color_from_hex("#166534")
RED     = get_color_from_hex("#f87171")
RED2    = get_color_from_hex("#7f1d1d")
BLUE    = get_color_from_hex("#60a5fa")
TEXT    = get_color_from_hex("#ffffff")
TEXT2   = get_color_from_hex("#cccccc")
TEXT3   = get_color_from_hex("#888888")

# ── TRANSLATIONS ─────────────────────────────────────────
LANGUAGES = {
    "en": {
        "name": "English", "dir": "ltr",
        "app_title":      "LocalClip",
        "tagline":        "Trim videos. Lossless. Offline.",
        "pick_video":     "PICK VIDEO",
        "no_video":       "Tap to select a video from your device",
        "trim":           "TRIM",
        "start":          "START",
        "end":            "END",
        "duration":       "Duration",
        "preview":        "▶  PREVIEW",
        "export":         "✓  EXPORT CLIP",
        "exporting":      "Exporting…",
        "done_title":     "Clip Saved",
        "done_msg":       "Saved to LocalClip_Exports/\nOriginal untouched.",
        "error_title":    "Error",
        "no_ffmpeg":      "ffmpeg not found.\nInstall ffmpeg to export clips.",
        "original":       "Original",
        "clip":           "Clip",
        "non_dest":       "Non-destructive · Original never modified",
        "drag_hint":      "Drag handles to trim · or type exact time below",
        "language":       "Language",
        "back":           "←",
        "open_exports":   "OPEN EXPORTS FOLDER",
        "export_another": "TRIM ANOTHER",
        "time_format":    "HH:MM:SS",
        "lossless_badge": "LOSSLESS",
        "offline_badge":  "OFFLINE",
        "free_badge":     "FREE",
    },
    "es": {
        "name": "Español", "dir": "ltr",
        "app_title":      "LocalClip",
        "tagline":        "Recorta videos. Sin pérdida. Sin internet.",
        "pick_video":     "ELEGIR VIDEO",
        "no_video":       "Toca para seleccionar un video",
        "trim":           "RECORTAR",
        "start":          "INICIO",
        "end":            "FIN",
        "duration":       "Duración",
        "preview":        "▶  VISTA PREVIA",
        "export":         "✓  EXPORTAR CLIP",
        "exporting":      "Exportando…",
        "done_title":     "Clip Guardado",
        "done_msg":       "Guardado en LocalClip_Exports/\nOriginal sin cambios.",
        "error_title":    "Error",
        "no_ffmpeg":      "ffmpeg no encontrado.",
        "original":       "Original",
        "clip":           "Clip",
        "non_dest":       "No destructivo · Original nunca modificado",
        "drag_hint":      "Arrastra los puntos · o escribe el tiempo exacto",
        "language":       "Idioma",
        "back":           "←",
        "open_exports":   "ABRIR CARPETA",
        "export_another": "RECORTAR OTRO",
        "time_format":    "HH:MM:SS",
        "lossless_badge": "SIN PÉRDIDA",
        "offline_badge":  "SIN INTERNET",
        "free_badge":     "GRATIS",
    },
    "fr": {
        "name": "Français", "dir": "ltr",
        "app_title":      "LocalClip",
        "tagline":        "Coupez des vidéos. Sans perte. Hors ligne.",
        "pick_video":     "CHOISIR VIDÉO",
        "no_video":       "Appuyez pour sélectionner une vidéo",
        "trim":           "COUPER",
        "start":          "DÉBUT",
        "end":            "FIN",
        "duration":       "Durée",
        "preview":        "▶  APERÇU",
        "export":         "✓  EXPORTER",
        "exporting":      "Export en cours…",
        "done_title":     "Clip Sauvegardé",
        "done_msg":       "Sauvegardé dans LocalClip_Exports/\nOriginal intact.",
        "error_title":    "Erreur",
        "no_ffmpeg":      "ffmpeg introuvable.",
        "original":       "Original",
        "clip":           "Clip",
        "non_dest":       "Non destructif · Original jamais modifié",
        "drag_hint":      "Faites glisser les poignées · ou saisissez le temps exact",
        "language":       "Langue",
        "back":           "←",
        "open_exports":   "OUVRIR DOSSIER",
        "export_another": "COUPER UN AUTRE",
        "time_format":    "HH:MM:SS",
        "lossless_badge": "SANS PERTE",
        "offline_badge":  "HORS LIGNE",
        "free_badge":     "GRATUIT",
    },
    "pt": {
        "name": "Português", "dir": "ltr",
        "app_title":      "LocalClip",
        "tagline":        "Corte vídeos. Sem perdas. Offline.",
        "pick_video":     "ESCOLHER VÍDEO",
        "no_video":       "Toque para selecionar um vídeo",
        "trim":           "CORTAR",
        "start":          "INÍCIO",
        "end":            "FIM",
        "duration":       "Duração",
        "preview":        "▶  PRÉ-VISUALIZAR",
        "export":         "✓  EXPORTAR CLIP",
        "exporting":      "Exportando…",
        "done_title":     "Clip Salvo",
        "done_msg":       "Salvo em LocalClip_Exports/\nOriginal intocado.",
        "error_title":    "Erro",
        "no_ffmpeg":      "ffmpeg não encontrado.",
        "original":       "Original",
        "clip":           "Clip",
        "non_dest":       "Não destrutivo · Original nunca modificado",
        "drag_hint":      "Arraste os pontos · ou digite o tempo exato",
        "language":       "Idioma",
        "back":           "←",
        "open_exports":   "ABRIR PASTA",
        "export_another": "CORTAR OUTRO",
        "time_format":    "HH:MM:SS",
        "lossless_badge": "SEM PERDAS",
        "offline_badge":  "OFFLINE",
        "free_badge":     "GRÁTIS",
    },
    "ar": {
        "name": "العربية", "dir": "rtl",
        "app_title":      "LocalClip",
        "tagline":        "قص الفيديو. بدون فقدان. بدون إنترنت.",
        "pick_video":     "اختر فيديو",
        "no_video":       "انقر لاختيار فيديو من جهازك",
        "trim":           "قص",
        "start":          "البداية",
        "end":            "النهاية",
        "duration":       "المدة",
        "preview":        "▶  معاينة",
        "export":         "✓  تصدير",
        "exporting":      "جارٍ التصدير…",
        "done_title":     "تم حفظ الكليب",
        "done_msg":       "محفوظ في LocalClip_Exports/\nالأصل لم يُمَس.",
        "error_title":    "خطأ",
        "no_ffmpeg":      "ffmpeg غير موجود.",
        "original":       "الأصلي",
        "clip":           "كليب",
        "non_dest":       "غير تدميري · الأصل لم يُعدَّل",
        "drag_hint":      "اسحب النقاط · أو اكتب الوقت الدقيق",
        "language":       "اللغة",
        "back":           "→",
        "open_exports":   "فتح مجلد التصدير",
        "export_another": "قص فيديو آخر",
        "time_format":    "HH:MM:SS",
        "lossless_badge": "بدون فقدان",
        "offline_badge":  "بدون إنترنت",
        "free_badge":     "مجاني",
    },
    "zh": {
        "name": "中文", "dir": "ltr",
        "app_title":      "LocalClip",
        "tagline":        "剪辑视频。无损。离线。",
        "pick_video":     "选择视频",
        "no_video":       "点击从设备选择视频",
        "trim":           "剪辑",
        "start":          "开始",
        "end":            "结束",
        "duration":       "时长",
        "preview":        "▶  预览",
        "export":         "✓  导出片段",
        "exporting":      "导出中…",
        "done_title":     "片段已保存",
        "done_msg":       "已保存到 LocalClip_Exports/\n原始文件未修改。",
        "error_title":    "错误",
        "no_ffmpeg":      "未找到 ffmpeg。",
        "original":       "原始",
        "clip":           "片段",
        "non_dest":       "非破坏性 · 原始文件从不修改",
        "drag_hint":      "拖动手柄修剪 · 或输入精确时间",
        "language":       "语言",
        "back":           "←",
        "open_exports":   "打开导出文件夹",
        "export_another": "剪辑另一个",
        "time_format":    "HH:MM:SS",
        "lossless_badge": "无损",
        "offline_badge":  "离线",
        "free_badge":     "免费",
    },
    "hi": {
        "name": "हिन्दी", "dir": "ltr",
        "app_title":      "LocalClip",
        "tagline":        "वीडियो ट्रिम करें। बिना नुकसान। ऑफलाइन।",
        "pick_video":     "वीडियो चुनें",
        "no_video":       "वीडियो चुनने के लिए टैप करें",
        "trim":           "ट्रिम",
        "start":          "शुरू",
        "end":            "अंत",
        "duration":       "अवधि",
        "preview":        "▶  पूर्वावलोकन",
        "export":         "✓  क्लिप निर्यात करें",
        "exporting":      "निर्यात हो रहा है…",
        "done_title":     "क्लिप सहेजा",
        "done_msg":       "LocalClip_Exports/ में सहेजा\nमूल अछूता।",
        "error_title":    "त्रुटि",
        "no_ffmpeg":      "ffmpeg नहीं मिला।",
        "original":       "मूल",
        "clip":           "क्लिप",
        "non_dest":       "गैर-विनाशकारी · मूल कभी संशोधित नहीं",
        "drag_hint":      "हैंडल खींचें · या सटीक समय टाइप करें",
        "language":       "भाषा",
        "back":           "←",
        "open_exports":   "निर्यात फ़ोल्डर खोलें",
        "export_another": "दूसरा ट्रिम करें",
        "time_format":    "HH:MM:SS",
        "lossless_badge": "बिना नुकसान",
        "offline_badge":  "ऑफलाइन",
        "free_badge":     "मुफ़्त",
    },
}

LANG_ORDER = ["en", "es", "fr", "pt", "ar", "zh", "hi"]


# ── HELPERS ───────────────────────────────────────────────
def secs_to_hms(secs):
    secs = max(0, int(secs))
    h = secs // 3600
    m = (secs % 3600) // 60
    s = secs % 60
    return f"{h:02d}:{m:02d}:{s:02d}"


def hms_to_secs(hms):
    try:
        parts = hms.strip().split(":")
        if len(parts) == 3:
            return int(parts[0]) * 3600 + int(parts[1]) * 60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0]) * 60 + int(parts[1])
        else:
            return float(hms)
    except Exception:
        return None


def get_video_duration(path):
    import subprocess
    try:
        result = subprocess.run(
            ["ffprobe", "-v", "error",
             "-show_entries", "format=duration",
             "-of", "default=noprint_wrappers=1:nokey=1",
             str(path)],
            capture_output=True, text=True, timeout=10)
        return float(result.stdout.strip())
    except Exception:
        return 0.0


def export_clip(src, dst, start_sec, end_sec, progress_cb=None):
    import subprocess
    duration = end_sec - start_sec
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-i", str(src),
        "-t", str(duration),
        "-c", "copy",
        "-avoid_negative_ts", "make_zero",
        str(dst)
    ]
    proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
    for line in proc.stderr:
        if progress_cb:
            progress_cb(line)
    proc.wait()
    return proc.returncode == 0


def make_export_path(src_path, start_sec, end_sec):
    src = Path(src_path)
    out = src.parent / "LocalClip_Exports"
    out.mkdir(exist_ok=True)
    name = f"{src.stem}_{int(start_sec)}s-{int(end_sec)}s{src.suffix}"
    return out / name


# ── STYLED WIDGETS ────────────────────────────────────────
def make_btn(text, bg_hex="#222222", fg_hex="#ffffff", font_size=16, bold=True):
    return Button(
        text=text,
        font_size=sp(font_size),
        bold=bold,
        color=get_color_from_hex(fg_hex),
        background_normal="",
        background_color=get_color_from_hex(bg_hex),
    )


def make_label(text, font_size=14, color_hex="#cccccc", bold=False, halign="left"):
    lbl = Label(
        text=text,
        font_size=sp(font_size),
        bold=bold,
        color=get_color_from_hex(color_hex),
        halign=halign,
        valign="middle",
    )
    lbl.bind(size=lbl.setter("text_size"))
    return lbl


# ── TRIM BAR ──────────────────────────────────────────────
class TrimBar(Widget):
    start_ratio = NumericProperty(0.0)
    end_ratio   = NumericProperty(1.0)

    HANDLE_W = dp(22)
    TRACK_H  = dp(10)

    def __init__(self, on_change=None, **kwargs):
        super().__init__(**kwargs)
        self._on_change  = on_change
        self._drag_start = False
        self._drag_end   = False
        self.bind(pos=self._redraw, size=self._redraw,
                  start_ratio=self._redraw, end_ratio=self._redraw)

    def _redraw(self, *_):
        self.canvas.clear()
        x, y = self.x, self.y
        w, h = self.width, self.height
        cy   = y + h / 2
        sx   = x + self.start_ratio * w
        ex   = x + self.end_ratio * w

        with self.canvas:
            Color(*get_color_from_hex("#2a2a2a"))
            Rectangle(pos=(x, cy - self.TRACK_H / 2), size=(w, self.TRACK_H))

            Color(*get_color_from_hex("#f5a623"), 0.5)
            Rectangle(pos=(sx, cy - self.TRACK_H / 2), size=(ex - sx, self.TRACK_H))

            Color(*get_color_from_hex("#f5a623"))
            Rectangle(pos=(sx - self.HANDLE_W / 2, cy - dp(20)), size=(self.HANDLE_W, dp(40)))
            Rectangle(pos=(ex - self.HANDLE_W / 2, cy - dp(20)), size=(self.HANDLE_W, dp(40)))

            Color(*get_color_from_hex("#0a0a0a"))
            for hx in [sx, ex]:
                for dy in [-dp(6), 0, dp(6)]:
                    Line(points=[hx - dp(3), cy + dy, hx + dp(3), cy + dy], width=dp(1.5))

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos):
            return False
        sx = self.x + self.start_ratio * self.width
        ex = self.x + self.end_ratio * self.width
        if abs(touch.x - sx) < dp(30):
            self._drag_start = True
            touch.grab(self)
            return True
        if abs(touch.x - ex) < dp(30):
            self._drag_end = True
            touch.grab(self)
            return True
        return False

    def on_touch_move(self, touch):
        if touch.grab_current is not self:
            return False
        ratio = (touch.x - self.x) / max(self.width, 1)
        ratio = max(0.0, min(1.0, ratio))
        if self._drag_start and ratio < self.end_ratio - 0.01:
            self.start_ratio = ratio
            if self._on_change:
                self._on_change("start", ratio)
        elif self._drag_end and ratio > self.start_ratio + 0.01:
            self.end_ratio = ratio
            if self._on_change:
                self._on_change("end", ratio)
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self:
            return False
        self._drag_start = False
        self._drag_end   = False
        touch.ungrab(self)
        return True


# ── HOME SCREEN ───────────────────────────────────────────
class HomeScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(name="home", **kwargs)
        self.app = app
        self._build()

    def _build(self):
        root = FloatLayout()

        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda o, v: setattr(self._bg, "pos", v),
                  size=lambda o, v: setattr(self._bg, "size", v))

        col = BoxLayout(orientation="vertical", spacing=dp(20),
                        padding=[dp(32), dp(60), dp(32), dp(40)],
                        size_hint=(1, 1))

        col.add_widget(Widget(size_hint_y=None, height=dp(40)))

        # Wordmark
        wm = BoxLayout(orientation="horizontal", size_hint=(1, None),
                       height=dp(64), spacing=0)
        wm.add_widget(make_label("Local", font_size=42, bold=True,
                                 color_hex="#ffffff", halign="right"))
        wm.add_widget(make_label("Clip", font_size=42, bold=True,
                                 color_hex="#f5a623", halign="left"))
        col.add_widget(wm)

        self.tagline_lbl = make_label(self.app.t("tagline"), font_size=14,
                                      color_hex="#cccccc", halign="center")
        col.add_widget(self.tagline_lbl)

        # Badges
        badges = BoxLayout(orientation="horizontal", spacing=dp(10),
                           size_hint=(1, None), height=dp(36))
        for key, c in [("lossless_badge", "#f5a623"),
                        ("offline_badge", "#60a5fa"),
                        ("free_badge", "#4ade80")]:
            badges.add_widget(make_label(self.app.t(key), font_size=11,
                                         color_hex=c, halign="center"))
        col.add_widget(badges)

        col.add_widget(Widget(size_hint_y=1))

        # Pick video button
        self.pick_btn = Button(
            text=self.app.t("pick_video"),
            font_size=sp(18), bold=True,
            color=get_color_from_hex("#0a0a0a"),
            background_normal="",
            background_color=get_color_from_hex("#f5a623"),
            size_hint=(1, None), height=dp(64))
        self.pick_btn.bind(on_release=self._pick_video)
        col.add_widget(self.pick_btn)

        col.add_widget(Widget(size_hint_y=None, height=dp(16)))

        # No-video hint
        self.hint_lbl = make_label(self.app.t("no_video"), font_size=13,
                                   color_hex="#555555", halign="center")
        col.add_widget(self.hint_lbl)

        col.add_widget(Widget(size_hint_y=1))

        # Language selector
        lang_row = BoxLayout(orientation="horizontal", spacing=dp(8),
                             size_hint=(1, None), height=dp(40))
        for code in LANG_ORDER:
            btn = Button(
                text=LANGUAGES[code]["name"],
                font_size=sp(11),
                background_normal="",
                background_color=get_color_from_hex(
                    "#f5a623" if code == self.app.lang else "#222222"),
                color=get_color_from_hex(
                    "#0a0a0a" if code == self.app.lang else "#cccccc"),
                size_hint_x=1)
            btn.bind(on_release=lambda b, c=code: self._set_lang(c))
            lang_row.add_widget(btn)
        self.lang_row = lang_row
        col.add_widget(lang_row)

        # Ko-fi credit
        col.add_widget(make_label("ko-fi.com/satdiva", font_size=10,
                                  color_hex="#333333", halign="center"))

        root.add_widget(col)
        self.add_widget(root)

    def _pick_video(self, *_):
        content = BoxLayout(orientation="vertical", spacing=dp(8),
                            padding=dp(12))
        fc = FileChooserListView(
            filters=["*.mp4", "*.mkv", "*.mov", "*.avi", "*.webm", "*.m4v"],
            path=str(Path.home()))
        content.add_widget(fc)

        btn_row = BoxLayout(size_hint_y=None, height=dp(48), spacing=dp(8))
        cancel_btn = make_btn("Cancel", bg_hex="#222222")
        select_btn = make_btn("SELECT", bg_hex="#f5a623", fg_hex="#0a0a0a")
        btn_row.add_widget(cancel_btn)
        btn_row.add_widget(select_btn)
        content.add_widget(btn_row)

        popup = Popup(title="Pick a Video", content=content,
                      size_hint=(0.95, 0.85),
                      background_color=get_color_from_hex("#111111"),
                      title_color=get_color_from_hex("#f5a623"))

        cancel_btn.bind(on_release=popup.dismiss)

        def on_select(*_):
            if fc.selection:
                popup.dismiss()
                self.app.load_video(fc.selection[0])

        select_btn.bind(on_release=on_select)
        fc.bind(on_submit=lambda *_: on_select())
        popup.open()

    def _set_lang(self, code):
        self.app.lang = code
        self.app.refresh_all_screens()

    def refresh(self):
        self.tagline_lbl.text = self.app.t("tagline")
        self.pick_btn.text    = self.app.t("pick_video")
        self.hint_lbl.text    = self.app.t("no_video")
        for i, code in enumerate(LANG_ORDER):
            btn = self.lang_row.children[len(LANG_ORDER) - 1 - i]
            btn.background_color = get_color_from_hex(
                "#f5a623" if code == self.app.lang else "#222222")
            btn.color = get_color_from_hex(
                "#0a0a0a" if code == self.app.lang else "#cccccc")


# ── TRIM SCREEN ───────────────────────────────────────────
class TrimScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(name="trim", **kwargs)
        self.app       = app
        self.duration  = 0.0
        self.start_sec = 0.0
        self.end_sec   = 0.0
        self._build()

    def _build(self):
        root = FloatLayout()

        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda o, v: setattr(self._bg, "pos", v),
                  size=lambda o, v: setattr(self._bg, "size", v))

        col = BoxLayout(orientation="vertical", spacing=dp(12),
                        padding=[dp(20), dp(24), dp(20), dp(20)],
                        size_hint=(1, 1))

        # Top bar
        top = BoxLayout(size_hint=(1, None), height=dp(48), spacing=dp(10))
        self.back_btn = make_btn(self.app.t("back"), bg_hex="#222222",
                                 font_size=20)
        self.back_btn.size_hint_x = None
        self.back_btn.width = dp(56)
        self.back_btn.bind(on_release=lambda *_: self.app.go_home())

        self.title_lbl = make_label("LocalClip", font_size=18, bold=True,
                                    color_hex="#f5a623", halign="center")
        top.add_widget(self.back_btn)
        top.add_widget(self.title_lbl)
        col.add_widget(top)

        # Filename
        self.file_lbl = make_label("", font_size=11, color_hex="#555555",
                                   halign="center")
        col.add_widget(self.file_lbl)

        # Duration info row
        dur_row = BoxLayout(size_hint=(1, None), height=dp(36), spacing=dp(16))
        self.orig_lbl = make_label("", font_size=12, color_hex="#888888",
                                   halign="center")
        self.clip_lbl = make_label("", font_size=12, color_hex="#f5a623",
                                   halign="center")
        dur_row.add_widget(self.orig_lbl)
        dur_row.add_widget(self.clip_lbl)
        col.add_widget(dur_row)

        # Trim bar
        self.trim_bar = TrimBar(on_change=self._on_trim_change,
                                size_hint=(1, None), height=dp(80))
        col.add_widget(self.trim_bar)

        # Drag hint
        self.hint_lbl = make_label(self.app.t("drag_hint"), font_size=11,
                                   color_hex="#444444", halign="center")
        col.add_widget(self.hint_lbl)

        # Time inputs
        time_row = BoxLayout(size_hint=(1, None), height=dp(56), spacing=dp(16))

        start_col = BoxLayout(orientation="vertical", spacing=dp(4))
        self.start_label = make_label(self.app.t("start"), font_size=11,
                                      color_hex="#888888", halign="center")
        self.start_input = TextInput(
            text="00:00:00", font_size=sp(16), multiline=False,
            background_color=get_color_from_hex("#1a1a1a"),
            foreground_color=get_color_from_hex("#ffffff"),
            cursor_color=get_color_from_hex("#f5a623"),
            halign="center", size_hint_y=None, height=dp(40))
        self.start_input.bind(on_text_validate=self._on_start_typed)
        start_col.add_widget(self.start_label)
        start_col.add_widget(self.start_input)

        end_col = BoxLayout(orientation="vertical", spacing=dp(4))
        self.end_label = make_label(self.app.t("end"), font_size=11,
                                    color_hex="#888888", halign="center")
        self.end_input = TextInput(
            text="00:00:00", font_size=sp(16), multiline=False,
            background_color=get_color_from_hex("#1a1a1a"),
            foreground_color=get_color_from_hex("#ffffff"),
            cursor_color=get_color_from_hex("#f5a623"),
            halign="center", size_hint_y=None, height=dp(40))
        self.end_input.bind(on_text_validate=self._on_end_typed)
        end_col.add_widget(self.end_label)
        end_col.add_widget(self.end_input)

        time_row.add_widget(start_col)
        time_row.add_widget(end_col)
        col.add_widget(time_row)

        col.add_widget(Widget(size_hint_y=1))

        # Non-destructive badge
        self.nd_lbl = make_label(self.app.t("non_dest"), font_size=10,
                                 color_hex="#333333", halign="center")
        col.add_widget(self.nd_lbl)

        # Export button
        self.export_btn = Button(
            text=self.app.t("export"),
            font_size=sp(17), bold=True,
            color=get_color_from_hex("#0a0a0a"),
            background_normal="",
            background_color=get_color_from_hex("#f5a623"),
            size_hint=(1, None), height=dp(64))
        self.export_btn.bind(on_release=self._do_export)
        col.add_widget(self.export_btn)

        # Progress bar (hidden until export)
        self.progress = ProgressBar(max=100, value=0,
                                    size_hint=(1, None), height=dp(8),
                                    opacity=0)
        col.add_widget(self.progress)

        root.add_widget(col)
        self.add_widget(root)

    def load_video(self, path):
        self.video_path = path
        self.duration   = get_video_duration(path)
        self.start_sec  = 0.0
        self.end_sec    = self.duration

        self.file_lbl.text  = Path(path).name
        self.orig_lbl.text  = f"{self.app.t('original')}: {secs_to_hms(self.duration)}"
        self._update_clip_label()

        self.trim_bar.start_ratio = 0.0
        self.trim_bar.end_ratio   = 1.0

        self.start_input.text = secs_to_hms(self.start_sec)
        self.end_input.text   = secs_to_hms(self.end_sec)

    def _update_clip_label(self):
        clip_dur = max(0, self.end_sec - self.start_sec)
        self.clip_lbl.text = f"{self.app.t('clip')}: {secs_to_hms(clip_dur)}"

    def _on_trim_change(self, handle, ratio):
        if handle == "start":
            self.start_sec        = ratio * self.duration
            self.start_input.text = secs_to_hms(self.start_sec)
        else:
            self.end_sec        = ratio * self.duration
            self.end_input.text = secs_to_hms(self.end_sec)
        self._update_clip_label()

    def _on_start_typed(self, instance):
        secs = hms_to_secs(instance.text)
        if secs is not None and 0 <= secs < self.end_sec:
            self.start_sec = secs
            if self.duration > 0:
                self.trim_bar.start_ratio = secs / self.duration
            self._update_clip_label()
        else:
            instance.text = secs_to_hms(self.start_sec)

    def _on_end_typed(self, instance):
        secs = hms_to_secs(instance.text)
        if secs is not None and secs > self.start_sec and secs <= self.duration:
            self.end_sec = secs
            if self.duration > 0:
                self.trim_bar.end_ratio = secs / self.duration
            self._update_clip_label()
        else:
            instance.text = secs_to_hms(self.end_sec)

    def _do_export(self, *_):
        if not hasattr(self, "video_path"):
            return

        self.export_btn.disabled = True
        self.export_btn.text     = self.app.t("exporting")
        self.progress.opacity    = 1
        self.progress.value      = 0

        dst = make_export_path(self.video_path, self.start_sec, self.end_sec)

        def run():
            ok = export_clip(
                self.video_path, dst,
                self.start_sec, self.end_sec,
                progress_cb=lambda line: Clock.schedule_once(
                    lambda dt: setattr(self.progress, "value",
                                       min(self.progress.value + 2, 95)), 0))
            Clock.schedule_once(lambda dt: self._export_done(ok, dst), 0)

        threading.Thread(target=run, daemon=True).start()

    def _export_done(self, ok, dst):
        self.export_btn.disabled = False
        self.export_btn.text     = self.app.t("export")
        self.progress.opacity    = 0

        if ok:
            self.app.show_done(str(dst))
        else:
            self._show_error(self.app.t("error_title"), self.app.t("no_ffmpeg"))

    def _show_error(self, title, msg):
        content = BoxLayout(orientation="vertical", padding=dp(16), spacing=dp(12))
        content.add_widget(make_label(msg, font_size=14,
                                      color_hex="#f87171", halign="center"))
        btn = make_btn("OK", bg_hex="#222222")
        content.add_widget(btn)
        p = Popup(title=title, content=content, size_hint=(0.85, 0.4),
                  background_color=get_color_from_hex("#111111"),
                  title_color=get_color_from_hex("#f87171"))
        btn.bind(on_release=p.dismiss)
        p.open()

    def refresh(self):
        self.back_btn.text   = self.app.t("back")
        self.hint_lbl.text   = self.app.t("drag_hint")
        self.start_label.text = self.app.t("start")
        self.end_label.text   = self.app.t("end")
        self.export_btn.text  = self.app.t("export")
        self.nd_lbl.text      = self.app.t("non_dest")
        if hasattr(self, "video_path"):
            self.orig_lbl.text = f"{self.app.t('original')}: {secs_to_hms(self.duration)}"
            self._update_clip_label()


# ── DONE SCREEN ───────────────────────────────────────────
class DoneScreen(Screen):
    def __init__(self, app, **kwargs):
        super().__init__(name="done", **kwargs)
        self.app = app
        self._build()

    def _build(self):
        root = FloatLayout()

        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda o, v: setattr(self._bg, "pos", v),
                  size=lambda o, v: setattr(self._bg, "size", v))

        col = BoxLayout(orientation="vertical", spacing=dp(24),
                        padding=[dp(32), dp(80), dp(32), dp(60)],
                        size_hint=(1, 1))

        # Check icon
        col.add_widget(make_label("✓", font_size=72, color_hex="#4ade80",
                                  halign="center"))

        self.title_lbl = make_label(self.app.t("done_title"), font_size=24,
                                    bold=True, color_hex="#ffffff",
                                    halign="center")
        col.add_widget(self.title_lbl)

        self.msg_lbl = make_label(self.app.t("done_msg"), font_size=14,
                                  color_hex="#cccccc", halign="center")
        col.add_widget(self.msg_lbl)

        self.path_lbl = make_label("", font_size=11, color_hex="#555555",
                                   halign="center")
        col.add_widget(self.path_lbl)

        col.add_widget(Widget(size_hint_y=1))

        self.another_btn = Button(
            text=self.app.t("export_another"),
            font_size=sp(16), bold=True,
            color=get_color_from_hex("#0a0a0a"),
            background_normal="",
            background_color=get_color_from_hex("#f5a623"),
            size_hint=(1, None), height=dp(60))
        self.another_btn.bind(on_release=lambda *_: self.app.go_home())
        col.add_widget(self.another_btn)

        # Ko-fi
        col.add_widget(make_label("Support: ko-fi.com/satdiva", font_size=10,
                                  color_hex="#333333", halign="center"))

        root.add_widget(col)
        self.add_widget(root)

    def set_path(self, path):
        self.path_lbl.text = path

    def refresh(self):
        self.title_lbl.text   = self.app.t("done_title")
        self.msg_lbl.text     = self.app.t("done_msg")
        self.another_btn.text = self.app.t("export_another")


# ── APP ───────────────────────────────────────────────────
class LocalClipApp(App):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang = "en"

    def t(self, key):
        return LANGUAGES.get(self.lang, LANGUAGES["en"]).get(key, key)

    def build(self):
        Window.clearcolor = get_color_from_hex("#0a0a0a")

        self.sm   = ScreenManager(transition=SlideTransition())
        self.home = HomeScreen(app=self)
        self.trim = TrimScreen(app=self)
        self.done = DoneScreen(app=self)

        self.sm.add_widget(self.home)
        self.sm.add_widget(self.trim)
        self.sm.add_widget(self.done)

        return self.sm

    def load_video(self, path):
        self.trim.load_video(path)
        self.sm.current = "trim"

    def go_home(self):
        self.sm.transition.direction = "right"
        self.sm.current = "home"
        self.sm.transition.direction = "left"

    def show_done(self, path):
        self.done.set_path(path)
        self.sm.current = "done"

    def refresh_all_screens(self):
        self.home.refresh()
        self.trim.refresh()
        self.done.refresh()


if __name__ == "__main__":
    LocalClipApp().run()
