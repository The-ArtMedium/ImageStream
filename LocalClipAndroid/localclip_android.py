
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
BG       = get_color_from_hex("#0a0a0a")
BG2      = get_color_from_hex("#111111")
BG3      = get_color_from_hex("#1a1a1a")
BG4      = get_color_from_hex("#222222")
ACCENT   = get_color_from_hex("#f5a623")
ACCENT2  = get_color_from_hex("#e8941a")
GREEN    = get_color_from_hex("#4ade80")
GREEN2   = get_color_from_hex("#166534")
RED      = get_color_from_hex("#f87171")
RED2     = get_color_from_hex("#7f1d1d")
BLUE     = get_color_from_hex("#60a5fa")
TEXT     = get_color_from_hex("#ffffff")
TEXT2    = get_color_from_hex("#cccccc")
TEXT3    = get_color_from_hex("#888888")

# ── TRANSLATIONS ─────────────────────────────────────────
LANGUAGES = {
    "en": {
        "name": "English", "dir": "ltr",
        "app_title":       "LocalClip",
        "tagline":         "Trim videos. Lossless. Offline.",
        "pick_video":      "PICK VIDEO",
        "no_video":        "Tap to select a video from your device",
        "trim":            "TRIM",
        "start":           "START",
        "end":             "END",
        "duration":        "Duration",
        "preview":         "▶  PREVIEW",
        "export":          "✓  EXPORT CLIP",
        "exporting":       "Exporting…",
        "done_title":      "Clip Saved",
        "done_msg":        "Saved to LocalClip_Exports/\nOriginal untouched.",
        "error_title":     "Error",
        "no_ffmpeg":       "ffmpeg not found.\nInstall ffmpeg to export clips.",
        "original":        "Original",
        "clip":            "Clip",
        "non_dest":        "Non-destructive · Original never modified",
        "drag_hint":       "Drag handles to trim · or type exact time below",
        "language":        "Language",
        "back":            "←",
        "open_exports":    "OPEN EXPORTS FOLDER",
        "export_another":  "TRIM ANOTHER",
        "time_format":     "HH:MM:SS",
        "lossless_badge":  "LOSSLESS",
        "offline_badge":   "OFFLINE",
        "free_badge":      "FREE",
    },
    "es": {
        "name": "Español", "dir": "ltr",
        "app_title":       "LocalClip",
        "tagline":         "Recorta videos. Sin pérdida. Sin internet.",
        "pick_video":      "ELEGIR VIDEO",
        "no_video":        "Toca para seleccionar un video",
        "trim":            "RECORTAR",
        "start":           "INICIO",
        "end":             "FIN",
        "duration":        "Duración",
        "preview":         "▶  VISTA PREVIA",
        "export":          "✓  EXPORTAR CLIP",
        "exporting":       "Exportando…",
        "done_title":      "Clip Guardado",
        "done_msg":        "Guardado en LocalClip_Exports/\nOriginal sin cambios.",
        "error_title":     "Error",
        "no_ffmpeg":       "ffmpeg no encontrado.",
        "original":        "Original",
        "clip":            "Clip",
        "non_dest":        "No destructivo · Original nunca modificado",
        "drag_hint":       "Arrastra los puntos · o escribe el tiempo exacto",
        "language":        "Idioma",
        "back":            "←",
        "open_exports":    "ABRIR CARPETA",
        "export_another":  "RECORTAR OTRO",
        "time_format":     "HH:MM:SS",
        "lossless_badge":  "SIN PÉRDIDA",
        "offline_badge":   "SIN INTERNET",
        "free_badge":      "GRATIS",
    },
    "fr": {
        "name": "Français", "dir": "ltr",
        "app_title":       "LocalClip",
        "tagline":         "Coupez des vidéos. Sans perte. Hors ligne.",
        "pick_video":      "CHOISIR VIDÉO",
        "no_video":        "Appuyez pour sélectionner une vidéo",
        "trim":            "COUPER",
        "start":           "DÉBUT",
        "end":             "FIN",
        "duration":        "Durée",
        "preview":         "▶  APERÇU",
        "export":          "✓  EXPORTER",
        "exporting":       "Export en cours…",
        "done_title":      "Clip Sauvegardé",
        "done_msg":        "Sauvegardé dans LocalClip_Exports/\nOriginal intact.",
        "error_title":     "Erreur",
        "no_ffmpeg":       "ffmpeg introuvable.",
        "original":        "Original",
        "clip":            "Clip",
        "non_dest":        "Non destructif · Original jamais modifié",
        "drag_hint":       "Faites glisser les poignées · ou saisissez le temps exact",
        "language":        "Langue",
        "back":            "←",
        "open_exports":    "OUVRIR DOSSIER",
        "export_another":  "COUPER UN AUTRE",
        "time_format":     "HH:MM:SS",
        "lossless_badge":  "SANS PERTE",
        "offline_badge":   "HORS LIGNE",
        "free_badge":      "GRATUIT",
    },
    "pt": {
        "name": "Português", "dir": "ltr",
        "app_title":       "LocalClip",
        "tagline":         "Corte vídeos. Sem perdas. Offline.",
        "pick_video":      "ESCOLHER VÍDEO",
        "no_video":        "Toque para selecionar um vídeo",
        "trim":            "CORTAR",
        "start":           "INÍCIO",
        "end":             "FIM",
        "duration":        "Duração",
        "preview":         "▶  PRÉ-VISUALIZAR",
        "export":          "✓  EXPORTAR CLIP",
        "exporting":       "Exportando…",
        "done_title":      "Clip Salvo",
        "done_msg":        "Salvo em LocalClip_Exports/\nOriginal intocado.",
        "error_title":     "Erro",
        "no_ffmpeg":       "ffmpeg não encontrado.",
        "original":        "Original",
        "clip":            "Clip",
        "non_dest":        "Não destrutivo · Original nunca modificado",
        "drag_hint":       "Arraste os pontos · ou digite o tempo exato",
        "language":        "Idioma",
        "back":            "←",
        "open_exports":    "ABRIR PASTA",
        "export_another":  "CORTAR OUTRO",
        "time_format":     "HH:MM:SS",
        "lossless_badge":  "SEM PERDAS",
        "offline_badge":   "OFFLINE",
        "free_badge":      "GRÁTIS",
    },
    "ar": {
        "name": "العربية", "dir": "rtl",
        "app_title":       "LocalClip",
        "tagline":         "قص الفيديو. بدون فقدان. بدون إنترنت.",
        "pick_video":      "اختر فيديو",
        "no_video":        "انقر لاختيار فيديو من جهازك",
        "trim":            "قص",
        "start":           "البداية",
        "end":             "النهاية",
        "duration":        "المدة",
        "preview":         "▶  معاينة",
        "export":          "✓  تصدير",
        "exporting":       "جارٍ التصدير…",
        "done_title":      "تم حفظ الكليب",
        "done_msg":        "محفوظ في LocalClip_Exports/\nالأصل لم يُمَس.",
        "error_title":     "خطأ",
        "no_ffmpeg":       "ffmpeg غير موجود.",
        "original":        "الأصلي",
        "clip":            "كليب",
        "non_dest":        "غير تدميري · الأصل لم يُعدَّل",
        "drag_hint":       "اسحب النقاط · أو اكتب الوقت الدقيق",
        "language":        "اللغة",
        "back":            "→",
        "open_exports":    "فتح مجلد التصدير",
        "export_another":  "قص فيديو آخر",
        "time_format":     "HH:MM:SS",
        "lossless_badge":  "بدون فقدان",
        "offline_badge":   "بدون إنترنت",
        "free_badge":      "مجاني",
    },
    "zh": {
        "name": "中文", "dir": "ltr",
        "app_title":       "LocalClip",
        "tagline":         "剪辑视频。无损。离线。",
        "pick_video":      "选择视频",
        "no_video":        "点击从设备选择视频",
        "trim":            "剪辑",
        "start":           "开始",
        "end":             "结束",
        "duration":        "时长",
        "preview":         "▶  预览",
        "export":          "✓  导出片段",
        "exporting":       "导出中…",
        "done_title":      "片段已保存",
        "done_msg":        "已保存到 LocalClip_Exports/\n原始文件未修改。",
        "error_title":     "错误",
        "no_ffmpeg":       "未找到 ffmpeg。",
        "original":        "原始",
        "clip":            "片段",
        "non_dest":        "非破坏性 · 原始文件从不修改",
        "drag_hint":       "拖动手柄修剪 · 或输入精确时间",
        "language":        "语言",
        "back":            "←",
        "open_exports":    "打开导出文件夹",
        "export_another":  "剪辑另一个",
        "time_format":     "HH:MM:SS",
        "lossless_badge":  "无损",
        "offline_badge":   "离线",
        "free_badge":      "免费",
    },
    "hi": {
        "name": "हिन्दी", "dir": "ltr",
        "app_title":       "LocalClip",
        "tagline":         "वीडियो ट्रिम करें। बिना नुकसान। ऑफलाइन।",
        "pick_video":      "वीडियो चुनें",
        "no_video":        "वीडियो चुनने के लिए टैप करें",
        "trim":            "ट्रिम",
        "start":           "शुरू",
        "end":             "अंत",
        "duration":        "अवधि",
        "preview":         "▶  पूर्वावलोकन",
        "export":          "✓  क्लिप निर्यात करें",
        "exporting":       "निर्यात हो रहा है…",
        "done_title":      "क्लिप सहेजा",
        "done_msg":        "LocalClip_Exports/ में सहेजा\nमूल अछूता।",
        "error_title":     "त्रुटि",
        "no_ffmpeg":       "ffmpeg नहीं मिला।",
        "original":        "मूल",
        "clip":            "क्लिप",
        "non_dest":        "गैर-विनाशकारी · मूल कभी संशोधित नहीं",
        "drag_hint":       "हैंडल खींचें · या सटीक समय टाइप करें",
        "language":        "भाषा",
        "back":            "←",
        "open_exports":    "निर्यात फ़ोल्डर खोलें",
        "export_another":  "दूसरा ट्रिम करें",
        "time_format":     "HH:MM:SS",
        "lossless_badge":  "बिना नुकसान",
        "offline_badge":   "ऑफलाइन",
        "free_badge":      "मुफ़्त",
    },
}

