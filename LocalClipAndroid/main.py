# main.py — LocalClip Android v0.3.0

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
from io import BytesIO

LOCALES = {
    'en': {'select': "SELECT FOOTAGE", 'load': "LOAD", 'in': "SET IN", 'out': "SET OUT",
           'save': "SAVE LOSSLESS CLIP", 'saving': "Saving...", 'close': "CLOSE",
           'exit': "EXIT", 'err_time': "Check IN / OUT", 'no_file': "No file",
           'saved': "SAVED"},
    'es': {'select': "SELECCIONAR", 'load': "CARGAR", 'in': "INICIO", 'out': "FIN",
           'save': "GUARDAR SIN PÉRDIDA", 'saving': "Guardando...", 'close': "CERRAR",
           'exit': "SALIR", 'err_time': "Ver IN/OUT", 'no_file': "Sin archivo",
           'saved': "GUARDADO"},
    'fr': {'select': "SÉLECTIONNER", 'load': "CHARGER", 'in': "DÉBUT", 'out': "FIN",
           'save': "SANS PERTE", 'saving': "Enregistrement...", 'close': "FERMER",
           'exit': "QUITTER", 'err_time': "Vérifier IN/OUT", 'no_file': "Aucun fichier",
           'saved': "ENREGISTRÉ"},
    'pt': {'select': "SELECIONAR", 'load': "CARREGAR", 'in': "INÍCIO", 'out': "FIM",
           'save': "SALVAR SEM PERDA", 'saving': "Salvando...", 'close': "FECHAR",
           'exit': "SAIR", 'err_time': "Ver IN/OUT", 'no_file': "Sem arquivo",
           'saved': "SALVO"},
    'ar': {'select': "اختر الفيديو", 'load': "تحميل", 'in': "بداية", 'out': "نهاية",
           'save': "حفظ بدون فقدان", 'saving': "جاري الحفظ...", 'close': "إغلاق",
           'exit': "خروج", 'err_time': "تحقق", 'no_file': "لا يوجد ملف",
           'saved': "تم الحفظ"},
    'zh': {'select': "选择素材", 'load': "加载", 'in': "入点", 'out': "出点",
           'save': "无损保存", 'saving': "保存中...", 'close': "关闭",
           'exit': "退出", 'err_time': "检查IN/OUT", 'no_file': "未选择",
           'saved': "已保存"},
    'hi': {'select': "फुटेज चुनें", 'load': "लोड", 'in': "शुरुआत", 'out': "अंत",
           'save': "लॉसलेस सहेजें", 'saving': "सहेज रहा है...", 'close': "बंद",
           'exit': "बाहर", 'err_time': "जांचें", 'no_file': "कोई फ़ाइल नहीं",
           'saved': "सहेजा गया"},
}

try:
    import locale
    L = LOCALES.get(locale.getdefaultlocale()[0][:2], LOCALES['en'])
except Exception:
    L = LOCALES['en']

if platform == 'android':
    from android.permissions import request_permissions, Permission
    from android.storage import primary_external_storage_path

KOFI_URL = "https://ko-fi.com/1satdiva"
D = (0.12, 0.12, 0.12, 1)
M = (0.22, 0.22, 0.22, 1)
W = (1, 1, 1, 1)


def B(text, sh, ph, bg=M, bold=False, fs='13sp'):
    return Button(text=text, size_hint=sh, pos_hint=ph,
                  background_color=bg, background_normal='',
                  color=W, bold=bold, font_size=fs)


def get_ffmpeg():
    if platform == 'android':
        app_dir = os.path.dirname(os.path.abspath(__file__))
        priv = os.environ.get('ANDROID_PRIVATE', '')
        for p in [
            os.path.join(app_dir, 'bin', 'ffmpeg'),
            os.path.join(app_dir, 'ffmpeg'),
            os.path.join(priv, 'bin', 'ffmpeg') if priv else '',
            os.path.join(priv, 'ffmpeg') if priv else '',
            '/data/data/org.satdiva.localclip/files/app/bin/ffmpeg',
            '/data/data/org.satdiva.localclip/files/app/ffmpeg',
            '/data/user/0/org.satdiva.localclip/files/app/bin/ffmpeg',
            '/data/user/0/org.satdiva.localclip/files/app/ffmpeg',
        ]:
            if p and os.path.isfile(p):
                try: os.chmod(p, 0o755)
                except: pass
                return p
        return 'ffmpeg'
    return 'ffmpeg'


