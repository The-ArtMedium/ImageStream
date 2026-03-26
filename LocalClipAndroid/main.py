import os
import threading
import subprocess
import shutil
from pathlib import Path

from kivy.app import App
from kivy.uix.screenmanager import ScreenManager, Screen, SlideTransition
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.floatlayout import FloatLayout
from kivy.uix.label import Label
from kivy.uix.button import Button
from kivy.uix.widget import Widget
from kivy.graphics import Color, Rectangle, Line
from kivy.metrics import dp, sp
from kivy.utils import get_color_from_hex, platform
from kivy.clock import Clock
from kivy.properties import NumericProperty, StringProperty

# Android-specific imports for the "Sovereign" storage model
if platform == 'android':
    from android.storage import primary_external_storage_path
    from android.permissions import request_permissions, Permission

# ── PALETTE ──────────────────────────────────────────────
BG      = get_color_from_hex("#0a0a0a")
ACCENT  = get_color_from_hex("#f5a623")
TEXT    = get_color_from_hex("#ffffff")

# ── TRANSLATIONS ─────────────────────────────────────────
LANGUAGES = {
    "en": {"name": "English", "tagline": "Trim videos. Lossless. Offline.", "pick_video": "PICK VIDEO", "export": "✓ EXPORT CLIP", "done_msg": "Saved to Movies/LocalClip_Exports"},
    "es": {"name": "Español", "tagline": "Recorta videos. Sin pérdida. Sin internet.", "pick_video": "ELEGIR VIDEO", "export": "✓ EXPORTAR CLIP", "done_msg": "Guardado en Movies/LocalClip_Exports"},
    "fr": {"name": "Français", "tagline": "Coupez des vidéos. Sans perte. Hors ligne.", "pick_video": "CHOISIR VIDÉO", "export": "✓ EXPORTER", "done_msg": "Sauvegardé dans Movies/LocalClip_Exports"},
    "pt": {"name": "Português", "tagline": "Corte vídeos. Sem perdas. Offline.", "pick_video": "ESCOLHER VÍDEO", "export": "✓ EXPORTAR CLIP", "done_msg": "Salvo em Movies/LocalClip_Exports"},
    "ar": {"name": "العربية", "tagline": "قص الفيديو. بدون فقدان. بدون إنترنت.", "pick_video": "اختر فيديو", "export": "✓ تصدير", "done_msg": "محفوظ في Movies/LocalClip_Exports"},
    "zh": {"name": "中文", "tagline": "剪辑视频。无损向。离线。", "pick_video": "选择视频", "export": "✓ 导出片段", "done_msg": "已保存到 Movies/LocalClip_Exports"},
    "hi": {"name": "हिन्दी", "tagline": "वीडियो ट्रिम करें। बिना नुकसान। ऑफलाइन।", "pick_video": "वीडियो चुनें", "export": "✓ क्लिप निर्यात करें", "done_msg": "Movies/LocalClip_Exports में सहेजा"},
}

LANG_ORDER = ["en", "es", "fr", "pt", "ar", "zh", "hi"]

# ── MOBILE-READY HELPERS ──────────────────────────────────
def get_ffmpeg_path():
    """Locates the bundled ffmpeg binary on Android or Desktop."""
    if platform == 'android':
        # Buildozer with ffmpeg recipe usually places it here
        potential_path = os.path.join(os.environ.get('PYTHONPATH', ''), 'bin', 'ffmpeg')
        return potential_path if os.path.exists(potential_path) else "ffmpeg"
    return shutil.which("ffmpeg") or "ffmpeg"

def export_clip(src, dst, start_sec, end_sec, progress_cb=None):
    """Lossless export using stream copy (No re-encoding)."""
    ffmpeg_bin = get_ffmpeg_path()
    duration = end_sec - start_sec
    # The 'copy' codec is what makes this 'Lossless' and 'Grid-Independent'
    cmd = [
        ffmpeg_bin, "-y", "-ss", str(start_sec), "-i", str(src),
        "-t", str(duration), "-c", "copy", "-avoid_negative_ts", "make_zero", str(dst)
    ]
    try:
        proc = subprocess.Popen(cmd, stderr=subprocess.PIPE, universal_newlines=True)
        if progress_cb:
            for line in proc.stderr:
                progress_cb(line)
        proc.wait()
        return proc.returncode == 0
    except Exception as e:
        print(f"Export Error: {e}")
        return False

def make_export_path(src_path, start_sec, end_sec):
    """Determines where to save the file based on the OS."""
    src = Path(src_path)
    if platform == 'android':
        # Uses the public Movies folder so the user can actually find it
        base_path = Path(primary_external_storage_path()) / "Movies" / "LocalClip_Exports"
    else:
        base_path = src.parent / "LocalClip_Exports"
    
    base_path.mkdir(parents=True, exist_ok=True)
    name = f"{src.stem}_{int(start_sec)}s-{int(end_sec)}s{src.suffix}"
    return base_path / name

# ── CORE UI ──────────────────────────────────────────────
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
        
        col = BoxLayout(orientation="vertical", spacing=dp(25), padding=dp(40))
        
        # Wordmark
        wm = BoxLayout(size_hint=(1, None), height=dp(80), spacing=dp(5))
        wm.add_widget(Label(text="Local", font_size=sp(42), bold=True, halign="right"))
        wm.add_widget(Label(text="Clip", font_size=sp(42), bold=True, color=ACCENT, halign="left"))
        col.add_widget(wm)

        col.add_widget(Label(text=self.app.t("tagline"), color=(0.8, 0.8, 0.8, 1), font_size=sp(16)))
        
        # Spacer
        col.add_widget(Widget(size_hint_y=1))

        # Main Action
        pick_btn = Button(
            text=self.app.t("pick_video"), 
            size_hint=(1, None), 
            height=dp(70), 
            background_color=ACCENT,
            background_normal='',
            color=(0,0,0,1),
            bold=True,
            font_size=sp(18)
        )
        col.add_widget(pick_btn)
        
        # Ko-fi / Support Hint
        col.add_widget(Label(text="ko-fi.com/satdiva", font_size=sp(12), color=(0.3, 0.3, 0.3, 1)))

        root.add_widget(col)
        self.add_widget(root)

class LocalClipApp(App):
    lang = StringProperty("en")
    
    def build(self):
        # Requesting permissions at startup for "Zero-Hurdle" experience
        if platform == 'android':
            request_permissions([
                Permission.READ_EXTERNAL_STORAGE, 
                Permission.WRITE_EXTERNAL_STORAGE,
                Permission.READ_MEDIA_VIDEO
            ])
        
        self.sm = ScreenManager(transition=SlideTransition())
        self.sm.add_widget(HomeScreen(self))
        return self.sm

    def t(self, key):
        """Translation helper"""
        return LANGUAGES[self.lang].get(key, key)

if __name__ == "__main__":
    LocalClipApp().run()