LANG_ORDER = ["en", "es", "fr", "pt", "ar", "zh", "hi"]

# ── HELPERS ───────────────────────────────────────────────
def secs_to_hms(secs):
    """Convert seconds to HH:MM:SS string."""
    secs  = max(0, int(secs))
    h     = secs // 3600
    m     = (secs % 3600) // 60
    s     = secs % 60
    return f"{h:02d}:{m:02d}:{s:02d}"

def hms_to_secs(hms):
    """Convert HH:MM:SS string to seconds. Returns None if invalid."""
    try:
        parts = hms.strip().split(":")
        if len(parts) == 3:
            return int(parts[0])*3600 + int(parts[1])*60 + int(parts[2])
        elif len(parts) == 2:
            return int(parts[0])*60 + int(parts[1])
        else:
            return float(hms)
    except Exception:
        return None

def get_video_duration(path):
    """Get video duration in seconds using ffprobe."""
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
    """
    Lossless export using ffmpeg stream copy.
    -c copy — no re-encoding, no quality loss, no compression.
    """
    import subprocess
    duration = end_sec - start_sec
    cmd = [
        "ffmpeg", "-y",
        "-ss", str(start_sec),
        "-i", str(src),
        "-t",  str(duration),
        "-c",  "copy",          # LOSSLESS — stream copy, no re-encode
        "-avoid_negative_ts", "make_zero",
        str(dst)
    ]
    proc = subprocess.Popen(cmd,
        stderr=subprocess.PIPE,
        universal_newlines=True)
    for line in proc.stderr:
        if progress_cb:
            progress_cb(line)
    proc.wait()
    return proc.returncode == 0