def get_duration_ms(path):
    if platform == 'android':
        try:
            from jnius import autoclass
            R = autoclass('android.media.MediaMetadataRetriever')
            r = R()
            r.setDataSource(path)
            val = r.extractMetadata(R.METADATA_KEY_DURATION)
            r.release()
            return int(val) if val else 0
        except: return 0
    return 0


def get_frame(path, ms):
    if platform != 'android':
        return None
    try:
        from jnius import autoclass
        R = autoclass('android.media.MediaMetadataRetriever')
        r = R()
        r.setDataSource(path)
        bmp = r.getFrameAtTime(int(ms) * 1000, 2)
        r.release()
        if bmp is None: return None
        BAOS = autoclass('java.io.ByteArrayOutputStream')
        CF = autoclass('android.graphics.Bitmap$CompressFormat')
        baos = BAOS()
        bmp.compress(CF.JPEG, 80, baos)
        buf = BytesIO(bytes(bytearray(baos.toByteArray())))
        baos.close()
        return buf
    except: return None


def open_kofi():
    try:
        if platform == 'android':
            from jnius import autoclass
            I = autoclass('android.content.Intent')
            U = autoclass('android.net.Uri')
            PA = autoclass('org.kivy.android.PythonActivity')
            PA.mActivity.startActivity(I(I.ACTION_VIEW, U.parse(KOFI_URL)))
        else:
            import webbrowser; webbrowser.open(KOFI_URL)
    except: pass


def fmt(ms):
    s = ms / 1000.0
    m, sec = divmod(s, 60)
    return f"{int(m):02d}:{sec:06.3f}"


def get_splash():
    d = os.path.dirname(os.path.abspath(__file__))
    p = os.path.join(d, 'splash-screen.png')
    return p if os.path.isfile(p) else 'splash-screen.png'


def launch_count():
    p = os.path.join(os.path.dirname(os.path.abspath(__file__)), '.lc')
    try:
        c = int(open(p).read().strip()) + 1
    except: c = 1
    try: open(p, 'w').write(str(c))
    except: pass
    return c


class MainScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        l = FloatLayout()
        l.add_widget(Image(source=get_splash(), allow_stretch=True,
                           keep_ratio=False, size_hint=(1,1),
                           pos_hint={'x':0,'y':0}))
        b = B(L['select'], (.85,.09), {'center_x':.5,'center_y':.2},
              bg=M, bold=True, fs='17sp')
        b.bind(on_release=self.pick)
        l.add_widget(b)
        e = B(L['exit'], (.4,.07), {'center_x':.5,'center_y':.09}, bg=D, fs='14sp')
        e.bind(on_release=lambda x: App.get_running_app().stop())
        l.add_widget(e)
        k = B("Ko-fi", (.2,.055), {'right':.98,'y':.01}, bg=D, fs='12sp')
        k.bind(on_release=lambda x: self._kofi())
        l.add_widget(k)
        self.add_widget(l)

    def on_enter(self):
        if launch_count() % 5 == 0:
            Clock.schedule_once(lambda dt: self._kofi(), 1.5)

    def _kofi(self):
        c = FloatLayout()
        c.add_widget(Label(text="LocalClip is free.\nA coffee keeps it alive.",
                           pos_hint={'center_x':.5,'center_y':.65},
                           font_size='15sp', halign='center', color=W))
        g = B("ko-fi.com/1satdiva", (.85,.2), {'center_x':.5,'center_y':.38}, bg=M, bold=True)
        cl = B("Maybe later", (.85,.15), {'center_x':.5,'center_y':.15}, bg=D)
        c.add_widget(g); c.add_widget(cl)
        p = Popup(title="Support LocalClip", content=c, size_hint=(.85,.4))
        g.bind(on_release=lambda x: [open_kofi(), p.dismiss()])
        cl.bind(on_release=p.dismiss)
        p.open()

    def pick(self, *a):
        if platform == 'android':
            request_permissions([Permission.READ_EXTERNAL_STORAGE,
                                  Permission.WRITE_EXTERNAL_STORAGE,
                                  "android.permission.READ_MEDIA_VIDEO"])
            start = primary_external_storage_path()
        else:
            start = os.path.expanduser("~")
        c = FloatLayout()
        fc = FileChooserListView(path=start,
                                 filters=['*.mp4','*.mov','*.MP4','*.MOV'],
                                 size_hint=(1,.85), pos_hint={'y':.15})
        lb = B(L['load'], (.9,.1), {'center_x':.5,'y':.02}, bg=M, bold=True)
        c.add_widget(fc); c.add_widget(lb)
        pop = Popup(title="LocalClip", content=c, size_hint=(.95,.9))
        def load(*a):
            if fc.selection:
                path = fc.selection[0].replace('file://','')
                pop.dismiss()
                self.manager.get_screen('editor').load_video(path)
                self.manager.current = 'editor'
        lb.bind(on_release=load)
        pop.open()


