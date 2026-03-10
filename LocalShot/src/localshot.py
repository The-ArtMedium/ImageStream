"""
LocalShot — Image Editor for Everyone
Part of the ImageStream Local Suite by The Art Medium
Simple. Offline. Private. Yours.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
import numpy as np
import os
import glob

# ─── LANGUAGES ───────────────────────────────────────────────────────────────

LANGUAGES = {
    "English": {
        "title": "LocalShot — Image Editor",
        "open": "Open Image",
        "open_folder": "Open Folder",
        "save": "Save / Export",
        "crop": "Crop",
        "resize": "Resize",
        "rotate_l": "Rotate Left",
        "rotate_r": "Rotate Right",
        "flip_h": "Flip Horizontal",
        "flip_v": "Flip Vertical",
        "brightness": "Brightness",
        "contrast": "Contrast",
        "exposure": "Exposure",
        "whites": "Whites",
        "blacks": "Blacks",
        "white_balance": "White Balance",
        "temperature": "Temperature",
        "tint": "Tint",
        "sharpening": "Sharpening",
        "dehaze": "Dehaze",
        "reset": "Reset All",
        "open_prompt": "Open an image or folder to get started",
        "saved": "Image saved!",
        "error": "Error",
        "width": "Width",
        "height": "Height",
        "apply": "Apply",
        "cancel": "Cancel",
        "resize_title": "Resize Image",
        "simple_mode": "Simple",
        "advanced_mode": "Advanced",
        "language": "Language",
        "basic": "BASIC",
        "tone": "TONE",
        "color": "COLOR",
        "detail": "DETAIL",
        "transform": "TRANSFORM",
        "no_folder": "No folder open",
    },
    "Español": {
        "title": "LocalShot — Editor de Imágenes",
        "open": "Abrir Imagen",
        "open_folder": "Abrir Carpeta",
        "save": "Guardar / Exportar",
        "crop": "Recortar",
        "resize": "Redimensionar",
        "rotate_l": "Girar Izquierda",
        "rotate_r": "Girar Derecha",
        "flip_h": "Voltear Horizontal",
        "flip_v": "Voltear Vertical",
        "brightness": "Brillo",
        "contrast": "Contraste",
        "exposure": "Exposición",
        "whites": "Blancos",
        "blacks": "Negros",
        "white_balance": "Balance de Blancos",
        "temperature": "Temperatura",
        "tint": "Tono",
        "sharpening": "Nitidez",
        "dehaze": "Eliminar Neblina",
        "reset": "Restablecer",
        "open_prompt": "Abre una imagen o carpeta para comenzar",
        "saved": "¡Guardado!",
        "error": "Error",
        "width": "Ancho",
        "height": "Alto",
        "apply": "Aplicar",
        "cancel": "Cancelar",
        "resize_title": "Redimensionar",
        "simple_mode": "Simple",
        "advanced_mode": "Avanzado",
        "language": "Idioma",
        "basic": "BÁSICO",
        "tone": "TONO",
        "color": "COLOR",
        "detail": "DETALLE",
        "transform": "TRANSFORMAR",
        "no_folder": "Sin carpeta",
    },
    "Français": {
        "title": "LocalShot — Éditeur d'Images",
        "open": "Ouvrir Image",
        "open_folder": "Ouvrir Dossier",
        "save": "Enregistrer",
        "crop": "Rogner",
        "resize": "Redimensionner",
        "rotate_l": "Rotation Gauche",
        "rotate_r": "Rotation Droite",
        "flip_h": "Miroir H",
        "flip_v": "Miroir V",
        "brightness": "Luminosité",
        "contrast": "Contraste",
        "exposure": "Exposition",
        "whites": "Blancs",
        "blacks": "Noirs",
        "white_balance": "Balance des Blancs",
        "temperature": "Température",
        "tint": "Teinte",
        "sharpening": "Netteté",
        "dehaze": "Antibrume",
        "reset": "Réinitialiser",
        "open_prompt": "Ouvrez une image ou un dossier",
        "saved": "Enregistré!",
        "error": "Erreur",
        "width": "Largeur",
        "height": "Hauteur",
        "apply": "Appliquer",
        "cancel": "Annuler",
        "resize_title": "Redimensionner",
        "simple_mode": "Simple",
        "advanced_mode": "Avancé",
        "language": "Langue",
        "basic": "BASE",
        "tone": "TON",
        "color": "COULEUR",
        "detail": "DÉTAIL",
        "transform": "TRANSFORMER",
        "no_folder": "Aucun dossier",
    },
    "Português": {
        "title": "LocalShot — Editor de Imagens",
        "open": "Abrir Imagem",
        "open_folder": "Abrir Pasta",
        "save": "Guardar",
        "crop": "Cortar",
        "resize": "Redimensionar",
        "rotate_l": "Rodar Esquerda",
        "rotate_r": "Rodar Direita",
        "flip_h": "Inverter H",
        "flip_v": "Inverter V",
        "brightness": "Brilho",
        "contrast": "Contraste",
        "exposure": "Exposição",
        "whites": "Brancos",
        "blacks": "Pretos",
        "white_balance": "Balanço de Brancos",
        "temperature": "Temperatura",
        "tint": "Matiz",
        "sharpening": "Nitidez",
        "dehaze": "Remover Neblina",
        "reset": "Repor",
        "open_prompt": "Abre uma imagem ou pasta",
        "saved": "Guardado!",
        "error": "Erro",
        "width": "Largura",
        "height": "Altura",
        "apply": "Aplicar",
        "cancel": "Cancelar",
        "resize_title": "Redimensionar",
        "simple_mode": "Simples",
        "advanced_mode": "Avançado",
        "language": "Idioma",
        "basic": "BÁSICO",
        "tone": "TOM",
        "color": "COR",
        "detail": "DETALHE",
        "transform": "TRANSFORMAR",
        "no_folder": "Sem pasta",
    },
    "العربية": {
        "title": "LocalShot — محرر الصور",
        "open": "فتح صورة",
        "open_folder": "فتح مجلد",
        "save": "حفظ",
        "crop": "قص",
        "resize": "تغيير الحجم",
        "rotate_l": "تدوير يسار",
        "rotate_r": "تدوير يمين",
        "flip_h": "قلب أفقي",
        "flip_v": "قلب عمودي",
        "brightness": "السطوع",
        "contrast": "التباين",
        "exposure": "التعرض",
        "whites": "الإضاءات",
        "blacks": "الظلال",
        "white_balance": "توازن اللون الأبيض",
        "temperature": "درجة الحرارة",
        "tint": "الصبغة",
        "sharpening": "الحدة",
        "dehaze": "إزالة الضباب",
        "reset": "إعادة تعيين",
        "open_prompt": "افتح صورة أو مجلدًا للبدء",
        "saved": "تم الحفظ!",
        "error": "خطأ",
        "width": "العرض",
        "height": "الارتفاع",
        "apply": "تطبيق",
        "cancel": "إلغاء",
        "resize_title": "تغيير الحجم",
        "simple_mode": "بسيط",
        "advanced_mode": "متقدم",
        "language": "اللغة",
        "basic": "أساسي",
        "tone": "النغمة",
        "color": "اللون",
        "detail": "التفاصيل",
        "transform": "تحويل",
        "no_folder": "لا يوجد مجلد",
    },
    "中文": {
        "title": "LocalShot — 图像编辑器",
        "open": "打开图像",
        "open_folder": "打开文件夹",
        "save": "保存",
        "crop": "裁剪",
        "resize": "调整大小",
        "rotate_l": "向左旋转",
        "rotate_r": "向右旋转",
        "flip_h": "水平翻转",
        "flip_v": "垂直翻转",
        "brightness": "亮度",
        "contrast": "对比度",
        "exposure": "曝光",
        "whites": "高光",
        "blacks": "阴影",
        "white_balance": "白平衡",
        "temperature": "色温",
        "tint": "色调",
        "sharpening": "锐化",
        "dehaze": "去雾",
        "reset": "重置",
        "open_prompt": "打开图像或文件夹以开始",
        "saved": "已保存！",
        "error": "错误",
        "width": "宽度",
        "height": "高度",
        "apply": "应用",
        "cancel": "取消",
        "resize_title": "调整大小",
        "simple_mode": "简单",
        "advanced_mode": "高级",
        "language": "语言",
        "basic": "基本",
        "tone": "色调",
        "color": "颜色",
        "detail": "细节",
        "transform": "变换",
        "no_folder": "未打开文件夹",
    },
    "हिन्दी": {
        "title": "LocalShot — छवि संपादक",
        "open": "छवि खोलें",
        "open_folder": "फ़ोल्डर खोलें",
        "save": "सहेजें",
        "crop": "क्रॉप",
        "resize": "आकार बदलें",
        "rotate_l": "बाएं घुमाएं",
        "rotate_r": "दाएं घुमाएं",
        "flip_h": "क्षैतिज पलटें",
        "flip_v": "लंबवत पलटें",
        "brightness": "चमक",
        "contrast": "कंट्रास्ट",
        "exposure": "एक्सपोज़र",
        "whites": "सफ़ेद",
        "blacks": "काला",
        "white_balance": "सफेद संतुलन",
        "temperature": "तापमान",
        "tint": "टिंट",
        "sharpening": "तीक्ष्णता",
        "dehaze": "धुंध हटाएं",
        "reset": "रीसेट",
        "open_prompt": "शुरू करने के लिए छवि या फ़ोल्डर खोलें",
        "saved": "सहेजा गया!",
        "error": "त्रुटि",
        "width": "चौड़ाई",
        "height": "ऊंचाई",
        "apply": "लागू करें",
        "cancel": "रद्द करें",
        "resize_title": "आकार बदलें",
        "simple_mode": "सरल",
        "advanced_mode": "उन्नत",
        "language": "भाषा",
        "basic": "बुनियादी",
        "tone": "टोन",
        "color": "रंग",
        "detail": "विवरण",
        "transform": "रूपांतरण",
        "no_folder": "कोई फ़ोल्डर नहीं",
    },
}

# ─── COLORS ───────────────────────────────────────────────────────────────────

C = {
    "bg":       "#141414",
    "bg2":      "#1e1e1e",
    "bg3":      "#282828",
    "bg4":      "#323232",
    "accent":   "#f5a623",
    "accent2":  "#ffb940",
    "text":     "#f0f0f0",
    "text2":    "#999999",
    "text3":    "#555555",
    "border":   "#333333",
    "success":  "#52b788",
    "danger":   "#e05252",
    "blue":     "#5b9cf6",
    "section":  "#f5a62322",
}

THUMB_W, THUMB_H = 90, 68
IMG_EXTENSIONS = ("*.jpg","*.jpeg","*.png","*.webp","*.bmp","*.tiff","*.tif","*.JPG","*.JPEG","*.PNG")


# ─── HELPER: IMAGE PROCESSING ────────────────────────────────────────────────

def apply_white_balance(img, temperature, tint):
    """Temperature: -100 (cool/blue) to +100 (warm/orange). Tint: -100 (green) to +100 (magenta)."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    arr = np.array(img, dtype=np.float32)
    # Temperature affects R and B channels
    r_shift = temperature * 0.5
    b_shift = -temperature * 0.5
    # Tint affects G channel
    g_shift = -tint * 0.3
    arr[:,:,0] = np.clip(arr[:,:,0] + r_shift, 0, 255)
    arr[:,:,1] = np.clip(arr[:,:,1] + g_shift, 0, 255)
    arr[:,:,2] = np.clip(arr[:,:,2] + b_shift, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def apply_whites_blacks(img, whites, blacks):
    """Whites: boost highlights. Blacks: crush shadows."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    arr = np.array(img, dtype=np.float32)
    # Whites: lift the top end
    w_factor = 1.0 + whites / 100.0
    # Blacks: crush the bottom end
    b_factor = 1.0 + blacks / 200.0
    # Apply: scale around midpoint for whites, offset for blacks
    arr = arr * w_factor
    arr = np.where(arr < 128, arr * b_factor, arr)
    arr = np.clip(arr, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def apply_dehaze(img, strength):
    """Simple dehazing using contrast enhancement + slight saturation boost."""
    if strength == 0:
        return img
    if img.mode != "RGB":
        img = img.convert("RGB")
    factor = 1.0 + strength / 50.0
    img = ImageEnhance.Contrast(img).enhance(factor)
    img = ImageEnhance.Color(img).enhance(1.0 + strength / 100.0)
    return img

def apply_sharpening(img, strength):
    if strength == 0:
        return img
    if img.mode not in ["RGB", "L"]:
        img = img.convert("RGB")
    for _ in range(max(1, int(strength / 30))):
        img = img.filter(ImageFilter.SHARPEN)
    return img


# ─── MAIN APP ─────────────────────────────────────────────────────────────────

class LocalShot:
    def __init__(self, root):
        self.root = root
        self.lang = "English"
        self.t = LANGUAGES[self.lang]
        self.advanced = False

        self.image_path = None
        self.original_image = None
        self.current_image = None
        self.photo_image = None
        self.folder_images = []
        self.thumb_images = []

        self._cropping = False
        self.crop_start = None
        self.crop_rect = None

        # Adjustment vars
        self.brightness_var  = tk.DoubleVar(value=1.0)
        self.contrast_var    = tk.DoubleVar(value=1.0)
        self.exposure_var    = tk.DoubleVar(value=0.0)
        self.whites_var      = tk.DoubleVar(value=0.0)
        self.blacks_var      = tk.DoubleVar(value=0.0)
        self.temperature_var = tk.DoubleVar(value=0.0)
        self.tint_var        = tk.DoubleVar(value=0.0)
        self.sharpening_var  = tk.DoubleVar(value=0.0)
        self.dehaze_var      = tk.DoubleVar(value=0.0)

        self._setup_window()
        self._build_ui()

    def _setup_window(self):
        self.root.title(self.t["title"])
        self.root.configure(bg=C["bg"])
        self.root.geometry("1280x800")
        self.root.minsize(900, 600)

    # ─── UI BUILD ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_topbar()
        self._build_body()
        self._build_statusbar()

    def _build_topbar(self):
        bar = tk.Frame(self.root, bg=C["bg2"], height=52)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="📸 LocalShot",
                 bg=C["bg2"], fg=C["accent"],
                 font=("Helvetica", 15, "bold")).pack(side=tk.LEFT, padx=20)

        # Open folder
        self._topbtn(bar, "📁 " + self.t["open_folder"], self.open_folder, C["bg3"]).pack(side=tk.LEFT, padx=4, pady=8)
        # Open image
        self._topbtn(bar, "🖼 " + self.t["open"], self.open_image, C["bg3"]).pack(side=tk.LEFT, padx=4, pady=8)
        # Save
        self._topbtn(bar, "💾 " + self.t["save"], self.save_image, C["success"]).pack(side=tk.LEFT, padx=4, pady=8)

        # Right
        right = tk.Frame(bar, bg=C["bg2"])
        right.pack(side=tk.RIGHT, padx=16)

        # Language
        self.lang_var = tk.StringVar(value=self.lang)
        lang_cb = ttk.Combobox(right, textvariable=self.lang_var,
                                values=list(LANGUAGES.keys()),
                                width=9, state="readonly")
        lang_cb.pack(side=tk.LEFT, padx=(0,12))
        lang_cb.bind("<<ComboboxSelected>>", self._change_language)

        # Mode toggle
        self.mode_btn = tk.Button(right,
                                   text="⚙ " + self.t["advanced_mode"],
                                   bg=C["bg4"], fg=C["text"],
                                   font=("Helvetica", 11),
                                   relief=tk.FLAT, cursor="hand2",
                                   padx=12, pady=4,
                                   command=self._toggle_mode)
        self.mode_btn.pack(side=tk.LEFT)

    def _topbtn(self, parent, text, cmd, bg):
        return tk.Button(parent, text=text, bg=bg, fg=C["text"],
                         font=("Helvetica", 11), relief=tk.FLAT,
                         cursor="hand2", padx=12, pady=4, command=cmd)

    def _build_body(self):
        self.body = tk.Frame(self.root, bg=C["bg"])
        self.body.pack(fill=tk.BOTH, expand=True)

        self._build_filmstrip()
        self._build_canvas_area()
        self._build_right_panel()

    def _build_filmstrip(self):
        """Left filmstrip — folder thumbnails"""
        self.filmstrip_frame = tk.Frame(self.body, bg=C["bg2"], width=110)
        self.filmstrip_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.filmstrip_frame.pack_propagate(False)

        tk.Label(self.filmstrip_frame, text="FOLDER",
                 bg=C["bg2"], fg=C["text3"],
                 font=("Helvetica", 9, "bold")).pack(pady=(10,4))

        # Scrollable canvas for thumbs
        self.strip_canvas = tk.Canvas(self.filmstrip_frame,
                                       bg=C["bg2"], width=108,
                                       highlightthickness=0)
        strip_scroll = ttk.Scrollbar(self.filmstrip_frame,
                                      orient=tk.VERTICAL,
                                      command=self.strip_canvas.yview)
        self.strip_canvas.configure(yscrollcommand=strip_scroll.set)
        self.strip_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.strip_inner = tk.Frame(self.strip_canvas, bg=C["bg2"])
        self.strip_canvas.create_window((0,0), window=self.strip_inner, anchor=tk.NW)
        self.strip_inner.bind("<Configure>",
                               lambda e: self.strip_canvas.configure(
                                   scrollregion=self.strip_canvas.bbox("all")))

        # Welcome label
        self.strip_label = tk.Label(self.strip_inner,
                                     text="Open a\nfolder\nto see\nimages",
                                     bg=C["bg2"], fg=C["text3"],
                                     font=("Helvetica", 9),
                                     justify=tk.CENTER)
        self.strip_label.pack(pady=20)

    def _build_canvas_area(self):
        self.canvas_wrap = tk.Frame(self.body, bg=C["bg"])
        self.canvas_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.canvas = tk.Canvas(self.canvas_wrap, bg=C["bg"],
                                 cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.create_text(400, 300,
                                 text="📸\n\n" + self.t["open_prompt"],
                                 fill=C["text3"], font=("Helvetica", 14),
                                 justify=tk.CENTER, tags="welcome")

        self.canvas.bind("<Configure>", lambda e: self._refresh_display())
        self.canvas.bind("<ButtonPress-1>",   self._crop_press)
        self.canvas.bind("<B1-Motion>",        self._crop_drag)
        self.canvas.bind("<ButtonRelease-1>",  self._crop_release)

    def _build_right_panel(self):
        """Right panel — adjustments"""
        self.right = tk.Frame(self.body, bg=C["bg2"], width=240)
        self.right.pack(side=tk.RIGHT, fill=tk.Y)
        self.right.pack_propagate(False)

        # Scrollable
        rcanvas = tk.Canvas(self.right, bg=C["bg2"],
                             highlightthickness=0, width=238)
        rscroll = ttk.Scrollbar(self.right, orient=tk.VERTICAL,
                                  command=rcanvas.yview)
        rcanvas.configure(yscrollcommand=rscroll.set)
        rscroll.pack(side=tk.RIGHT, fill=tk.Y)
        rcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.adj_frame = tk.Frame(rcanvas, bg=C["bg2"])
        rcanvas.create_window((0,0), window=self.adj_frame, anchor=tk.NW)
        self.adj_frame.bind("<Configure>",
                             lambda e: rcanvas.configure(
                                 scrollregion=rcanvas.bbox("all")))

        self._build_simple_adjustments()
        self._build_advanced_adjustments()
        self._build_transform_section()

        self.advanced_section.pack_forget()

    def _section_label(self, parent, text):
        f = tk.Frame(parent, bg=C["bg3"])
        f.pack(fill=tk.X, padx=0, pady=(8,0))
        tk.Label(f, text=text, bg=C["bg3"], fg=C["accent"],
                 font=("Helvetica", 9, "bold"),
                 padx=12, pady=5).pack(anchor=tk.W)
        return f

    def _slider(self, parent, label, var, from_, to, resolution=1.0):
        f = tk.Frame(parent, bg=C["bg2"])
        f.pack(fill=tk.X, padx=12, pady=3)
        row = tk.Frame(f, bg=C["bg2"])
        row.pack(fill=tk.X)
        tk.Label(row, text=label, bg=C["bg2"], fg=C["text2"],
                 font=("Helvetica", 10)).pack(side=tk.LEFT)
        val_lbl = tk.Label(row, bg=C["bg2"], fg=C["accent"],
                            font=("Helvetica", 9, "bold"), width=5)
        val_lbl.pack(side=tk.RIGHT)

        def update_label(*a):
            val_lbl.config(text=f"{var.get():.0f}" if resolution >= 1
                           else f"{var.get():.2f}")
            self._apply_all()

        tk.Scale(f, from_=from_, to=to, resolution=resolution,
                  orient=tk.HORIZONTAL, variable=var,
                  bg=C["bg2"], fg=C["text"], troughcolor=C["bg4"],
                  highlightthickness=0, sliderrelief=tk.FLAT,
                  activebackground=C["accent"], showvalue=False,
                  command=update_label).pack(fill=tk.X)
        update_label()

    def _build_simple_adjustments(self):
        self.simple_section = tk.Frame(self.adj_frame, bg=C["bg2"])
        self.simple_section.pack(fill=tk.X)

        self._section_label(self.simple_section, self.t["basic"])
        self._slider(self.simple_section, self.t["brightness"], self.brightness_var, 0.1, 3.0, 0.05)
        self._slider(self.simple_section, self.t["contrast"],   self.contrast_var,   0.1, 3.0, 0.05)
        self._slider(self.simple_section, self.t["exposure"],   self.exposure_var,  -100, 100, 1)

    def _build_advanced_adjustments(self):
        self.advanced_section = tk.Frame(self.adj_frame, bg=C["bg2"])

        # TONE
        self._section_label(self.advanced_section, self.t["tone"])
        self._slider(self.advanced_section, self.t["whites"], self.whites_var, -100, 100, 1)
        self._slider(self.advanced_section, self.t["blacks"], self.blacks_var, -100, 100, 1)

        # COLOR
        self._section_label(self.advanced_section, self.t["color"])
        self._slider(self.advanced_section, self.t["temperature"], self.temperature_var, -100, 100, 1)
        self._slider(self.advanced_section, self.t["tint"],        self.tint_var,        -100, 100, 1)

        # DETAIL
        self._section_label(self.advanced_section, self.t["detail"])
        self._slider(self.advanced_section, self.t["sharpening"], self.sharpening_var, 0, 100, 1)
        self._slider(self.advanced_section, self.t["dehaze"],     self.dehaze_var,     0, 100, 1)

    def _build_transform_section(self):
        self.transform_section = tk.Frame(self.adj_frame, bg=C["bg2"])
        self.transform_section.pack(fill=tk.X)

        self._section_label(self.transform_section, self.t["transform"])

        btn_grid = tk.Frame(self.transform_section, bg=C["bg2"])
        btn_grid.pack(padx=12, pady=6, fill=tk.X)

        btns = [
            ("↺", self.rotate_left),  ("↻", self.rotate_right),
            ("↔", self.flip_h),        ("↕", self.flip_v),
        ]
        for i, (icon, cmd) in enumerate(btns):
            tk.Button(btn_grid, text=icon, bg=C["bg3"], fg=C["text"],
                      font=("Helvetica", 16), relief=tk.FLAT,
                      cursor="hand2", width=3, pady=4,
                      command=cmd).grid(row=0, column=i, padx=2)

        tk.Button(self.transform_section,
                  text="✂️  " + self.t["crop"],
                  bg=C["bg3"], fg=C["text"],
                  font=("Helvetica", 11), relief=tk.FLAT,
                  cursor="hand2", padx=8, pady=6,
                  command=self.start_crop).pack(fill=tk.X, padx=12, pady=3)

        tk.Button(self.transform_section,
                  text="⊞  " + self.t["resize"],
                  bg=C["bg3"], fg=C["text"],
                  font=("Helvetica", 11), relief=tk.FLAT,
                  cursor="hand2", padx=8, pady=6,
                  command=self.resize_dialog).pack(fill=tk.X, padx=12, pady=3)

        # Reset
        tk.Button(self.transform_section,
                  text="🔄  " + self.t["reset"],
                  bg=C["bg2"], fg=C["text2"],
                  font=("Helvetica", 11), relief=tk.FLAT,
                  cursor="hand2", padx=8, pady=6,
                  command=self.reset_all).pack(fill=tk.X, padx=12, pady=(12,6))

    def _build_statusbar(self):
        bar = tk.Frame(self.root, bg=C["bg2"], height=28)
        bar.pack(fill=tk.X, side=tk.BOTTOM)
        bar.pack_propagate(False)
        self.status_lbl = tk.Label(bar, text="LocalShot — ImageStream Local Suite",
                                    bg=C["bg2"], fg=C["text3"],
                                    font=("Helvetica", 10))
        self.status_lbl.pack(side=tk.LEFT, padx=14)
        self.size_lbl = tk.Label(bar, text="",
                                  bg=C["bg2"], fg=C["text3"],
                                  font=("Helvetica", 10))
        self.size_lbl.pack(side=tk.RIGHT, padx=14)

    # ─── MODE & LANGUAGE ──────────────────────────────────────────────────────

    def _toggle_mode(self):
        self.advanced = not self.advanced
        if self.advanced:
            self.advanced_section.pack(fill=tk.X, after=self.simple_section)
            self.mode_btn.config(text="✦ " + self.t["simple_mode"])
        else:
            self.advanced_section.pack_forget()
            self.mode_btn.config(text="⚙ " + self.t["advanced_mode"])

    def _change_language(self, event=None):
        self.lang = self.lang_var.get()
        self.t = LANGUAGES[self.lang]
        # Rebuild UI preserving state
        img_backup = self.current_image
        orig_backup = self.original_image
        path_backup = self.image_path
        folder_backup = self.folder_images
        for w in self.root.winfo_children():
            w.destroy()
        self._build_ui()
        self.current_image = img_backup
        self.original_image = orig_backup
        self.image_path = path_backup
        self.folder_images = folder_backup
        if self.current_image:
            self._refresh_display()
        if self.folder_images:
            self._populate_filmstrip()

    # ─── FOLDER & FILMSTRIP ───────────────────────────────────────────────────

    def open_folder(self):
        folder = filedialog.askdirectory()
        if not folder:
            return
        files = []
        for ext in IMG_EXTENSIONS:
            files.extend(glob.glob(os.path.join(folder, ext)))
        files.sort()
        self.folder_images = files
        self._populate_filmstrip()
        if files:
            self._load_image(files[0])

    def _populate_filmstrip(self):
        for w in self.strip_inner.winfo_children():
            w.destroy()
        self.thumb_images = []
        for path in self.folder_images:
            self._add_thumb(path)

    def _add_thumb(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)
            # Pad to fixed size
            thumb = Image.new("RGB", (THUMB_W, THUMB_H), (30,30,30))
            x = (THUMB_W - img.width) // 2
            y = (THUMB_H - img.height) // 2
            thumb.paste(img, (x, y))
            tk_img = ImageTk.PhotoImage(thumb)
            self.thumb_images.append(tk_img)

            frame = tk.Frame(self.strip_inner, bg=C["bg2"],
                              cursor="hand2")
            frame.pack(pady=2, padx=4)

            lbl = tk.Label(frame, image=tk_img, bg=C["bg3"],
                            cursor="hand2")
            lbl.pack()
            lbl.bind("<Button-1>", lambda e, p=path: self._load_image(p))

            name = os.path.basename(path)[:10]
            tk.Label(frame, text=name, bg=C["bg2"], fg=C["text3"],
                      font=("Helvetica", 7)).pack()
        except Exception:
            pass

    # ─── IMAGE LOAD & DISPLAY ─────────────────────────────────────────────────

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif"),
                       ("All files", "*.*")])
        if path:
            self._load_image(path)

    def _load_image(self, path):
        self.image_path = path
        self.original_image = Image.open(path)
        self.current_image = self.original_image.copy()
        self._reset_vars()
        self._refresh_display()
        self._update_status()

    def _reset_vars(self):
        self.brightness_var.set(1.0)
        self.contrast_var.set(1.0)
        self.exposure_var.set(0.0)
        self.whites_var.set(0.0)
        self.blacks_var.set(0.0)
        self.temperature_var.set(0.0)
        self.tint_var.set(0.0)
        self.sharpening_var.set(0.0)
        self.dehaze_var.set(0.0)

    def _apply_all(self):
        if not self.original_image:
            return
        img = self.original_image.copy()

        # Basic
        img = ImageEnhance.Brightness(img).enhance(self.brightness_var.get())
        img = ImageEnhance.Contrast(img).enhance(self.contrast_var.get())

        # Exposure
        exp = self.exposure_var.get()
        if exp != 0:
            factor = 1.0 + exp / 100.0
            img = ImageEnhance.Brightness(img).enhance(max(0.01, factor))

        # Whites / Blacks
        w, b = self.whites_var.get(), self.blacks_var.get()
        if w != 0 or b != 0:
            img = apply_whites_blacks(img, w, b)

        # White Balance
        temp, tint = self.temperature_var.get(), self.tint_var.get()
        if temp != 0 or tint != 0:
            img = apply_white_balance(img, temp, tint)

        # Dehaze
        dh = self.dehaze_var.get()
        if dh > 0:
            img = apply_dehaze(img, dh)

        # Sharpening
        sh = self.sharpening_var.get()
        if sh > 0:
            img = apply_sharpening(img, sh)

        self.current_image = img
        self._refresh_display()

    def _refresh_display(self):
        if not self.current_image:
            return
        self.canvas.delete("all")
        cw = self.canvas.winfo_width() or 800
        ch = self.canvas.winfo_height() or 600
        iw, ih = self.current_image.size
        scale = min(cw / iw, ch / ih, 1.0)
        nw = int(iw * scale)
        nh = int(ih * scale)
        display = self.current_image.copy()
        display.thumbnail((nw, nh), Image.LANCZOS)
        self.photo_image = ImageTk.PhotoImage(display)
        x = (cw - nw) // 2
        y = (ch - nh) // 2
        self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)
        self._img_offset = (x, y, scale)

    def _update_status(self):
        if self.current_image:
            w, h = self.current_image.size
            name = os.path.basename(self.image_path) if self.image_path else ""
            self.status_lbl.config(text=f"📸  {name}")
            self.size_lbl.config(text=f"{w} × {h} px")

    # ─── SAVE ─────────────────────────────────────────────────────────────────

    def save_image(self):
        if not self.current_image:
            return
        path = filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"),
                       ("WebP", "*.webp"), ("BMP", "*.bmp"),
                       ("TIFF", "*.tiff")])
        if not path:
            return
        img = self.current_image
        if path.lower().endswith((".jpg", ".jpeg")) and img.mode in ["RGBA","P"]:
            img = img.convert("RGB")
        img.save(path, quality=95)
        self.status_lbl.config(text="✅ " + self.t["saved"])
        self.root.after(3000, self._update_status)

    # ─── TRANSFORMS ───────────────────────────────────────────────────────────

    def rotate_left(self):
        if not self.current_image: return
        self.original_image = self.current_image.rotate(90, expand=True)
        self.current_image = self.original_image.copy()
        self._refresh_display()

    def rotate_right(self):
        if not self.current_image: return
        self.original_image = self.current_image.rotate(-90, expand=True)
        self.current_image = self.original_image.copy()
        self._refresh_display()

    def flip_h(self):
        if not self.current_image: return
        self.original_image = self.current_image.transpose(Image.FLIP_LEFT_RIGHT)
        self.current_image = self.original_image.copy()
        self._refresh_display()

    def flip_v(self):
        if not self.current_image: return
        self.original_image = self.current_image.transpose(Image.FLIP_TOP_BOTTOM)
        self.current_image = self.original_image.copy()
        self._refresh_display()

    def reset_all(self):
        if not self.image_path: return
        self.original_image = Image.open(self.image_path)
        self.current_image = self.original_image.copy()
        self._reset_vars()
        self._refresh_display()

    # ─── CROP ─────────────────────────────────────────────────────────────────

    def start_crop(self):
        if not self.current_image: return
        self._cropping = True
        self.status_lbl.config(text="✂️  Drag on image to crop")

    def _crop_press(self, e):
        if self._cropping:
            self.crop_start = (e.x, e.y)
            if self.crop_rect:
                self.canvas.delete(self.crop_rect)

    def _crop_drag(self, e):
        if self._cropping and self.crop_start:
            if self.crop_rect:
                self.canvas.delete(self.crop_rect)
            self.crop_rect = self.canvas.create_rectangle(
                self.crop_start[0], self.crop_start[1], e.x, e.y,
                outline=C["accent"], width=2, dash=(5,3))

    def _crop_release(self, e):
        if not self._cropping or not self.crop_start:
            return
        x1, y1 = self.crop_start
        x2, y2 = e.x, e.y
        if abs(x2-x1) < 10 or abs(y2-y1) < 10:
            self._cropping = False
            return
        if hasattr(self, '_img_offset'):
            ox, oy, scale = self._img_offset
            iw, ih = self.current_image.size
            ix1 = int((min(x1,x2) - ox) / scale)
            iy1 = int((min(y1,y2) - oy) / scale)
            ix2 = int((max(x1,x2) - ox) / scale)
            iy2 = int((max(y1,y2) - oy) / scale)
            ix1 = max(0,ix1); iy1 = max(0,iy1)
            ix2 = min(iw,ix2); iy2 = min(ih,iy2)
            if ix2 > ix1 and iy2 > iy1:
                self.current_image = self.current_image.crop((ix1,iy1,ix2,iy2))
                self.original_image = self.current_image.copy()
                self._refresh_display()
                self._update_status()
        if self.crop_rect:
            self.canvas.delete(self.crop_rect)
        self._cropping = False
        self._update_status()

    # ─── RESIZE ───────────────────────────────────────────────────────────────

    def resize_dialog(self):
        if not self.current_image: return
        w, h = self.current_image.size
        d = tk.Toplevel(self.root)
        d.title(self.t["resize_title"])
        d.configure(bg=C["bg"])
        d.geometry("280x180")
        d.resizable(False, False)

        for row, (label, var_val) in enumerate([(self.t["width"], w), (self.t["height"], h)]):
            tk.Label(d, text=label + ":", bg=C["bg"], fg=C["text"],
                     font=("Helvetica", 12)).grid(row=row, column=0, padx=20, pady=12, sticky=tk.W)
        w_v = tk.IntVar(value=w)
        h_v = tk.IntVar(value=h)
        tk.Entry(d, textvariable=w_v, width=8, bg=C["bg3"], fg=C["text"],
                 insertbackground=C["text"]).grid(row=0, column=1, padx=10)
        tk.Entry(d, textvariable=h_v, width=8, bg=C["bg3"], fg=C["text"],
                 insertbackground=C["text"]).grid(row=1, column=1, padx=10)

        def apply():
            try:
                self.current_image = self.current_image.resize(
                    (w_v.get(), h_v.get()), Image.LANCZOS)
                self.original_image = self.current_image.copy()
                self._refresh_display()
                self._update_status()
                d.destroy()
            except Exception as ex:
                messagebox.showerror(self.t["error"], str(ex))

        bf = tk.Frame(d, bg=C["bg"])
        bf.grid(row=2, column=0, columnspan=2, pady=14)
        tk.Button(bf, text=self.t["apply"], bg=C["accent"], fg=C["bg"],
                  font=("Helvetica",11,"bold"), relief=tk.FLAT,
                  cursor="hand2", padx=14, pady=5, command=apply).pack(side=tk.LEFT, padx=6)
        tk.Button(bf, text=self.t["cancel"], bg=C["bg3"], fg=C["text"],
                  font=("Helvetica",11), relief=tk.FLAT,
                  cursor="hand2", padx=14, pady=5, command=d.destroy).pack(side=tk.LEFT, padx=6)


# ─── ENTRY ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = LocalShot(root)
    root.mainloop()