def make_export_path(src_path, start_sec, end_sec):
    """Build output path in LocalClip_Exports/ next to source file."""
    src   = Path(src_path)
    out   = src.parent / "LocalClip_Exports"
    out.mkdir(exist_ok=True)
    name  = f"{src.stem}_{int(start_sec)}s-{int(end_sec)}s{src.suffix}"
    return out / name

# ── STYLED WIDGETS ────────────────────────────────────────
def make_btn(text, bg_hex="#222222", fg_hex="#ffffff",
             font_size=16, bold=True, radius=10):
    btn = Button(
        text=text,
        font_size=sp(font_size),
        bold=bold,
        color=get_color_from_hex(fg_hex),
        background_normal="",
        background_color=get_color_from_hex(bg_hex),
    )
    return btn

def make_label(text, font_size=14, color_hex="#cccccc",
               bold=False, halign="left"):
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

# ── TRIM BAR WIDGET ───────────────────────────────────────
class TrimBar(Widget):
    """
    Custom touch widget — a timeline bar with two draggable handles.
    Left handle = start point (orange)
    Right handle = end point (orange)
    Selected region highlighted in amber.
    """
    start_ratio = NumericProperty(0.0)   # 0.0 – 1.0
    end_ratio   = NumericProperty(1.0)   # 0.0 – 1.0

    HANDLE_W = dp(22)
    TRACK_H  = dp(10)

    def __init__(self, on_change=None, **kwargs):
        super().__init__(**kwargs)
        self._on_change    = on_change
        self._drag_start   = False
        self._drag_end     = False
        self.bind(pos=self._redraw, size=self._redraw,
                  start_ratio=self._redraw, end_ratio=self._redraw)

    def _redraw(self, *_):
        self.canvas.clear()
        x, y  = self.x, self.y
        w, h  = self.width, self.height
        cy    = y + h / 2

        sx = x + self.start_ratio * w
        ex = x + self.end_ratio   * w

        with self.canvas:
            # Track background
            Color(*get_color_from_hex("#2a2a2a"))
            Rectangle(pos=(x, cy - self.TRACK_H/2),
                      size=(w, self.TRACK_H))

            # Selected region
            Color(*get_color_from_hex("#f5a623"), 0.5)
            Rectangle(pos=(sx, cy - self.TRACK_H/2),
                      size=(ex - sx, self.TRACK_H))

            # Start handle
            Color(*get_color_from_hex("#f5a623"))
            Rectangle(pos=(sx - self.HANDLE_W/2, cy - dp(20)),
                      size=(self.HANDLE_W, dp(40)))

            # End handle
            Color(*get_color_from_hex("#f5a623"))
            Rectangle(pos=(ex - self.HANDLE_W/2, cy - dp(20)),
                      size=(self.HANDLE_W, dp(40)))

            # Handle lines
            Color(*get_color_from_hex("#0a0a0a"))
            for hx in [sx, ex]:
                for dy in [-dp(6), 0, dp(6)]:
                    Line(points=[hx - dp(3), cy + dy,
                                 hx + dp(3), cy + dy],
                         width=dp(1.5))

    def on_touch_down(self, touch):
        if not self.collide_point(*touch.pos): return False
        cx  = self.x
        w   = self.width
        sx  = cx + self.start_ratio * w
        ex  = cx + self.end_ratio   * w
        tx  = touch.x
        if abs(tx - sx) < dp(30):
            self._drag_start = True
            touch.grab(self)
            return True
        if abs(tx - ex) < dp(30):
            self._drag_end = True
            touch.grab(self)
            return True
        return False

    def on_touch_move(self, touch):
        if touch.grab_current is not self: return False
        ratio = (touch.x - self.x) / max(self.width, 1)
        ratio = max(0.0, min(1.0, ratio))
        if self._drag_start:
            if ratio < self.end_ratio - 0.01:
                self.start_ratio = ratio
                if self._on_change:
                    self._on_change("start", ratio)
        elif self._drag_end:
            if ratio > self.start_ratio + 0.01:
                self.end_ratio = ratio
                if self._on_change:
                    self._on_change("end", ratio)
        return True

    def on_touch_up(self, touch):
        if touch.grab_current is not self: return False
        self._drag_start = False
        self._drag_end   = False
        touch.ungrab(self)
        return True