class EditorScreen(Screen):
    def __init__(self, **kw):
        super().__init__(**kw)
        self.video_path = ''
        self.pos_ms = 0
        self.dur_ms = 0
        self.in_ms = 0
        self.out_ms = 0
        self._pending = 0
        self._fetching = False
        self._build()

    def _build(self):
        l = FloatLayout()
        self.img = Image(source=get_splash(), allow_stretch=True,
                         keep_ratio=True, size_hint=(1,.42),
                         pos_hint={'center_x':.5,'top':1})
        l.add_widget(self.img)
        self.tc = Label(text="00:00.000", font_size='42sp', bold=True,
                        color=W, pos_hint={'center_x':.5,'center_y':.535})
        l.add_widget(self.tc)
        self.dur_lbl = Label(text="", font_size='12sp', color=(.5,.5,.5,1),
                             pos_hint={'center_x':.5,'center_y':.488})
        l.add_widget(self.dur_lbl)
        self.prog = ProgressBar(max=1000, value=0, size_hint=(.94,.015),
                                pos_hint={'center_x':.5,'center_y':.458})
        l.add_widget(self.prog)
        for i,(t,v) in enumerate([("-60s",-60000),("-30s",-30000),("-10s",-10000),
                                   ("+10s",10000),("+30s",30000),("+60s",60000)]):
            b = B(t,(.148,.052),{'x':.018+i*.164,'center_y':.418},bg=D,fs='12sp')
            b.bind(on_release=lambda x,v=v: self._seek(v))
            l.add_widget(b)
        for i,(t,v) in enumerate([("-3s",-3000),("-1s",-1000),("+1s",1000),("+3s",3000)]):
            b = B(t,(.22,.052),{'x':.018+i*.245,'center_y':.358},bg=M,bold=True,fs='13sp')
            b.bind(on_release=lambda x,v=v: self._seek(v))
            l.add_widget(b)
        for i,(t,v) in enumerate([("-200",-200),("-50",-50),("+50",50),("+200",200)]):
            b = B(t,(.22,.052),{'x':.018+i*.245,'center_y':.298},bg=D,fs='12sp')
            b.bind(on_release=lambda x,v=v: self._seek(v))
            l.add_widget(b)
        self.in_btn = B(L['in'],(.47,.062),{'x':.018,'center_y':.234},bg=M,bold=True,fs='14sp')
        self.out_btn = B(L['out'],(.47,.062),{'right':.982,'center_y':.234},bg=M,bold=True,fs='14sp')
        self.in_btn.bind(on_release=self.set_in)
        self.out_btn.bind(on_release=self.set_out)
        l.add_widget(self.in_btn); l.add_widget(self.out_btn)
        self.range_lbl = Label(text="IN --:--   OUT --:--", font_size='12sp',
                               color=(.6,.6,.6,1), pos_hint={'center_x':.5,'center_y':.178})
        l.add_widget(self.range_lbl)
        sv = B(L['save'],(.96,.062),{'center_x':.5,'center_y':.118},bg=M,bold=True,fs='15sp')
        sv.bind(on_release=self.save_clip)
        l.add_widget(sv)
        self.sv_lbl = Label(text="", font_size='15sp', bold=True, color=W,
                            pos_hint={'center_x':.5,'center_y':.058}, halign='center')
        l.add_widget(self.sv_lbl)
        cl = B(L['close'],(.75,.052),{'x':.018,'center_y':.018},bg=D,fs='13sp')
        cl.bind(on_release=lambda x: setattr(self.manager,'current','main'))
        l.add_widget(cl)
        kf = B("Ko-fi",(.18,.052),{'right':.982,'center_y':.018},bg=D,fs='12sp')
        kf.bind(on_release=lambda x: open_kofi())
        l.add_widget(kf)
        self.add_widget(l)

    def load_video(self, path):
        self.video_path = path
        self.pos_ms = 0; self.in_ms = 0; self.out_ms = 0
        self.in_btn.text = L['in']; self.out_btn.text = L['out']
        self.range_lbl.text = "IN --:--   OUT --:--"
        self.sv_lbl.text = f"Loading {os.path.basename(path)}"
        self.tc.text = "00:00.000"
        def _load():
            dur = get_duration_ms(path)
            Clock.schedule_once(lambda dt: self._loaded(dur))
        threading.Thread(target=_load, daemon=True).start()

    def _loaded(self, dur):
        self.dur_ms = dur
        self.out_ms = dur
        self.prog.max = max(dur, 1)
        self.dur_lbl.text = f"Duration: {fmt(dur)}"
        self.sv_lbl.text = ""
        self._fetch(0)

    def _seek(self, delta):
        self.pos_ms = max(0, min(self.dur_ms, self.pos_ms + delta))
        self.tc.text = fmt(self.pos_ms)
        self.prog.value = self.pos_ms
        self._pending = self.pos_ms
        if not self._fetching:
            self._fetch(self.pos_ms)

    def _fetch(self, ms):
        self._fetching = True
        def run():
            buf = get_frame(self.video_path, ms)
            Clock.schedule_once(lambda dt: self._show(buf, ms))
        threading.Thread(target=run, daemon=True).start()

    def _show(self, buf, fetched_ms):
        self._fetching = False
        if buf:
            try:
                buf.seek(0)
                self.img.texture = CoreImage(buf, ext='jpg').texture
            except: pass
        if self._pending != fetched_ms:
            self._fetch(self._pending)

    def set_in(self, *a):
        self.in_ms = self.pos_ms
        self.in_btn.text = fmt(self.in_ms)
        self._update_range()

    def set_out(self, *a):
        self.out_ms = self.pos_ms
        self.out_btn.text = fmt(self.out_ms)
        self._update_range()

    def _update_range(self):
        dur = (self.out_ms - self.in_ms) / 1000.0
        if dur > 0:
            m, s = divmod(dur, 60)
            self.range_lbl.text = f"IN {fmt(self.in_ms)}   OUT {fmt(self.out_ms)}   {int(m):02d}:{s:05.2f}"
        else:
            self.range_lbl.text = f"IN {fmt(self.in_ms)}   OUT {fmt(self.out_ms)}"

    def save_clip(self, *a):
        if self.out_ms <= self.in_ms:
            self.sv_lbl.text = L['err_time']; return
        if not self.video_path:
            self.sv_lbl.text = L['no_file']; return
        base = primary_external_storage_path() if platform == 'android' else os.path.expanduser("~")
        out_dir = os.path.join(base, "Movies", "LocalClip_Exports")
        os.makedirs(out_dir, exist_ok=True)
        out_file = os.path.join(out_dir, f"clip_{int(time.time())}.mp4")
        self.sv_lbl.text = L['saving']
        def run():
            ff = get_ffmpeg()
            cmd = [ff, '-y',
                   '-ss', f'{self.in_ms/1000:.3f}',
                   '-i', self.video_path,
                   '-t', f'{(self.out_ms-self.in_ms)/1000:.3f}',
                   '-c', 'copy',
                   '-avoid_negative_ts', 'make_zero',
                   '-movflags', '+faststart',
                   out_file]
            try:
                r = subprocess.run(cmd, capture_output=True, text=True, timeout=180)
                if r.returncode == 0:
                    msg = f"{L['saved']}\n{os.path.basename(out_file)}"
                else:
                    msg = f"ERROR: {r.stderr[-150:] if r.stderr else 'none'}"
            except FileNotFoundError:
                msg = f"ffmpeg not found\n{get_ffmpeg()}"
            except subprocess.TimeoutExpired:
                msg = "Timeout"
            except Exception as e:
                msg = str(e)[:120]
            Clock.schedule_once(lambda dt: setattr(self.sv_lbl, 'text', msg))
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