# ── SCREENS ───────────────────────────────────────────────

class HomeScreen(Screen):
    """
    Opening screen.
    Wordmark, tagline, Pick Video button, language selector.
    """
    def __init__(self, app, **kwargs):
        super().__init__(name="home", **kwargs)
        self.app = app
        self._build()

    def _build(self):
        root = FloatLayout()

        # Background
        with root.canvas.before:
            Color(*BG)
            self._bg_rect = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda o,v: setattr(self._bg_rect, "pos", v),
                  size=lambda o,v: setattr(self._bg_rect, "size", v))

        # Center column
        col = BoxLayout(orientation="vertical",
                        spacing=dp(20),
                        padding=[dp(32), dp(60), dp(32), dp(40)],
                        size_hint=(1, 1))

        col.add_widget(Widget(size_hint_y=None, height=dp(40)))

        # Wordmark
        wm = BoxLayout(orientation="horizontal",
                       size_hint=(1, None), height=dp(64),
                       spacing=0)
        wm.add_widget(make_label("Local", font_size=42, bold=True,
                                  color_hex="#ffffff", halign="right"))
        wm.add_widget(make_label("Clip",  font_size=42, bold=True,
                                  color_hex="#f5a623", halign="left"))
        col.add_widget(wm)

        # Tagline
        self.tagline_lbl = make_label(
            self.app.t("tagline"), font_size=14,
            color_hex="#cccccc", halign="center")
        col.add_widget(self.tagline_lbl)

        # Badges row
        badges = BoxLayout(orientation="horizontal",
                           spacing=dp(10), size_hint=(1, None),
                           height=dp(36))
        for key, col_hex in [
            ("lossless_badge", "#f5a623"),
            ("offline_badge",  "#60a5fa"),
            ("free_badge",     "#4ade80"),
        ]:
            lbl = make_label(self.app.t(key), font_size=11,
                              color_hex=col_hex, halign="center")
            badges.add_widget(lbl)
        col.add_widget(badges)

        col.add_widget(Widget(size_hint_y=1))

        # Pick video button
        self.pick_btn = Button(
            text=self.app.t("pick_video"),
            font_size=sp(18), bold=True,
            color=get_color_from_hex("#0a0a0a"),
            background_normal="",
            background_color=get_color_from_hex("#f5a623"),
            size_hint=(1, None), height=dp(72),
        )
        self.pick_btn.bind(on_release=self.app.pick_video)
        col.add_widget(self.pick_btn)

        # Non-destructive note
        self.nd_lbl = make_label(
            self.app.t("non_dest"), font_size=11,
            color_hex="#888888", halign="center")
        col.add_widget(self.nd_lbl)

        col.add_widget(Widget(size_hint_y=None, height=dp(20)))

        # Language selector row
        lang_row = BoxLayout(orientation="horizontal",
                             spacing=dp(8),
                             size_hint=(1, None), height=dp(44))
        lang_row.add_widget(make_label(self.app.t("language"),
                                        font_size=12,
                                        color_hex="#888888"))
        for code in LANG_ORDER:
            btn = Button(
                text=LANGUAGES[code]["name"],
                font_size=sp(11),
                color=get_color_from_hex("#f5a623" if code == self.app.lang_code
                                          else "#888888"),
                background_normal="",
                background_color=get_color_from_hex(
                    "#1e1e1e" if code == self.app.lang_code else "#111111"),
                size_hint=(None, 1),
                width=dp(56),
            )
            btn.bind(on_release=lambda b, c=code: self.app.set_language(c))
            lang_row.add_widget(btn)
        col.add_widget(lang_row)

        root.add_widget(col)
        self.add_widget(root)

    def refresh(self):
        self.clear_widgets()
        self._build()


class TrimScreen(Screen):
    """
    Main trim screen.
    Video info, timeline bar with drag handles,
    manual time inputs, preview and export.
    """
    def __init__(self, app, **kwargs):
        super().__init__(name="trim", **kwargs)
        self.app        = app
        self.duration   = 0.0
        self.start_sec  = 0.0
        self.end_sec    = 0.0
        self._player    = None
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical",
                         spacing=0,
                         padding=0)

        # ── TOPBAR ──
        topbar = BoxLayout(orientation="horizontal",
                           size_hint=(1, None), height=dp(56),
                           padding=[dp(12), dp(8), dp(12), dp(8)],
                           spacing=dp(12))
        with topbar.canvas.before:
            Color(*BG2)
            self._tb_rect = Rectangle(pos=topbar.pos, size=topbar.size)
        topbar.bind(pos=lambda o,v: setattr(self._tb_rect,"pos",v),
                    size=lambda o,v: setattr(self._tb_rect,"size",v))

        self.back_btn = Button(
            text=self.app.t("back"),
            font_size=sp(20), bold=True,
            color=get_color_from_hex("#f5a623"),
            background_normal="", background_color=(0,0,0,0),
            size_hint=(None, 1), width=dp(48))
        self.back_btn.bind(on_release=lambda _: self.app.go_home())
        topbar.add_widget(self.back_btn)

        self.title_lbl = make_label("Local[color=#f5a623]Clip[/color]",
                                     font_size=18, bold=True,
                                     color_hex="#ffffff")
        self.title_lbl.markup = True
        topbar.add_widget(self.title_lbl)

        root.add_widget(topbar)

        # ── VIDEO INFO ──
        info_box = BoxLayout(orientation="vertical",
                             size_hint=(1, None), height=dp(80),
                             padding=[dp(20), dp(12), dp(20), dp(8)],
                             spacing=dp(4))
        with info_box.canvas.before:
            Color(*BG3)
            self._info_rect = Rectangle(pos=info_box.pos, size=info_box.size)
        info_box.bind(pos=lambda o,v: setattr(self._info_rect,"pos",v),
                      size=lambda o,v: setattr(self._info_rect,"size",v))

        self.filename_lbl = make_label("", font_size=13, bold=True,
                                        color_hex="#ffffff")
        info_box.add_widget(self.filename_lbl)

        self.duration_lbl = make_label("", font_size=11,
                                        color_hex="#888888")
        info_box.add_widget(self.duration_lbl)
        root.add_widget(info_box)

        # ── PREVIEW AREA ──
        self.preview_area = BoxLayout(
            orientation="vertical",
            size_hint=(1, 1),
            padding=[dp(20), dp(16), dp(20), dp(16)])
        with self.preview_area.canvas.before:
            Color(*BG)
            self._prev_rect = Rectangle(pos=self.preview_area.pos,
                                         size=self.preview_area.size)
        self.preview_area.bind(
            pos=lambda o,v: setattr(self._prev_rect,"pos",v),
            size=lambda o,v: setattr(self._prev_rect,"size",v))

        # Placeholder when no preview
        self.prev_placeholder = make_label(
            "▶", font_size=48,
            color_hex="#2a2a2a", halign="center")
        self.preview_area.add_widget(self.prev_placeholder)
        root.add_widget(self.preview_area)

        # ── TRIM BAR ──
        trim_section = BoxLayout(orientation="vertical",
                                  size_hint=(1, None), height=dp(160),
                                  padding=[dp(20), dp(12), dp(20), dp(12)],
                                  spacing=dp(10))
        with trim_section.canvas.before:
            Color(*BG2)
            self._trim_rect = Rectangle(pos=trim_section.pos,
                                         size=trim_section.size)
        trim_section.bind(
            pos=lambda o,v: setattr(self._trim_rect,"pos",v),
            size=lambda o,v: setattr(self._trim_rect,"size",v))

        self.drag_hint = make_label(self.app.t("drag_hint"),
                                     font_size=11,
                                     color_hex="#888888",
                                     halign="center")
        trim_section.add_widget(self.drag_hint)

        self.trim_bar = TrimBar(on_change=self._on_handle_drag,
                                 size_hint=(1, None), height=dp(60))
        trim_section.add_widget(self.trim_bar)

        # Time display row
        time_row = BoxLayout(orientation="horizontal",
                             size_hint=(1, None), height=dp(28),
                             spacing=dp(8))
        self.start_time_lbl = make_label("00:00:00", font_size=13,
                                          color_hex="#f5a623",
                                          bold=True, halign="left")
        time_row.add_widget(self.start_time_lbl)

        self.clip_dur_lbl = make_label("", font_size=11,
                                        color_hex="#888888",
                                        halign="center")
        time_row.add_widget(self.clip_dur_lbl)

        self.end_time_lbl = make_label("00:00:00", font_size=13,
                                        color_hex="#f5a623",
                                        bold=True, halign="right")
        time_row.add_widget(self.end_time_lbl)
        trim_section.add_widget(time_row)
        root.add_widget(trim_section)

        # ── MANUAL TIME INPUT ──
        manual = BoxLayout(orientation="horizontal",
                           size_hint=(1, None), height=dp(64),
                           padding=[dp(20), dp(8), dp(20), dp(8)],
                           spacing=dp(12))
        with manual.canvas.before:
            Color(*BG3)
            self._man_rect = Rectangle(pos=manual.pos, size=manual.size)
        manual.bind(pos=lambda o,v: setattr(self._man_rect,"pos",v),
                    size=lambda o,v: setattr(self._man_rect,"size",v))

        # Start input
        start_col = BoxLayout(orientation="vertical", spacing=dp(2))
        start_col.add_widget(make_label(self.app.t("start"),
                                         font_size=10,
                                         color_hex="#888888"))
        self.start_input = TextInput(
            text="00:00:00",
            font_size=sp(14),
            foreground_color=get_color_from_hex("#ffffff"),
            background_color=get_color_from_hex("#1e1e1e"),
            cursor_color=get_color_from_hex("#f5a623"),
            multiline=False,
            size_hint=(1, None), height=dp(40),
            padding=[dp(8), dp(8)])
        self.start_input.bind(on_text_validate=self._on_start_input)
        self.start_input.bind(focus=self._on_input_focus)
        start_col.add_widget(self.start_input)
        manual.add_widget(start_col)

        # End input
        end_col = BoxLayout(orientation="vertical", spacing=dp(2))
        end_col.add_widget(make_label(self.app.t("end"),
                                       font_size=10,
                                       color_hex="#888888"))
        self.end_input = TextInput(
            text="00:00:00",
            font_size=sp(14),
            foreground_color=get_color_from_hex("#ffffff"),
            background_color=get_color_from_hex("#1e1e1e"),
            cursor_color=get_color_from_hex("#f5a623"),
            multiline=False,
            size_hint=(1, None), height=dp(40),
            padding=[dp(8), dp(8)])
        self.end_input.bind(on_text_validate=self._on_end_input)
        self.end_input.bind(focus=self._on_input_focus)
        end_col.add_widget(self.end_input)
        manual.add_widget(end_col)
        root.add_widget(manual)

        # ── BUTTONS ──
        btn_row = BoxLayout(orientation="horizontal",
                            size_hint=(1, None), height=dp(72),
                            padding=[dp(20), dp(8), dp(20), dp(8)],
                            spacing=dp(12))
        with btn_row.canvas.before:
            Color(*BG)
            self._btn_rect = Rectangle(pos=btn_row.pos, size=btn_row.size)
        btn_row.bind(pos=lambda o,v: setattr(self._btn_rect,"pos",v),
                     size=lambda o,v: setattr(self._btn_rect,"size",v))

        self.preview_btn = Button(
            text=self.app.t("preview"),
            font_size=sp(14), bold=True,
            color=get_color_from_hex("#60a5fa"),
            background_normal="",
            background_color=get_color_from_hex("#1a2a3a"),
            size_hint=(0.4, 1))
        self.preview_btn.bind(on_release=self._do_preview)
        btn_row.add_widget(self.preview_btn)

        self.export_btn = Button(
            text=self.app.t("export"),
            font_size=sp(16), bold=True,
            color=get_color_from_hex("#0a0a0a"),
            background_normal="",
            background_color=get_color_from_hex("#f5a623"),
            size_hint=(0.6, 1))
        self.export_btn.bind(on_release=self._do_export)
        btn_row.add_widget(self.export_btn)
        root.add_widget(btn_row)

        self.add_widget(root)

    def load_video(self, path):
        """Called when a video is selected."""
        self.video_path = path
        self.duration   = get_video_duration(path)
        self.start_sec  = 0.0
        self.end_sec    = self.duration

        # Update UI
        self.filename_lbl.text  = Path(path).name
        self.duration_lbl.text  = (f"{self.app.t('duration')}: "
                                    f"{secs_to_hms(self.duration)}")
        self.trim_bar.start_ratio = 0.0
        self.trim_bar.end_ratio   = 1.0
        self._update_time_display()

    def _on_handle_drag(self, handle, ratio):
        if handle == "start":
            self.start_sec = ratio * self.duration
            self.start_input.text = secs_to_hms(self.start_sec)
        else:
            self.end_sec = ratio * self.duration
            self.end_input.text = secs_to_hms(self.end_sec)
        self._update_time_display()

    def _on_start_input(self, instance):
        secs = hms_to_secs(instance.text)
        if secs is not None and 0 <= secs < self.end_sec:
            self.start_sec = secs
            self.trim_bar.start_ratio = secs / max(self.duration, 1)
            self._update_time_display()

    def _on_end_input(self, instance):
        secs = hms_to_secs(instance.text)
        if secs is not None and secs > self.start_sec:
            self.end_sec = min(secs, self.duration)
            self.trim_bar.end_ratio = self.end_sec / max(self.duration, 1)
            self._update_time_display()

    def _on_input_focus(self, instance, focused):
        if not focused:
            if instance == self.start_input:
                self._on_start_input(instance)
            else:
                self._on_end_input(instance)

    def _update_time_display(self):
        self.start_time_lbl.text = secs_to_hms(self.start_sec)
        self.end_time_lbl.text   = secs_to_hms(self.end_sec)
        clip_dur = max(0, self.end_sec - self.start_sec)
        self.clip_dur_lbl.text   = (f"↔ {secs_to_hms(clip_dur)}")
        self.start_input.text    = secs_to_hms(self.start_sec)
        self.end_input.text      = secs_to_hms(self.end_sec)

    def _do_preview(self, *_):
        """Jump video preview to start point."""
        if not PREVIEW_AVAILABLE:
            return
        # Seek existing player or open new
        if self._player:
            self._player.seek(self.start_sec, relative=False)
        # Full preview integration requires kivy video widget
        # — handled in the app layer

    def _do_export(self, *_):
        """Start lossless export in background thread."""
        self.export_btn.disabled = True
        self.export_btn.text     = self.app.t("exporting")

        def _run():
            dst     = make_export_path(self.video_path,
                                        self.start_sec,
                                        self.end_sec)
            success = export_clip(self.video_path, dst,
                                   self.start_sec, self.end_sec)
            Clock.schedule_once(lambda dt: self._export_done(success, dst))

        threading.Thread(target=_run, daemon=True).start()

    def _export_done(self, success, dst):
        self.export_btn.disabled = False
        self.export_btn.text     = self.app.t("export")
        if success:
            self.app.show_done(dst)
        else:
            self._show_error()

    def _show_error(self):
        popup = Popup(
            title=self.app.t("error_title"),
            content=make_label(self.app.t("no_ffmpeg"),
                                font_size=13,
                                color_hex="#f87171",
                                halign="center"),
            size_hint=(0.8, 0.3))
        popup.open()

    def refresh_labels(self):
        self.drag_hint.text    = self.app.t("drag_hint")
        self.preview_btn.text  = self.app.t("preview")
        self.export_btn.text   = self.app.t("export")
        self.back_btn.text     = self.app.t("back")


class DoneScreen(Screen):
    """
    Export success screen.
    Shows output path, Open Exports, Trim Another.
    """
    def __init__(self, app, **kwargs):
        super().__init__(name="done", **kwargs)
        self.app  = app
        self._dst = ""
        self._build()

    def _build(self):
        root = BoxLayout(orientation="vertical",
                         spacing=dp(20),
                         padding=[dp(32), dp(60), dp(32), dp(40)])
        with root.canvas.before:
            Color(*BG)
            self._bg = Rectangle(pos=root.pos, size=root.size)
        root.bind(pos=lambda o,v: setattr(self._bg,"pos",v),
                  size=lambda o,v: setattr(self._bg,"size",v))

        root.add_widget(Widget(size_hint_y=1))

        # Success icon
        root.add_widget(make_label("✓", font_size=72,
                                    color_hex="#4ade80",
                                    halign="center"))

        self.done_title = make_label(self.app.t("done_title"),
                                      font_size=22, bold=True,
                                      color_hex="#ffffff",
                                      halign="center")
        root.add_widget(self.done_title)

        self.done_msg = make_label(self.app.t("done_msg"),
                                    font_size=13,
                                    color_hex="#cccccc",
                                    halign="center")
        root.add_widget(self.done_msg)

        self.path_lbl = make_label("", font_size=11,
                                    color_hex="#888888",
                                    halign="center")
        root.add_widget(self.path_lbl)

        root.add_widget(Widget(size_hint_y=1))

        self.trim_another_btn = Button(
            text=self.app.t("export_another"),
            font_size=sp(16), bold=True,
            color=get_color_from_hex("#0a0a0a"),
            background_normal="",
            background_color=get_color_from_hex("#f5a623"),
            size_hint=(1, None), height=dp(64))
        self.trim_another_btn.bind(on_release=lambda _: self.app.go_home())
        root.add_widget(self.trim_another_btn)

        root.add_widget(Widget(size_hint_y=None, height=dp(20)))

        self.add_widget(root)

    def set_dst(self, dst):
        self._dst = str(dst)
        self.path_lbl.text = self._dst

    def refresh_labels(self):
        self.done_title.text       = self.app.t("done_title")
        self.done_msg.text         = self.app.t("done_msg")
        self.trim_another_btn.text = self.app.t("export_another")


# ══════════════════════════════════════════════════════════
# APP
# ══════════════════════════════════════════════════════════
class LocalClipApp(App):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.lang_code = "en"
        self.T         = LANGUAGES["en"]

    def t(self, key, *args):
        val = self.T.get(key, LANGUAGES["en"].get(key, key))
        return val.format(*args) if args else val

    def set_language(self, code):
        if code not in LANGUAGES: return
        self.lang_code = code
        self.T         = LANGUAGES[code]
        self._home.refresh()
        self._trim.refresh_labels()
        self._done.refresh_labels()

    def build(self):
        Window.clearcolor = get_color_from_hex("#0a0a0a")

        self.sm    = ScreenManager(transition=SlideTransition())
        self._home = HomeScreen(app=self)
        self._trim = TrimScreen(app=self)
        self._done = DoneScreen(app=self)

        self.sm.add_widget(self._home)
        self.sm.add_widget(self._trim)
        self.sm.add_widget(self._done)

        return self.sm

    def pick_video(self, *_):
        """Open file chooser for video selection."""
        content = BoxLayout(orientation="vertical", spacing=dp(10),
                             padding=dp(10))
        fc = FileChooserListView(
            filters=["*.mp4","*.mov","*.avi","*.mkv",
                     "*.webm","*.m4v","*.3gp","*.flv"],
            path=self._default_path())
        content.add_widget(fc)

        btn_row = BoxLayout(size_hint=(1,None), height=dp(48),
                             spacing=dp(10))
        cancel = Button(text="Cancel",
                         background_normal="",
                         background_color=get_color_from_hex("#222222"),
                         color=get_color_from_hex("#cccccc"),
                         font_size=sp(14))
        select = Button(text="Select",
                         background_normal="",
                         background_color=get_color_from_hex("#f5a623"),
                         color=get_color_from_hex("#0a0a0a"),
                         font_size=sp(14), bold=True)
        btn_row.add_widget(cancel)
        btn_row.add_widget(select)
        content.add_widget(btn_row)

        popup = Popup(title="Select Video",
                       content=content,
                       size_hint=(0.95, 0.85))

        cancel.bind(on_release=popup.dismiss)
        select.bind(on_release=lambda _: self._on_video_selected(
            fc.selection, popup))
        popup.open()

    def _default_path(self):
        """Best default folder for videos on Android."""
        for p in ["/sdcard/DCIM", "/sdcard/Movies",
                  "/sdcard/Download", "/sdcard"]:
            if os.path.exists(p):
                return p
        return "/"

    def _on_video_selected(self, selection, popup):
        if not selection: return
        path = selection[0]
        popup.dismiss()
        self._trim.load_video(path)
        self.sm.current = "trim"

    def go_home(self):
        self.sm.transition.direction = "right"
        self.sm.current = "home"

    def show_done(self, dst):
        self._done.set_dst(dst)
        self.sm.transition.direction = "left"
        self.sm.current = "done"


if __name__ == "__main__":
    LocalClipApp().run()
