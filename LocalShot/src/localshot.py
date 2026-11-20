"""
LocalShot — Image Editor for Everyone
Part of the ImageStream Local Suite by The Art Medium
Simple. Offline. Private. Yours.

Copyright (c) 2026 Satdiva / ImageStream (The-ArtMedium). All rights reserved.
Free to use. Not to be modified, redistributed or sold. See LICENSE.
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk, ImageEnhance, ImageFilter, ImageOps
import numpy as np
import os
import sys
import threading
import json
import webbrowser
from fractions import Fraction

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
# New texts (navigation, zoom, delete, Focus Check). English is the fallback.
EXTRA = {
    "English": {
        "grey_picker": "Grey Picker", "grey_hint": "Now click something that should be neutral grey or white.", "grey_bad": "That spot is too dark or too bright to read. Try another one.",
        "order": "Order", "auto": "Auto",
        "highlights": "Highlights", "shadows": "Shadows", "saturation": "Saturation", "greens_first": "Greens first",
        "prev": "Previous", "next": "Next", "delete": "Delete", "fit": "Fit",
        "before_after": "Before | After", "folder": "FOLDER",
        "strip_empty": "Open a\nfolder\nto see\nimages",
        "delete_confirm": "Move '{name}' to the Trash?\n\nYou can restore it from the Trash if you change your mind.",
        "delete_fail": "Could not move the photo to the Trash.",
        "moved_trash": "Moved to the Trash",
        "focus_title": "FOCUS CHECK", "focus_run": "Check Focus", "stop": "Stop",
        "checking": "Checking focus... {i} of {n}", "stopped": "Stopped. Nothing was changed.",
        "sharp": "IN FOCUS", "fixable": "FIXABLE", "rejected": "REJECTED",
        "show_all": "Show: all photos", "show": "Show",
        "recover": "Recover Sharpness", "trash_rejected": "Trash All Rejected",
        "trash_confirm": "Move {n} rejected photos to the Trash?\n\nRejected means the softest photos of this folder. Look at them first if you are not sure.\nYou can restore them from the Trash.",
        "no_rejected": "There are no rejected photos.",
        "already_sharp": "This photo is already sharp.",
        "need_scan": "Press Check Focus first, then click a photo.",
        "need_folder": "Open a folder first.",
        "motion_blur": "motion blur", "focus_error": "focus error", "of": "of",
        "loading": "Loading previews... {i} of {n}",
        "crop_hint": "Pull the corners or sides to adjust the frame, drag inside it to move it. Then press Apply.",
        "saving": "Saving...",
    },
    "Español": {
        "grey_picker": "Cuentagotas de Gris", "grey_hint": "Ahora haz clic en algo que deba ser gris neutro o blanco.", "grey_bad": "Ese punto es demasiado oscuro o claro. Prueba otro.",
        "order": "Orden", "auto": "Auto",
        "highlights": "Luces", "shadows": "Sombras", "saturation": "Saturación", "greens_first": "Verdes primero",
        "prev": "Anterior", "next": "Siguiente", "delete": "Eliminar", "fit": "Ajustar",
        "before_after": "Antes | Después", "folder": "CARPETA",
        "strip_empty": "Abre una\ncarpeta\npara ver\nimágenes",
        "delete_confirm": "¿Mover '{name}' a la Papelera?\n\nPuedes restaurarla desde la Papelera si cambias de opinión.",
        "delete_fail": "No se pudo mover la foto a la Papelera.",
        "moved_trash": "Movida a la Papelera",
        "focus_title": "CONTROL DE ENFOQUE", "focus_run": "Revisar Enfoque", "stop": "Detener",
        "checking": "Revisando enfoque... {i} de {n}", "stopped": "Detenido. No se cambió nada.",
        "sharp": "NÍTIDA", "fixable": "RECUPERABLE", "rejected": "RECHAZADA",
        "show_all": "Ver: todas las fotos", "show": "Ver",
        "recover": "Recuperar Nitidez", "trash_rejected": "Rechazadas a la Papelera",
        "trash_confirm": "¿Mover {n} fotos rechazadas a la Papelera?\n\nRechazada significa las fotos menos nítidas de esta carpeta. Míralas primero si no estás seguro.\nPuedes restaurarlas desde la Papelera.",
        "no_rejected": "No hay fotos rechazadas.",
        "already_sharp": "Esta foto ya está nítida.",
        "need_scan": "Pulsa primero Revisar Enfoque y luego haz clic en una foto.",
        "need_folder": "Abre primero una carpeta.",
        "motion_blur": "foto movida", "focus_error": "error de enfoque", "of": "de",
        "loading": "Cargando vistas... {i} de {n}",
        "crop_hint": "Tira de las esquinas o los lados para ajustar el marco; arrastra dentro para moverlo. Luego pulsa Aplicar.",
        "saving": "Guardando...",
    },
    "Français": {
        "grey_picker": "Pipette de Gris", "grey_hint": "Cliquez maintenant sur quelque chose qui doit être gris neutre ou blanc.", "grey_bad": "Ce point est trop sombre ou trop clair. Essayez-en un autre.",
        "order": "Ordre", "auto": "Auto",
        "highlights": "Hautes lumières", "shadows": "Ombres", "saturation": "Saturation", "greens_first": "Vertes d'abord",
        "prev": "Précédente", "next": "Suivante", "delete": "Supprimer", "fit": "Ajuster",
        "before_after": "Avant | Après", "folder": "DOSSIER",
        "strip_empty": "Ouvrez un\ndossier\npour voir\nles images",
        "delete_confirm": "Mettre '{name}' à la Corbeille ?\n\nVous pourrez la restaurer depuis la Corbeille.",
        "delete_fail": "Impossible de mettre la photo à la Corbeille.",
        "moved_trash": "Mise à la Corbeille",
        "focus_title": "CONTRÔLE DE NETTETÉ", "focus_run": "Vérifier la Netteté", "stop": "Arrêter",
        "checking": "Vérification... {i} sur {n}", "stopped": "Arrêté. Rien n'a été modifié.",
        "sharp": "NETTE", "fixable": "RÉCUPÉRABLE", "rejected": "REJETÉE",
        "show_all": "Voir : toutes les photos", "show": "Voir",
        "recover": "Récupérer la Netteté", "trash_rejected": "Rejetées à la Corbeille",
        "trash_confirm": "Mettre {n} photos rejetées à la Corbeille ?\n\nRejetée signifie les photos les moins nettes de ce dossier. Regardez-les d'abord en cas de doute.\nVous pourrez les restaurer depuis la Corbeille.",
        "no_rejected": "Il n'y a aucune photo rejetée.",
        "already_sharp": "Cette photo est déjà nette.",
        "need_scan": "Appuyez d'abord sur Vérifier la Netteté, puis cliquez sur une photo.",
        "need_folder": "Ouvrez d'abord un dossier.",
        "motion_blur": "flou de bougé", "focus_error": "erreur de mise au point", "of": "sur",
        "loading": "Chargement des aperçus... {i} sur {n}",
        "crop_hint": "Tirez les coins ou les côtés pour ajuster le cadre, glissez à l'intérieur pour le déplacer. Puis appuyez sur Appliquer.",
        "saving": "Enregistrement...",
    },
    "Português": {
        "grey_picker": "Conta-gotas de Cinza", "grey_hint": "Agora clique em algo que deveria ser cinza neutro ou branco.", "grey_bad": "Esse ponto é escuro ou claro demais. Tente outro.",
        "order": "Ordem", "auto": "Auto",
        "highlights": "Realces", "shadows": "Sombras", "saturation": "Saturação", "greens_first": "Verdes primeiro",
        "prev": "Anterior", "next": "Próxima", "delete": "Apagar", "fit": "Ajustar",
        "before_after": "Antes | Depois", "folder": "PASTA",
        "strip_empty": "Abra uma\npasta\npara ver\nas imagens",
        "delete_confirm": "Mover '{name}' para a Lixeira?\n\nVocê pode restaurá-la da Lixeira se mudar de ideia.",
        "delete_fail": "Não foi possível mover a foto para a Lixeira.",
        "moved_trash": "Movida para a Lixeira",
        "focus_title": "VERIFICAR FOCO", "focus_run": "Verificar Foco", "stop": "Parar",
        "checking": "Verificando foco... {i} de {n}", "stopped": "Parado. Nada foi alterado.",
        "sharp": "NÍTIDA", "fixable": "RECUPERÁVEL", "rejected": "REJEITADA",
        "show_all": "Ver: todas as fotos", "show": "Ver",
        "recover": "Recuperar Nitidez", "trash_rejected": "Rejeitadas para a Lixeira",
        "trash_confirm": "Mover {n} fotos rejeitadas para a Lixeira?\n\nRejeitada significa as fotos menos nítidas desta pasta. Veja-as primeiro se não tiver certeza.\nVocê pode restaurá-las da Lixeira.",
        "no_rejected": "Não há fotos rejeitadas.",
        "already_sharp": "Esta foto já está nítida.",
        "need_scan": "Clique primeiro em Verificar Foco e depois em uma foto.",
        "need_folder": "Abra uma pasta primeiro.",
        "motion_blur": "foto tremida", "focus_error": "erro de foco", "of": "de",
        "loading": "Carregando miniaturas... {i} de {n}",
        "crop_hint": "Puxe os cantos ou os lados para ajustar a moldura; arraste dentro para movê-la. Depois clique em Aplicar.",
        "saving": "Salvando...",
    },
    "العربية": {
        "grey_picker": "قطّارة الرمادي", "grey_hint": "انقر الآن على شيء يجب أن يكون رمادياً محايداً أو أبيض.", "grey_bad": "هذه النقطة داكنة جداً أو ساطعة جداً. جرّب نقطة أخرى.",
        "order": "الترتيب", "auto": "تلقائي",
        "highlights": "الإضاءات", "shadows": "الظلال", "saturation": "التشبع", "greens_first": "الواضحة أولاً",
        "prev": "السابقة", "next": "التالية", "delete": "حذف", "fit": "ملاءمة",
        "before_after": "قبل | بعد", "folder": "المجلد",
        "strip_empty": "افتح مجلداً\nلعرض الصور",
        "delete_confirm": "نقل '{name}' إلى سلة المهملات؟\n\nيمكنك استعادتها من سلة المهملات.",
        "delete_fail": "تعذر نقل الصورة إلى سلة المهملات.",
        "moved_trash": "نُقلت إلى سلة المهملات",
        "focus_title": "فحص الوضوح", "focus_run": "فحص الوضوح", "stop": "إيقاف",
        "checking": "جارٍ الفحص... {i} من {n}", "stopped": "تم الإيقاف. لم يتغير شيء.",
        "sharp": "واضحة", "fixable": "قابلة للإصلاح", "rejected": "مرفوضة",
        "show_all": "عرض: كل الصور", "show": "عرض",
        "recover": "استعادة الوضوح", "trash_rejected": "المرفوضة إلى السلة",
        "trash_confirm": "نقل {n} صورة مرفوضة إلى سلة المهملات؟\n\nالمرفوضة تعني أقل الصور وضوحاً في هذا المجلد. راجعها أولاً إن لم تكن متأكداً.\nيمكنك استعادتها من سلة المهملات.",
        "no_rejected": "لا توجد صور مرفوضة.",
        "already_sharp": "هذه الصورة واضحة بالفعل.",
        "need_scan": "اضغط فحص الوضوح أولاً ثم انقر على صورة.",
        "need_folder": "افتح مجلداً أولاً.",
        "motion_blur": "اهتزاز الحركة", "focus_error": "خطأ في التركيز", "of": "من",
        "loading": "جارٍ تحميل المعاينات... {i} من {n}",
        "crop_hint": "اسحب الزوايا أو الجوانب لضبط الإطار، واسحب داخله لتحريكه. ثم اضغط تطبيق.",
        "saving": "جارٍ الحفظ...",
    },
    "中文": {
        "grey_picker": "灰点吸管", "grey_hint": "现在点击照片中应为中性灰或白色的地方。", "grey_bad": "该处太暗或太亮，无法读取。请换一处。",
        "order": "顺序", "auto": "自动",
        "highlights": "高光", "shadows": "阴影", "saturation": "饱和度", "greens_first": "清晰的排前面",
        "prev": "上一张", "next": "下一张", "delete": "删除", "fit": "适合窗口",
        "before_after": "修改前 | 修改后", "folder": "文件夹",
        "strip_empty": "打开文件夹\n查看图片",
        "delete_confirm": "将“{name}”移到废纸篓？\n\n如果改变主意，可以从废纸篓恢复。",
        "delete_fail": "无法将照片移到废纸篓。",
        "moved_trash": "已移到废纸篓",
        "focus_title": "对焦检查", "focus_run": "检查对焦", "stop": "停止",
        "checking": "正在检查对焦... {i} / {n}", "stopped": "已停止，未作任何更改。",
        "sharp": "清晰", "fixable": "可修复", "rejected": "淘汰",
        "show_all": "显示：全部照片", "show": "显示",
        "recover": "恢复清晰度", "trash_rejected": "淘汰的全部移到废纸篓",
        "trash_confirm": "将 {n} 张淘汰的照片移到废纸篓？\n\n“淘汰”是指此文件夹中最不清晰的照片。如不确定，请先查看。\n可以从废纸篓恢复。",
        "no_rejected": "没有淘汰的照片。",
        "already_sharp": "这张照片已经清晰。",
        "need_scan": "请先点击“检查对焦”，再点击一张照片。",
        "need_folder": "请先打开文件夹。",
        "motion_blur": "运动模糊", "focus_error": "对焦失误", "of": "/",
        "loading": "正在加载预览... {i} / {n}",
        "crop_hint": "拖动边角或边线调整裁剪框，在框内拖动可移动。然后点击“应用”。",
        "saving": "正在保存...",
    },
    "हिन्दी": {
        "grey_picker": "ग्रे पिकर", "grey_hint": "अब फ़ोटो में ऐसी जगह क्लिक करें जो तटस्थ ग्रे या सफ़ेद होनी चाहिए।", "grey_bad": "यह जगह बहुत गहरी या बहुत चमकीली है। कोई और जगह चुनें।",
        "order": "क्रम", "auto": "ऑटो",
        "highlights": "हाइलाइट", "shadows": "छाया", "saturation": "संतृप्ति", "greens_first": "स्पष्ट पहले",
        "prev": "पिछला", "next": "अगला", "delete": "हटाएँ", "fit": "फ़िट",
        "before_after": "पहले | बाद में", "folder": "फ़ोल्डर",
        "strip_empty": "चित्र देखने\nके लिए\nफ़ोल्डर खोलें",
        "delete_confirm": "'{name}' को ट्रैश में भेजें?\n\nमन बदलने पर आप इसे ट्रैश से वापस ला सकते हैं।",
        "delete_fail": "फ़ोटो को ट्रैश में नहीं भेजा जा सका।",
        "moved_trash": "ट्रैश में भेजा गया",
        "focus_title": "फ़ोकस जाँच", "focus_run": "फ़ोकस जाँचें", "stop": "रोकें",
        "checking": "फ़ोकस जाँच रहे हैं... {n} में से {i}", "stopped": "रोक दिया गया। कुछ नहीं बदला।",
        "sharp": "स्पष्ट", "fixable": "सुधार योग्य", "rejected": "अस्वीकृत",
        "show_all": "दिखाएँ: सभी फ़ोटो", "show": "दिखाएँ",
        "recover": "स्पष्टता वापस लाएँ", "trash_rejected": "अस्वीकृत ट्रैश में भेजें",
        "trash_confirm": "{n} अस्वीकृत फ़ोटो ट्रैश में भेजें?\n\nअस्वीकृत का अर्थ है इस फ़ोल्डर की सबसे धुंधली फ़ोटो। पक्का न हो तो पहले देख लें।\nआप इन्हें ट्रैश से वापस ला सकते हैं।",
        "no_rejected": "कोई अस्वीकृत फ़ोटो नहीं है।",
        "already_sharp": "यह फ़ोटो पहले से स्पष्ट है।",
        "need_scan": "पहले फ़ोकस जाँचें दबाएँ, फिर किसी फ़ोटो पर क्लिक करें।",
        "need_folder": "पहले एक फ़ोल्डर खोलें।",
        "motion_blur": "गति से धुंधलापन", "focus_error": "फ़ोकस की गलती", "of": "/",
        "loading": "पूर्वावलोकन लोड हो रहे हैं... {n} में से {i}",
        "crop_hint": "फ़्रेम ठीक करने के लिए कोने या किनारे खींचें, खिसकाने के लिए अंदर खींचें। फिर लागू करें दबाएँ।",
        "saving": "सहेज रहे हैं...",
    },
}
for _name, _texts in EXTRA.items():
    LANGUAGES[_name].update(_texts)
for _name in LANGUAGES:                       # anything missing falls back to English
    for _key, _value in LANGUAGES["English"].items():
        LANGUAGES[_name].setdefault(_key, _value)

# ─── QUICK START, KO-FI, AUTOMATIC LANGUAGE ──────────────────────────────────

QS_TEXT = {
    "English": {
        "auto_lang": "Automatic", "quick_start": "Quick Start", "got_it": "Got it",
        "show_at_start": "Show this when LocalShot starts",
        "kofi_tip": "LocalShot is free. If it helps your work, a coffee on Ko-fi keeps it going.",
        "kofi_thanks": "☕ Thank you! Say thanks on Ko-fi",
        "qs_intro": "LocalShot sorts, fixes and saves your photos on your own computer. Here is how, step by step.",
        "qs1": "Open your photos", "qs1b": "Click Open Folder to see all the photos of a shoot in the strip on the left, or Open Image for a single photo. Your originals are never changed.",
        "qs2": "Check the focus", "qs2b": "Press Check Focus. Every photo gets a colour: green in focus, yellow fixable, red rejected. The colour buttons show only those photos. Recover Sharpness helps a yellow one.",
        "qs3": "Look closely", "qs3b": "Press + and − to zoom, 1 for 100 %, 0 to fit the window. Drag to move around. Before | After compares your edit with the original.",
        "qs4": "Adjust", "qs4b": "Use the sliders on the right. Auto sets the tone for you. Grey Picker: click something white or grey and the colour cast is gone. Advanced shows more controls.",
        "qs5": "Crop and turn", "qs5b": "Crop: pull the corners or sides, drag inside the frame to move it, then press Apply. Rotate and Flip are in the same section.",
        "qs6": "Save", "qs6b": "Save / Export writes a new file, JPEG or PNG, wherever you choose. The original stays exactly as it was.",
        "qs7": "Next photo", "qs7b": "← → move through the photos. Delete sends the current photo to the Trash, where you can still restore it. Trash All Rejected clears the red ones in one go.",
        "qs_tip": "Everything happens on your computer: no internet, no account, no tracking.",
    },
    "Español": {
        "auto_lang": "Automático", "quick_start": "Guía rápida", "got_it": "Entendido",
        "show_at_start": "Mostrar al abrir LocalShot",
        "kofi_tip": "LocalShot es gratis. Si le sirve en su trabajo, un café en Ko-fi lo mantiene vivo.",
        "kofi_thanks": "☕ ¡Gracias! Agradezca en Ko-fi",
        "qs_intro": "LocalShot ordena, corrige y guarda sus fotos en su propia computadora. Así se hace, paso a paso.",
        "qs1": "Abrir sus fotos", "qs1b": "Haga clic en Abrir carpeta para ver todas las fotos de una sesión en la tira de la izquierda, o en Abrir imagen para una sola foto. Sus originales nunca cambian.",
        "qs2": "Revisar el foco", "qs2b": "Pulse Revisar foco. Cada foto recibe un color: verde en foco, amarillo recuperable, rojo descartada. Los botones de color muestran solo esas fotos. Recuperar nitidez ayuda a una amarilla.",
        "qs3": "Mirar de cerca", "qs3b": "Pulse + y − para acercar, 1 para el 100 %, 0 para ajustar a la ventana. Arrastre para moverse. Antes | Después compara su ajuste con el original.",
        "qs4": "Ajustar", "qs4b": "Use los controles de la derecha. Auto ajusta el tono por usted. Selector de gris: haga clic en algo blanco o gris y el tinte desaparece. Avanzado muestra más controles.",
        "qs5": "Recortar y girar", "qs5b": "Recortar: tire de las esquinas o lados, arrastre dentro del marco para moverlo y pulse Aplicar. Girar y Voltear están en la misma sección.",
        "qs6": "Guardar", "qs6b": "Guardar / Exportar crea un archivo nuevo, JPEG o PNG, donde usted elija. El original queda exactamente igual.",
        "qs7": "Siguiente foto", "qs7b": "← → recorren las fotos. Borrar envía la foto actual a la papelera, de donde aún puede recuperarla. Enviar descartadas a la papelera quita las rojas de una vez.",
        "qs_tip": "Todo sucede en su computadora: sin internet, sin cuenta, sin rastreo.",
    },
    "Français": {
        "auto_lang": "Automatique", "quick_start": "Prise en main", "got_it": "Compris",
        "show_at_start": "Afficher à l'ouverture de LocalShot",
        "kofi_tip": "LocalShot est gratuit. S'il vous aide dans votre travail, un café sur Ko-fi le fait vivre.",
        "kofi_thanks": "☕ Merci ! Dites merci sur Ko-fi",
        "qs_intro": "LocalShot trie, corrige et enregistre vos photos sur votre propre ordinateur. Voici comment, pas à pas.",
        "qs1": "Ouvrir vos photos", "qs1b": "Cliquez sur Ouvrir un dossier pour voir toutes les photos d'une séance dans le bandeau de gauche, ou sur Ouvrir une image pour une seule photo. Vos originaux ne sont jamais modifiés.",
        "qs2": "Contrôler la netteté", "qs2b": "Appuyez sur Contrôler la netteté. Chaque photo reçoit une couleur : vert net, jaune récupérable, rouge rejeté. Les boutons de couleur n'affichent que ces photos. Récupérer la netteté aide une jaune.",
        "qs3": "Regarder de près", "qs3b": "Appuyez sur + et − pour zoomer, 1 pour 100 %, 0 pour ajuster à la fenêtre. Faites glisser pour vous déplacer. Avant | Après compare votre réglage avec l'original.",
        "qs4": "Régler", "qs4b": "Utilisez les curseurs à droite. Auto règle les tons pour vous. Pipette grise : cliquez sur quelque chose de blanc ou gris et la dominante disparaît. Avancé affiche plus de réglages.",
        "qs5": "Recadrer et tourner", "qs5b": "Recadrer : tirez les coins ou les côtés, faites glisser dans le cadre pour le déplacer, puis Appliquer. Pivoter et Retourner sont dans la même section.",
        "qs6": "Enregistrer", "qs6b": "Enregistrer / Exporter crée un nouveau fichier, JPEG ou PNG, à l'endroit choisi. L'original reste exactement tel quel.",
        "qs7": "Photo suivante", "qs7b": "← → parcourent les photos. Supprimer met la photo à la corbeille, d'où vous pouvez encore la récupérer. Mettre les rejetées à la corbeille retire les rouges d'un coup.",
        "qs_tip": "Tout se passe sur votre ordinateur : sans internet, sans compte, sans pistage.",
    },
    "Português": {
        "auto_lang": "Automático", "quick_start": "Guia rápido", "got_it": "Entendi",
        "show_at_start": "Mostrar ao abrir o LocalShot",
        "kofi_tip": "LocalShot é grátis. Se ajuda no seu trabalho, um café no Ko-fi o mantém vivo.",
        "kofi_thanks": "☕ Obrigado! Agradeça no Ko-fi",
        "qs_intro": "LocalShot organiza, corrige e salva suas fotos no seu próprio computador. Veja como, passo a passo.",
        "qs1": "Abrir suas fotos", "qs1b": "Clique em Abrir pasta para ver todas as fotos de um trabalho na faixa à esquerda, ou em Abrir imagem para uma só foto. Seus originais nunca mudam.",
        "qs2": "Verificar o foco", "qs2b": "Aperte Verificar foco. Cada foto ganha uma cor: verde em foco, amarelo recuperável, vermelho descartada. Os botões de cor mostram só essas fotos. Recuperar nitidez ajuda uma amarela.",
        "qs3": "Olhar de perto", "qs3b": "Aperte + e − para dar zoom, 1 para 100 %, 0 para caber na janela. Arraste para se mover. Antes | Depois compara seu ajuste com o original.",
        "qs4": "Ajustar", "qs4b": "Use os controles à direita. Auto ajusta o tom para você. Seletor de cinza: clique em algo branco ou cinza e a dominante some. Avançado mostra mais controles.",
        "qs5": "Cortar e girar", "qs5b": "Cortar: puxe os cantos ou lados, arraste dentro do quadro para movê-lo e aperte Aplicar. Girar e Espelhar ficam na mesma seção.",
        "qs6": "Salvar", "qs6b": "Salvar / Exportar cria um arquivo novo, JPEG ou PNG, onde você escolher. O original fica exatamente como estava.",
        "qs7": "Próxima foto", "qs7b": "← → passam pelas fotos. Apagar manda a foto atual para o lixo, de onde ainda dá para recuperar. Mandar descartadas para o lixo tira as vermelhas de uma vez.",
        "qs_tip": "Tudo acontece no seu computador: sem internet, sem conta, sem rastreamento.",
    },
    "العربية": {
        "auto_lang": "تلقائي", "quick_start": "البدء السريع", "got_it": "فهمت",
        "show_at_start": "اعرض هذا عند فتح LocalShot",
        "kofi_tip": "LocalShot مجاني. إن كان يفيد عملك، فقهوة على Ko-fi تُبقيه مستمرًا.",
        "kofi_thanks": "☕ شكرًا! قل شكرًا على Ko-fi",
        "qs_intro": "يرتّب LocalShot صورك ويصلحها ويحفظها على جهازك. إليك الطريقة خطوة بخطوة.",
        "qs1": "افتح صورك", "qs1b": "انقر «فتح مجلد» لترى كل صور الجلسة في الشريط على اليسار، أو «فتح صورة» لصورة واحدة. أصولك لا تتغير أبدًا.",
        "qs2": "افحص التركيز", "qs2b": "اضغط «فحص التركيز». تحصل كل صورة على لون: أخضر واضحة، أصفر قابلة للإصلاح، أحمر مرفوضة. أزرار الألوان تعرض تلك الصور فقط. «استعادة الحدة» تساعد الصفراء.",
        "qs3": "انظر عن قرب", "qs3b": "اضغط + و − للتكبير، 1 لحجم 100 %، 0 لملاءمة النافذة. اسحب للتنقل. «قبل | بعد» يقارن تعديلك بالأصل.",
        "qs4": "اضبط", "qs4b": "استخدم المنزلقات على اليمين. «تلقائي» يضبط الدرجات عنك. منتقي الرمادي: انقر شيئًا أبيض أو رماديًا فتزول الصبغة اللونية. «متقدم» يعرض أدوات أكثر.",
        "qs5": "قص ودوّر", "qs5b": "القص: اسحب الزوايا أو الجوانب، واسحب داخل الإطار لتحريكه، ثم اضغط «تطبيق». التدوير والقلب في القسم نفسه.",
        "qs6": "احفظ", "qs6b": "«حفظ / تصدير» ينشئ ملفًا جديدًا، JPEG أو PNG، حيث تختار. يبقى الأصل كما هو تمامًا.",
        "qs7": "الصورة التالية", "qs7b": "← → للتنقل بين الصور. «حذف» يرسل الصورة الحالية إلى المهملات، ويمكنك استعادتها. «نقل كل المرفوضة إلى المهملات» يزيل الحمراء دفعة واحدة.",
        "qs_tip": "كل شيء يحدث على جهازك: بلا إنترنت، بلا حساب، بلا تتبّع.",
    },
    "中文": {
        "auto_lang": "自动", "quick_start": "快速入门", "got_it": "知道了",
        "show_at_start": "启动 LocalShot 时显示",
        "kofi_tip": "LocalShot 免费。如果它对你的工作有帮助，在 Ko-fi 请杯咖啡就能让它继续下去。",
        "kofi_thanks": "☕ 谢谢！在 Ko-fi 上表达感谢",
        "qs_intro": "LocalShot 在你自己的电脑上整理、修正并保存照片。下面一步步说明。",
        "qs1": "打开照片", "qs1b": "点击“打开文件夹”，在左侧缩略图条中查看一次拍摄的所有照片；或点击“打开图片”打开单张照片。原片永远不会被改动。",
        "qs2": "检查对焦", "qs2b": "按“检查对焦”。每张照片会得到一种颜色：绿色清晰，黄色可修复，红色淘汰。颜色按钮只显示对应的照片。“恢复锐度”可帮助黄色照片。",
        "qs3": "仔细查看", "qs3b": "按 + 和 − 缩放，按 1 为 100 %，按 0 适合窗口。拖动可移动画面。“前 | 后”把你的调整与原片对比。",
        "qs4": "调整", "qs4b": "使用右侧滑块。“自动”会替你设置影调。灰色吸管：点击白色或灰色的地方即可去除偏色。“高级”显示更多控制。",
        "qs5": "裁剪和旋转", "qs5b": "裁剪：拖动角或边，在框内拖动以移动，然后按“应用”。旋转和翻转在同一区域。",
        "qs6": "保存", "qs6b": "“保存 / 导出”会在你选择的位置生成新的 JPEG 或 PNG 文件。原片保持原样。",
        "qs7": "下一张", "qs7b": "← → 浏览照片。“删除”把当前照片移到废纸篓，仍可恢复。“将淘汰照片全部移到废纸篓”一次清除红色照片。",
        "qs_tip": "一切都在你的电脑上完成：无需联网，无需账号，没有跟踪。",
    },
    "हिन्दी": {
        "auto_lang": "अपने-आप", "quick_start": "जल्दी शुरुआत", "got_it": "समझ गया",
        "show_at_start": "LocalShot खुलने पर यह दिखाएँ",
        "kofi_tip": "LocalShot मुफ़्त है। अगर यह आपके काम आता है, तो Ko-fi पर एक कॉफ़ी इसे चलाए रखती है।",
        "kofi_thanks": "☕ धन्यवाद! Ko-fi पर शुक्रिया कहें",
        "qs_intro": "LocalShot आपकी फ़ोटो आपके ही कंप्यूटर पर छाँटता, सुधारता और सेव करता है। यह रहा तरीका, कदम दर कदम।",
        "qs1": "फ़ोटो खोलें", "qs1b": "किसी शूट की सारी फ़ोटो बाईं पट्टी में देखने के लिए 'फ़ोल्डर खोलें' पर क्लिक करें, या एक फ़ोटो के लिए 'तस्वीर खोलें'। आपकी मूल फ़ोटो कभी नहीं बदलतीं।",
        "qs2": "फ़ोकस जाँचें", "qs2b": "'फ़ोकस जाँचें' दबाएँ। हर फ़ोटो को एक रंग मिलता है: हरा साफ़, पीला सुधार योग्य, लाल अस्वीकृत। रंग वाले बटन सिर्फ़ वही फ़ोटो दिखाते हैं। 'शार्पनेस वापस लाएँ' पीली फ़ोटो की मदद करता है।",
        "qs3": "पास से देखें", "qs3b": "ज़ूम के लिए + और − दबाएँ, 100 % के लिए 1, विंडो में फ़िट करने के लिए 0। घूमने के लिए खींचें। 'पहले | बाद' आपके एडिट की मूल से तुलना करता है।",
        "qs4": "सुधारें", "qs4b": "दाईं ओर के स्लाइडर इस्तेमाल करें। 'ऑटो' टोन अपने-आप सेट करता है। ग्रे पिकर: किसी सफ़ेद या ग्रे चीज़ पर क्लिक करें और रंग की झलक हट जाती है। 'एडवांस्ड' ज़्यादा कंट्रोल दिखाता है।",
        "qs5": "क्रॉप करें और घुमाएँ", "qs5b": "क्रॉप: कोने या किनारे खींचें, फ़्रेम के अंदर खींचकर उसे हिलाएँ, फिर 'लागू करें' दबाएँ। घुमाना और पलटना उसी हिस्से में हैं।",
        "qs6": "सेव करें", "qs6b": "'सेव / एक्सपोर्ट' आपकी चुनी जगह पर नई फ़ाइल, JPEG या PNG, बनाता है। मूल फ़ोटो जैसी थी वैसी ही रहती है।",
        "qs7": "अगली फ़ोटो", "qs7b": "← → से फ़ोटो बदलें। 'हटाएँ' मौजूदा फ़ोटो को ट्रैश में भेजता है, जहाँ से वह वापस आ सकती है। 'सभी अस्वीकृत ट्रैश में' लाल फ़ोटो एक साथ हटाता है।",
        "qs_tip": "सब कुछ आपके कंप्यूटर पर होता है: न इंटरनेट, न अकाउंट, न ट्रैकिंग।",
    },
}
for _name, _texts in QS_TEXT.items():
    LANGUAGES[_name].update(_texts)
for _name in LANGUAGES:
    for _key, _value in QS_TEXT["English"].items():
        LANGUAGES[_name].setdefault(_key, _value)

KOFI = "https://ko-fi.com/satdiva"
LANG_BY_CODE = {"en": "English", "es": "Español", "fr": "Français", "pt": "Português",
                "ar": "العربية", "zh": "中文", "hi": "हिन्दी"}


def _settings_file():
    if sys.platform == "darwin":
        base = os.path.expanduser("~/Library/Application Support/LocalShot")
    elif sys.platform.startswith("win"):
        base = os.path.join(os.environ.get("APPDATA", os.path.expanduser("~")), "LocalShot")
    else:
        base = os.path.expanduser("~/.config/localshot")
    return os.path.join(base, "settings.json")


def load_settings():
    try:
        with open(_settings_file(), encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return {}


def save_settings(data):
    try:
        os.makedirs(os.path.dirname(_settings_file()), exist_ok=True)
        with open(_settings_file(), "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=1)
    except Exception:
        pass


def computer_language():
    """The computer's own language (System Settings on a Mac, the Windows display
    language), if LocalShot speaks it; English otherwise."""
    tags = []
    try:
        if sys.platform == "darwin":
            import subprocess
            out = subprocess.run(["defaults", "read", "-g", "AppleLanguages"],
                                 capture_output=True, text=True, timeout=3).stdout
            tags += [t.strip(' ",()\n') for t in out.split("\n") if t.strip(' ",()\n')]
        elif sys.platform.startswith("win"):
            import ctypes, locale
            tags.append(locale.windows_locale.get(ctypes.windll.kernel32.GetUserDefaultUILanguage(), ""))
    except Exception:
        pass
    tags += [os.environ.get("LANG", ""), os.environ.get("LANGUAGE", "")]
    for tag in tags:
        code = tag.replace("_", "-").split("-")[0].lower()
        if code in LANG_BY_CODE:
            return LANG_BY_CODE[code]
    return "English"


# ─── COLORS ───────────────────────────────────────────────────────────────────

C = {
    "bg":       "#141414",
    "bg2":      "#1e1e1e",
    "bg3":      "#282828",
    "bg4":      "#3a3a3a",
    "accent":   "#f5a623",
    "accent2":  "#ffb940",
    "text":     "#f0f0f0",
    "text2":    "#999999",
    "text3":    "#666666",
    "border":   "#333333",
    "success":  "#2f7d5b",
    "danger":   "#e05252",
    "blue":     "#5b9cf6",
}
FOCUS_COLORS = {"sharp": "#4caf50", "fixable": "#ffd54f", "rejected": "#ff6b6b"}

THUMB_W, THUMB_H = 132, 99
STRIP_W = 176
PREVIEW_MAX = 1600
IMG_EXTENSIONS = (".jpg", ".jpeg", ".png", ".webp", ".bmp", ".tiff", ".tif")
SCORE_LONG_SIDE = 1600
MOTION_SHUTTER = Fraction(1, 250)
MAX_ZOOM = 4.0
APP_VERSION = "1.7"      # shown in the window title, so an old copy is easy to spot
GRIP = 14                # how close the pointer must be to grab a corner or side of the crop frame


# ─── HELPER: IMAGE PROCESSING ────────────────────────────────────────────────

def apply_white_balance(img, temperature, tint):
    """Temperature: -100 (cool/blue) to +100 (warm/orange). Tint: -100 (green) to +100 (magenta)."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    arr = np.array(img, dtype=np.float32)
    arr[:, :, 0] = np.clip(arr[:, :, 0] + temperature * 0.5, 0, 255)
    arr[:, :, 1] = np.clip(arr[:, :, 1] - tint * 0.5, 0, 255)
    arr[:, :, 2] = np.clip(arr[:, :, 2] - temperature * 0.5, 0, 255)
    return Image.fromarray(arr.astype(np.uint8))

def apply_whites_blacks(img, whites, blacks):
    """Whites: +100 brightens the white point. Blacks: -100 deepens the black point."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    black_point = -blacks / 100.0 * 0.12
    white_point = 1.0 - whites / 100.0 * 0.20
    arr = np.asarray(img, dtype=np.float32) / 255.0
    arr = (arr - black_point) / max(0.05, white_point - black_point)
    return Image.fromarray((np.clip(arr, 0, 1) * 255).astype(np.uint8))

def auto_tone_values(lum):
    """From the brightness of a photo (0..1): exposure gain, then
    (highlights, shadows, whites, blacks), each -1..1."""
    hi = float(np.percentile(lum, 99.5))
    # an underexposed photo is first lifted so its brightest tones reach near white
    gain = min(2.0, max(1.0, 0.96 / max(hi, 0.02))) if hi < 0.90 else 1.0
    lum = np.clip(lum * gain, 0, 1)
    lo, hi = np.percentile(lum, 0.5), np.percentile(lum, 99.5)
    blacks = -min(1.0, lo / 0.12) if lo > 0.01 else 0.0
    whites = min(1.0, max(0.0, (1.0 - hi) / 0.20))
    black_point, white_point = -blacks * 0.12, 1.0 - whites * 0.20
    mid = (float(np.median(lum)) - black_point) / max(0.05, white_point - black_point)
    shadows = min(0.7, (0.32 - mid) / 0.32 * 1.2) if mid < 0.32 else 0.0
    highlights = -min(0.6, (mid - 0.62) / 0.38) if mid > 0.62 else 0.0
    return gain, highlights, shadows, whites, blacks

def apply_highlights_shadows(img, highlights, shadows):
    """Highlights: -100 recovers bright areas, +100 brightens them.
    Shadows: +100 opens dark areas, -100 deepens them. Tones are never flipped."""
    if img.mode != "RGB":
        img = img.convert("RGB")
    h, sh = highlights / 100.0, shadows / 100.0
    radius = max(1.0, min(img.size) / 150.0)       # soft mask keeps fine detail
    soft = np.asarray(img.convert("L").filter(ImageFilter.GaussianBlur(radius)), dtype=np.float32) / 255.0
    dark = np.clip(1.0 - soft / 0.5, 0, 1)
    bright = np.clip((soft - 0.5) / 0.5, 0, 1)
    delta = h * 0.22 * bright ** 2
    delta = delta + (sh * 0.22 * dark ** 2 if sh > 0 else sh * 0.6 * dark * soft)
    gain = np.clip((soft + delta) / np.maximum(soft, 0.02), 0, 4)
    arr = np.asarray(img, dtype=np.float32) * gain[..., None]
    return Image.fromarray(np.clip(arr, 0, 255).astype(np.uint8))

def apply_dehaze(img, strength):
    """Simple dehazing using contrast enhancement + slight saturation boost."""
    if strength == 0:
        return img
    if img.mode != "RGB":
        img = img.convert("RGB")
    img = ImageEnhance.Contrast(img).enhance(1.0 + strength / 50.0)
    return ImageEnhance.Color(img).enhance(1.0 + strength / 100.0)

def apply_sharpening(img, strength):
    if strength == 0:
        return img
    if img.mode not in ["RGB", "L"]:
        img = img.convert("RGB")
    for _ in range(max(1, int(strength / 30))):
        img = img.filter(ImageFilter.SHARPEN)
    return img


# ─── HELPER: FOCUS CHECK (same method as FocusCheck / LocalRAW) ──────────────

def score_image(path):
    """Sharpness as Laplacian variance, measured at one fixed size for every photo."""
    try:
        with Image.open(path) as img:
            img.draft("L", (SCORE_LONG_SIDE, SCORE_LONG_SIDE))     # fast JPEG decode
            img = img.convert("L")
            if max(img.size) > SCORE_LONG_SIDE:
                k = SCORE_LONG_SIDE / float(max(img.size))
                img = img.resize((int(img.width * k), int(img.height * k)), Image.BOX)
            g = np.asarray(img, dtype=np.float32)
        if g.shape[0] < 3 or g.shape[1] < 3:
            return 0.0
        lap = (g[:-2, 1:-1] + g[2:, 1:-1] + g[1:-1, :-2] + g[1:-1, 2:] - 4.0 * g[1:-1, 1:-1])
        return float(lap.var())
    except Exception:
        return 0.0

def get_shutter(path):
    try:
        with Image.open(path) as img:
            exif = img.getexif()
            value = exif.get_ifd(0x8769).get(0x829A) or exif.get(0x829A)
        if value is None:
            return None
        if isinstance(value, tuple):
            return Fraction(int(value[0]), int(value[1]))
        return Fraction(float(value)).limit_denominator(100000)
    except Exception:
        return None

def blur_type(shutter):
    if shutter is None:
        return "unknown"
    return "motion" if shutter >= MOTION_SHUTTER else "focus"

def shutter_str(shutter):
    if shutter is None:
        return ""
    if shutter >= 1:
        return f"{float(shutter):.1f}s"
    return f"1/{int(round(1 / shutter))}s"

def calibrate(scores):
    """Limits relative to this shoot: (sharp_limit, fixable_limit)."""
    if not scores:
        return 150.0, 50.0
    s = sorted(scores)
    n = len(s)
    return max(s[int(n * 0.60)], 80.0), max(s[int(n * 0.30)], 20.0)

def category(score, sharp_t, fix_t):
    if score >= sharp_t:
        return "sharp"
    if score >= fix_t:
        return "fixable"
    return "rejected"


# ─── HELPER: BUTTON THAT KEEPS ITS COLORS ON EVERY SYSTEM ────────────────────

class FlatButton(tk.Label):
    """A Label that behaves like a button. Real Tk buttons ignore their colors
    on macOS, which made light text unreadable there."""

    def __init__(self, parent, text, command, bg, fg=None, font=("Helvetica", 11),
                 padx=12, pady=5, **kw):
        super().__init__(parent, text=text, bg=bg, fg=fg or C["text"], font=font,
                         padx=padx, pady=pady, cursor="hand2", **kw)
        self._bg = bg
        self._fg = fg or C["text"]
        self._command = command
        self._enabled = True
        self.bind("<Button-1>", self._click)
        self.bind("<Enter>", lambda e: self._enabled and self.config(bg=C["bg4"]))
        self.bind("<Leave>", lambda e: self.config(bg=self._bg))

    def _click(self, _event):
        if self._enabled and self._command:
            self._command()

    def set_enabled(self, on):
        self._enabled = bool(on)
        self.config(fg=self._fg if on else C["text3"], cursor="hand2" if on else "arrow")

    def set_colors(self, bg, fg=None):
        self._bg = bg
        if fg:
            self._fg = fg
        self.config(bg=bg, fg=self._fg if self._enabled else C["text3"])


# ─── MAIN APP ─────────────────────────────────────────────────────────────────

class LocalShot:
    def __init__(self, root):
        self.root = root
        self.settings = load_settings()
        choice = self.settings.get("language", "auto")       # "auto" follows the computer
        self.lang = choice if choice in LANGUAGES else computer_language()
        self.t = LANGUAGES[self.lang]
        self.advanced = False

        self.image_path = None
        self.base = None              # full-size photo (after rotate / crop / resize)
        self.preview_base = None      # small copy used while editing
        self.exif = None
        self.photo_image = None
        self.folder_images = []
        self.thumb_cache = {}
        self.cells = {}
        self._strip_job = None
        self._strip_queue = []

        self.focus = {}               # Focus Check results per photo
        self.focus_limits = None
        self.focus_show = set()       # colours switched on; empty = everything, in shooting order
        self._scan = None

        self.zoom = None              # None = fit the window; 1.0 = 100 %
        self.center = None
        self.compare = False
        self._view = None
        self._render_job = None
        self._proc_cache = (None, None)
        self._pan_from = None

        self._cropping = False
        self.crop_box = None          # the crop frame, in pixels of the photo
        self._crop_mode = None
        self.picking_grey = False

        # Adjustment vars
        self.brightness_var  = tk.DoubleVar(value=1.0)
        self.contrast_var    = tk.DoubleVar(value=1.0)
        self.exposure_var    = tk.DoubleVar(value=0.0)
        self.whites_var      = tk.DoubleVar(value=0.0)
        self.blacks_var      = tk.DoubleVar(value=0.0)
        self.highlights_var  = tk.DoubleVar(value=0.0)
        self.shadows_var     = tk.DoubleVar(value=0.0)
        self.saturation_var  = tk.DoubleVar(value=0.0)
        self.temperature_var = tk.DoubleVar(value=0.0)
        self.tint_var        = tk.DoubleVar(value=0.0)
        self.sharpening_var  = tk.DoubleVar(value=0.0)
        self.dehaze_var      = tk.DoubleVar(value=0.0)

        self._setup_window()
        self._build_ui()
        self._bind_keys()
        if self.settings.get("quickstart_at_start", True):
            self.root.after(500, self.show_quickstart)      # the first time, and until switched off

    def _setup_window(self):
        self.root.title(self.t["title"] + "  ·  " + APP_VERSION)
        self.root.configure(bg=C["bg"])
        # never taller or wider than the screen, so nothing hides under the Dock
        sw, sh = self.root.winfo_screenwidth(), self.root.winfo_screenheight()
        w, h = min(1280, sw - 40), min(800, sh - 110)
        self.root.geometry(f"{w}x{h}+{max(0, (sw - w) // 2)}+20")
        self.root.minsize(900, 540)

    def _bind_keys(self):
        r = self.root
        r.bind("<Left>", lambda e: self.show_neighbor(-1))
        r.bind("<Right>", lambda e: self.show_neighbor(1))
        r.bind("<Delete>", lambda e: self.delete_current())
        r.bind("<BackSpace>", lambda e: self.delete_current())      # the Mac delete key
        r.bind("<Escape>", lambda e: self.cancel_crop())
        r.bind("<Return>", lambda e: self._cropping and self.apply_crop())
        for key in ("<plus>", "<equal>", "<KP_Add>"):
            r.bind(key, lambda e: self.zoom_by(1.5))
        for key in ("<minus>", "<KP_Subtract>"):
            r.bind(key, lambda e: self.zoom_by(1 / 1.5))
        r.bind("<Key-0>", lambda e: self.zoom_fit())
        r.bind("<Key-1>", lambda e: self.zoom_to(1.0))
        r.protocol("WM_DELETE_WINDOW", self._quit)

    def _quit(self):
        if self._scan:
            self._scan["stop"] = True
        self.root.destroy()

    # ─── UI BUILD ─────────────────────────────────────────────────────────────

    def _build_ui(self):
        self._build_topbar()
        self._build_statusbar()
        self._build_body()

    def _build_topbar(self):
        bar = tk.Frame(self.root, bg=C["bg2"], height=52)
        bar.pack(fill=tk.X)
        bar.pack_propagate(False)

        tk.Label(bar, text="LocalShot",
                 bg=C["bg2"], fg=C["accent"],
                 font=("Helvetica", 15, "bold")).pack(side=tk.LEFT, padx=20)

        self._topbtn(bar, self.t["open_folder"], self.open_folder, C["bg3"]).pack(side=tk.LEFT, padx=4, pady=8)
        self._topbtn(bar, self.t["open"], self.open_image, C["bg3"]).pack(side=tk.LEFT, padx=4, pady=8)
        self._topbtn(bar, self.t["save"], self.save_image, C["success"]).pack(side=tk.LEFT, padx=4, pady=8)

        right = tk.Frame(bar, bg=C["bg2"])
        right.pack(side=tk.RIGHT, padx=16)

        FlatButton(right, "?", self.show_quickstart, C["bg3"]).pack(side=tk.LEFT, padx=(0, 6))
        FlatButton(right, "☕ Ko-fi", self.open_kofi, C["accent"], fg="#000000").pack(side=tk.LEFT, padx=(0, 12))
        auto = self.t["auto_lang"]
        chosen = self.settings.get("language", "auto")
        self.lang_var = tk.StringVar(value=auto if chosen not in LANGUAGES else self.lang)
        lang_cb = ttk.Combobox(right, textvariable=self.lang_var,
                                values=[auto] + list(LANGUAGES.keys()),
                                width=11, state="readonly")
        lang_cb.pack(side=tk.LEFT, padx=(0, 12))
        lang_cb.bind("<<ComboboxSelected>>", self._change_language)

        self.mode_btn = FlatButton(
            right, (self.t["simple_mode"] if self.advanced else self.t["advanced_mode"]),
            self._toggle_mode, C["bg3"])
        self.mode_btn.pack(side=tk.LEFT)

    def _topbtn(self, parent, text, cmd, bg):
        return FlatButton(parent, text, cmd, bg)

    def _build_body(self):
        self.body = tk.Frame(self.root, bg=C["bg"])
        self.body.pack(fill=tk.BOTH, expand=True)

        self._build_filmstrip()
        self._build_right_panel()
        self._build_canvas_area()

    def _build_filmstrip(self):
        """Left side — Focus Check and the folder thumbnails"""
        self.filmstrip_frame = tk.Frame(self.body, bg=C["bg2"], width=STRIP_W)
        self.filmstrip_frame.pack(side=tk.LEFT, fill=tk.Y)
        self.filmstrip_frame.pack_propagate(False)

        # Focus Check
        tk.Label(self.filmstrip_frame, text=self.t["focus_title"],
                 bg=C["bg2"], fg=C["accent"],
                 font=("Helvetica", 9, "bold")).pack(pady=(8, 2))
        scanning = bool(self._scan)
        self.focus_btn = FlatButton(self.filmstrip_frame,
                                    self.t["stop"] if scanning else self.t["focus_run"],
                                    self.run_focus_check, C["bg3"], font=("Helvetica", 10), padx=6)
        self.focus_btn.pack(fill=tk.X, padx=6, pady=2)
        self.focus_summary = tk.Label(self.filmstrip_frame, text="", bg=C["bg2"], fg=C["text2"],
                                      font=("Helvetica", 9), wraplength=STRIP_W - 12, justify=tk.CENTER)
        self.focus_summary.pack(fill=tk.X, padx=4)
        # one strip of four toggles: shooting order, greens, yellows, reds
        show_row = tk.Frame(self.filmstrip_frame, bg=C["bg2"])
        show_row.pack(fill=tk.X, padx=6, pady=2)
        show_row.columnconfigure(0, weight=1, uniform="show")
        show_row.columnconfigure(1, weight=1, uniform="show")
        self.order_btn = FlatButton(show_row, self.t["order"], self.show_order, C["bg3"],
                                    font=("Helvetica", 9, "bold"), padx=2, pady=4)
        self.order_btn.grid(row=0, column=0, sticky="ew", padx=1, pady=1)
        self.show_btns = {}
        for cat, cell in (("sharp", (0, 1)), ("fixable", (1, 0)), ("rejected", (1, 1))):
            btn = FlatButton(show_row, self._show_name(cat), lambda c=cat: self.toggle_group(c), C["bg3"],
                             fg=FOCUS_COLORS[cat], font=("Helvetica", 9, "bold"), padx=2, pady=4)
            btn.grid(row=cell[0], column=cell[1], sticky="ew", padx=1, pady=1)
            self.show_btns[cat] = btn
        self.recover_btn = FlatButton(self.filmstrip_frame, self.t["recover"], self.recover_current,
                                      C["bg3"], font=("Helvetica", 10), padx=6)
        self.recover_btn.pack(fill=tk.X, padx=6, pady=2)
        self.trash_btn = FlatButton(self.filmstrip_frame, self.t["trash_rejected"], self.trash_rejected,
                                    C["bg3"], fg="#ff8a80", font=("Helvetica", 10), padx=6)
        self.trash_btn.pack(fill=tk.X, padx=6, pady=2)

        self.folder_lbl = tk.Label(self.filmstrip_frame, text=self.t["folder"],
                                   bg=C["bg2"], fg=C["text3"],
                                   font=("Helvetica", 9, "bold"))
        self.folder_lbl.pack(pady=(8, 2))

        # Scrollable canvas for thumbs
        self.strip_canvas = tk.Canvas(self.filmstrip_frame,
                                       bg=C["bg2"], width=STRIP_W - 18,
                                       highlightthickness=0)
        strip_scroll = ttk.Scrollbar(self.filmstrip_frame,
                                      orient=tk.VERTICAL,
                                      command=self.strip_canvas.yview)
        self.strip_canvas.configure(yscrollcommand=strip_scroll.set)
        strip_scroll.pack(side=tk.RIGHT, fill=tk.Y)
        self.strip_canvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.strip_inner = tk.Frame(self.strip_canvas, bg=C["bg2"])
        self.strip_canvas.create_window((0, 0), window=self.strip_inner, anchor=tk.NW)
        self.strip_inner.bind("<Configure>",
                               lambda e: self.strip_canvas.configure(
                                   scrollregion=self.strip_canvas.bbox("all")))
        self._wheel_scroll(self.strip_canvas, self.filmstrip_frame)

        self.strip_label = tk.Label(self.strip_inner,
                                     text=self.t["strip_empty"],
                                     bg=C["bg2"], fg=C["text3"],
                                     font=("Helvetica", 9),
                                     justify=tk.CENTER)
        self.strip_label.pack(pady=20, padx=30)
        self._update_focus_controls()

    def _build_canvas_area(self):
        self.canvas_wrap = tk.Frame(self.body, bg=C["bg"])
        self.canvas_wrap.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Top bar: always visible, never under the Dock
        nav = tk.Frame(self.canvas_wrap, bg=C["bg2"])
        nav.pack(fill=tk.X)
        FlatButton(nav, "◀  " + self.t["prev"], lambda: self.show_neighbor(-1), C["bg3"]).pack(side=tk.LEFT, padx=4, pady=4)
        FlatButton(nav, "✖  " + self.t["delete"], self.delete_current, C["bg3"],
                   fg="#ff8a80", font=("Helvetica", 11, "bold")).pack(side=tk.RIGHT, padx=4, pady=4)
        FlatButton(nav, self.t["next"] + "  ▶", lambda: self.show_neighbor(1), C["bg3"]).pack(side=tk.RIGHT, padx=4, pady=4)
        self.info_lbl = tk.Label(nav, text="", bg=C["bg2"], fg=C["accent"],
                                 font=("Helvetica", 11, "bold"))
        self.info_lbl.pack(side=tk.LEFT, fill=tk.X, expand=True)

        zbar = tk.Frame(self.canvas_wrap, bg=C["bg"])
        zbar.pack(fill=tk.X)
        zin = tk.Frame(zbar, bg=C["bg"])
        zin.pack()
        FlatButton(zin, "−", lambda: self.zoom_by(1 / 1.5), C["bg3"], padx=14, pady=3).pack(side=tk.LEFT, padx=2, pady=3)
        FlatButton(zin, self.t["fit"], self.zoom_fit, C["bg3"], pady=3).pack(side=tk.LEFT, padx=2)
        FlatButton(zin, "100%", lambda: self.zoom_to(1.0), C["bg3"], pady=3).pack(side=tk.LEFT, padx=2)
        FlatButton(zin, "+", lambda: self.zoom_by(1.5), C["bg3"], padx=14, pady=3).pack(side=tk.LEFT, padx=2)
        self.zoom_lbl = tk.Label(zin, text=self.t["fit"], bg=C["bg"], fg=C["text2"],
                                 font=("Helvetica", 10), width=8)
        self.zoom_lbl.pack(side=tk.LEFT, padx=6)
        self.compare_btn = FlatButton(zin, self.t["before_after"], self.toggle_compare, C["bg3"], pady=3)
        self.compare_btn.pack(side=tk.LEFT, padx=2)
        self._paint_compare_btn()

        self.canvas = tk.Canvas(self.canvas_wrap, bg=C["bg"],
                                 cursor="crosshair", highlightthickness=0)
        self.canvas.pack(fill=tk.BOTH, expand=True)

        self.canvas.create_text(400, 300,
                                 text=self.t["open_prompt"],
                                 fill=C["text3"], font=("Helvetica", 14),
                                 justify=tk.CENTER, tags="welcome")

        self.canvas.bind("<Configure>", lambda e: self._schedule_render())
        self.canvas.bind("<ButtonPress-1>",   self._press)
        self.canvas.bind("<B1-Motion>",        self._drag)
        self.canvas.bind("<ButtonRelease-1>",  self._release)
        self.canvas.bind("<Motion>",           self._hover)
        self.canvas.bind("<MouseWheel>", self._wheel_zoom)
        self.canvas.bind("<Button-4>", lambda e: self.zoom_by(1.25, (e.x, e.y)))
        self.canvas.bind("<Button-5>", lambda e: self.zoom_by(1 / 1.25, (e.x, e.y)))

    def _build_right_panel(self):
        """Right panel — adjustments"""
        self.right = tk.Frame(self.body, bg=C["bg2"], width=240)
        self.right.pack(side=tk.RIGHT, fill=tk.Y)
        self.right.pack_propagate(False)

        rcanvas = tk.Canvas(self.right, bg=C["bg2"],
                             highlightthickness=0, width=238)
        rscroll = ttk.Scrollbar(self.right, orient=tk.VERTICAL,
                                  command=rcanvas.yview)
        rcanvas.configure(yscrollcommand=rscroll.set)
        rscroll.pack(side=tk.RIGHT, fill=tk.Y)
        rcanvas.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        self.adj_frame = tk.Frame(rcanvas, bg=C["bg2"])
        adj_window = rcanvas.create_window((0, 0), window=self.adj_frame, anchor=tk.NW)
        rcanvas.bind("<Configure>", lambda e: rcanvas.itemconfigure(adj_window, width=e.width))
        self.adj_frame.bind("<Configure>",
                             lambda e: rcanvas.configure(
                                 scrollregion=rcanvas.bbox("all")))
        self._wheel_scroll(rcanvas, self.right)

        self._build_simple_adjustments()
        self._build_advanced_adjustments()
        self._build_transform_section()

        if self.advanced:
            self.advanced_section.pack(fill=tk.X, after=self.simple_section)

    def _wheel_scroll(self, target, area):
        """Mouse wheel scrolls this list while the pointer is over it."""
        def on_wheel(e):
            if getattr(e, "num", 0) == 4:
                step = -2
            elif getattr(e, "num", 0) == 5:
                step = 2
            else:
                step = -int(e.delta / 120) if abs(e.delta) >= 120 else -int(e.delta)
            target.yview_scroll(step, "units")
            return "break"
        def enter(_e):
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                area.bind_all(seq, on_wheel)
        def leave(_e):
            for seq in ("<MouseWheel>", "<Button-4>", "<Button-5>"):
                area.unbind_all(seq)
        area.bind("<Enter>", enter)
        area.bind("<Leave>", leave)

    def _section_label(self, parent, text):
        f = tk.Frame(parent, bg=C["bg3"])
        f.pack(fill=tk.X, padx=0, pady=(8, 0))
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

        def show(*_a):
            val_lbl.config(text=f"{var.get():.0f}" if resolution >= 1
                           else f"{var.get():.2f}")
        def moved(*_a):
            self._schedule_render()

        tk.Scale(f, from_=from_, to=to, resolution=resolution,
                  orient=tk.HORIZONTAL, variable=var,
                  bg=C["bg2"], fg=C["text"], troughcolor=C["bg4"],
                  highlightthickness=0, sliderrelief=tk.FLAT,
                  activebackground=C["accent"], showvalue=False,
                  command=moved).pack(fill=tk.X)
        trace = var.trace_add("write", show)
        val_lbl.bind("<Destroy>", lambda e: var.trace_remove("write", trace))
        show()

    def _build_simple_adjustments(self):
        self.simple_section = tk.Frame(self.adj_frame, bg=C["bg2"])
        self.simple_section.pack(fill=tk.X)

        self._section_label(self.simple_section, self.t["basic"])
        FlatButton(self.simple_section, "✨  " + self.t["auto"], self.auto_tone,
                   C["bg3"], padx=8, pady=5).pack(fill=tk.X, padx=12, pady=(6, 2))
        self._slider(self.simple_section, self.t["brightness"], self.brightness_var, 0.1, 3.0, 0.05)
        self._slider(self.simple_section, self.t["contrast"],   self.contrast_var,   0.1, 3.0, 0.05)
        self._slider(self.simple_section, self.t["exposure"],   self.exposure_var,  -100, 100, 1)

    def _build_advanced_adjustments(self):
        self.advanced_section = tk.Frame(self.adj_frame, bg=C["bg2"])

        self._section_label(self.advanced_section, self.t["tone"])
        self._slider(self.advanced_section, self.t["highlights"], self.highlights_var, -100, 100, 1)
        self._slider(self.advanced_section, self.t["shadows"],    self.shadows_var,    -100, 100, 1)
        self._slider(self.advanced_section, self.t["whites"], self.whites_var, -100, 100, 1)
        self._slider(self.advanced_section, self.t["blacks"], self.blacks_var, -100, 100, 1)

        self._section_label(self.advanced_section, self.t["color"])
        self.grey_btn = FlatButton(self.advanced_section, self.t["grey_picker"], self.toggle_grey,
                                   C["bg3"], padx=8, pady=5)
        self.grey_btn.pack(fill=tk.X, padx=12, pady=(6, 2))
        self._paint_grey_btn()
        self._slider(self.advanced_section, self.t["temperature"], self.temperature_var, -100, 100, 1)
        self._slider(self.advanced_section, self.t["tint"],        self.tint_var,        -100, 100, 1)
        self._slider(self.advanced_section, self.t["saturation"],  self.saturation_var,  -100, 100, 1)

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
            ("↔", self.flip_h),       ("↕", self.flip_v),
        ]
        for i, (icon, cmd) in enumerate(btns):
            FlatButton(btn_grid, icon, cmd, C["bg3"], font=("Helvetica", 16),
                       padx=10, pady=4).grid(row=0, column=i, padx=2)

        self.crop_btn = FlatButton(self.transform_section, "✂  " + self.t["crop"], self.start_crop,
                                   C["bg3"], padx=8, pady=6)
        self.crop_btn.pack(fill=tk.X, padx=12, pady=3)
        self.crop_cancel_btn = FlatButton(self.transform_section, self.t["cancel"], self.cancel_crop,
                                          C["bg3"], padx=8, pady=6)
        self._paint_crop_btn()
        FlatButton(self.transform_section, self.t["resize"], self.resize_dialog,
                   C["bg3"], padx=8, pady=6).pack(fill=tk.X, padx=12, pady=3)
        FlatButton(self.transform_section, self.t["reset"], self.reset_all,
                   C["bg2"], fg=C["text2"], padx=8, pady=6).pack(fill=tk.X, padx=12, pady=(12, 6))

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
        self.thanks_lbl = tk.Label(bar, text=self.t["kofi_thanks"], bg=C["bg2"], fg=C["accent"],
                                   font=("Helvetica", 10, "bold"), cursor="hand2")
        self.thanks_lbl.bind("<Button-1>", lambda e: self.open_kofi())

    # ─── KO-FI & QUICK START ──────────────────────────────────────────────────

    def open_kofi(self):
        webbrowser.open(KOFI)

    def _show_thanks(self):
        try:
            self.thanks_lbl.config(text=self.t["kofi_thanks"])
            self.thanks_lbl.pack(side=tk.LEFT, padx=10)
        except tk.TclError:
            pass

    def show_quickstart(self):
        t = self.t
        win = tk.Toplevel(self.root)
        win.title(t["quick_start"])
        win.configure(bg=C["bg2"])
        sh = self.root.winfo_screenheight()
        win.geometry(f"600x{min(800, sh - 90)}+60+30")
        win.transient(self.root)
        tk.Label(win, text=t["quick_start"], bg=C["bg2"], fg=C["accent"],
                 font=("Helvetica", 20, "bold")).pack(anchor="w", padx=20, pady=(16, 2))
        tk.Label(win, text=t["qs_intro"], bg=C["bg2"], fg=C["text"], font=("Helvetica", 12),
                 wraplength=530, justify="left").pack(anchor="w", padx=20, pady=(0, 10))
        body = tk.Frame(win, bg=C["bg2"])
        body.pack(fill=tk.BOTH, expand=True, padx=20)
        for n in range(1, 8):
            row = tk.Frame(body, bg=C["bg2"])
            row.pack(fill=tk.X, pady=5)
            tk.Label(row, text=str(n), bg=C["accent"], fg="#000000", width=2,
                     font=("Helvetica", 12, "bold")).pack(side=tk.LEFT, anchor="n", padx=(0, 10))
            col = tk.Frame(row, bg=C["bg2"])
            col.pack(side=tk.LEFT, fill=tk.X, expand=True)
            tk.Label(col, text=t[f"qs{n}"], bg=C["bg2"], fg=C["text"],
                     font=("Helvetica", 13, "bold"), anchor="w").pack(fill=tk.X)
            tk.Label(col, text=t[f"qs{n}b"], bg=C["bg2"], fg=C["text2"], font=("Helvetica", 11),
                     wraplength=480, justify="left", anchor="w").pack(fill=tk.X)
        tk.Label(win, text=t["qs_tip"], bg=C["bg2"], fg="#2EC4B6", font=("Helvetica", 11),
                 wraplength=530, justify="left").pack(anchor="w", padx=20, pady=(6, 4))
        bottom = tk.Frame(win, bg=C["bg2"])
        bottom.pack(fill=tk.X, padx=20, pady=(4, 14))
        at_start = tk.BooleanVar(value=self.settings.get("quickstart_at_start", True))

        def toggled():
            self.settings["quickstart_at_start"] = bool(at_start.get())
            save_settings(self.settings)

        tk.Checkbutton(bottom, text=t["show_at_start"], variable=at_start, command=toggled,
                       bg=C["bg2"], fg=C["text2"], selectcolor=C["bg3"], activebackground=C["bg2"],
                       font=("Helvetica", 11)).pack(side=tk.LEFT)
        FlatButton(bottom, t["got_it"], win.destroy, C["accent"], fg="#000000").pack(side=tk.RIGHT)
        win.lift()
        win.focus_set()

    # ─── MODE & LANGUAGE ──────────────────────────────────────────────────────

    def _toggle_mode(self):
        self.advanced = not self.advanced
        if self.advanced:
            self.advanced_section.pack(fill=tk.X, after=self.simple_section)
            self.mode_btn.config(text=self.t["simple_mode"])
        else:
            self.advanced_section.pack_forget()
            self.mode_btn.config(text=self.t["advanced_mode"])

    def _change_language(self, event=None):
        picked = self.lang_var.get()
        if picked in LANGUAGES:
            self.settings["language"] = picked
            self.lang = picked
        else:                                   # Automatic: like the computer
            self.settings["language"] = "auto"
            self.lang = computer_language()
        save_settings(self.settings)
        self.t = LANGUAGES[self.lang]
        self.root.title(self.t["title"] + "  ·  " + APP_VERSION)
        if self._strip_job:
            self.root.after_cancel(self._strip_job)
            self._strip_job = None
        if self._render_job:
            self.root.after_cancel(self._render_job)
            self._render_job = None
        for w in self.root.winfo_children():
            w.destroy()
        self.cells = {}
        self._build_ui()
        if self.folder_images:
            self._populate_filmstrip()
        self._update_status()
        self._schedule_render()

    # ─── FOLDER & FILMSTRIP ───────────────────────────────────────────────────

    def _show_name(self, cat):
        """The word on a colour button, so nobody has to guess what a colour means."""
        word = self.t[cat]
        return word.capitalize() if word.isupper() else word

    def _shown(self):
        """Photos in the strip: everything in shooting order, or the colours switched on."""
        if not self.focus or not self.focus_show:
            return self.folder_images
        # greens, then yellows, then reds; the sort is stable, so shooting order
        # is kept inside each colour, and files on disk are never touched
        rank = {"sharp": 0, "fixable": 1, "rejected": 2}
        chosen = [p for p in self.folder_images if self.focus.get(p, {}).get("cat") in self.focus_show]
        return sorted(chosen, key=lambda p: rank[self.focus[p]["cat"]])

    def show_order(self):
        if self.focus:
            self.focus_show.clear()
            self._show_changed()

    def toggle_group(self, cat):
        if self.focus:
            self.focus_show.symmetric_difference_update({cat})
            self._show_changed()

    def _show_changed(self):
        self._update_focus_controls()
        self._populate_filmstrip()
        shown = self._shown()
        if shown and self.image_path not in shown:
            self._load_image(shown[0])

    def open_folder(self, folder=None):
        folder = folder or filedialog.askdirectory()
        if not folder:
            return
        self.stop_focus_check()
        files = [os.path.join(folder, name) for name in sorted(os.listdir(folder), key=str.lower)
                 if name.lower().endswith(IMG_EXTENSIONS) and not name.startswith(".")]
        self.folder_images = files
        self.thumb_cache = {}
        self.focus = {}
        self.focus_limits = None
        self.focus_show.clear()
        self._update_focus_controls()
        self._populate_filmstrip()
        if files:
            self._load_image(files[0])

    def _populate_filmstrip(self):
        if self._strip_job:
            self.root.after_cancel(self._strip_job)
            self._strip_job = None
        for w in self.strip_inner.winfo_children():
            w.destroy()
        self.cells = {}
        self.strip_canvas.yview_moveto(0)
        self._strip_queue = list(self._shown())
        self._strip_total = len(self._strip_queue)
        if not self._strip_queue:
            tk.Label(self.strip_inner, text=self.t["strip_empty"] if not self.folder_images else "—",
                     bg=C["bg2"], fg=C["text3"], font=("Helvetica", 9),
                     justify=tk.CENTER).pack(pady=20, padx=30)
        self._strip_step()

    def _strip_step(self):
        """Adds thumbnails a few at a time so a big folder never freezes the window."""
        self._strip_job = None
        made = 0
        while self._strip_queue and made < 8:
            path = self._strip_queue.pop(0)
            fresh = path not in self.thumb_cache
            self._add_thumb(path)
            made += 1 if fresh else 0.1
        if self._strip_queue:
            done = self._strip_total - len(self._strip_queue)
            self.folder_lbl.config(text=self.t["loading"].format(i=done, n=self._strip_total))
            self._strip_job = self.root.after(1, self._strip_step)
        else:
            shown, total = self._strip_total, len(self.folder_images)
            self.folder_lbl.config(
                text=f"{self.t['folder']}  {shown}" if shown == total
                else f"{self.t['folder']}  {shown} / {total}")
            self._highlight()

    def _make_thumb(self, path):
        try:
            with Image.open(path) as img:
                img.draft("RGB", (THUMB_W * 2, THUMB_H * 2))      # fast for big JPEGs
                img = ImageOps.exif_transpose(img).convert("RGB")
                img.thumbnail((THUMB_W, THUMB_H), Image.BILINEAR)
                thumb = Image.new("RGB", (THUMB_W, THUMB_H), (30, 30, 30))
                thumb.paste(img, ((THUMB_W - img.width) // 2, (THUMB_H - img.height) // 2))
        except Exception:
            thumb = Image.new("RGB", (THUMB_W, THUMB_H), (60, 30, 30))
        return ImageTk.PhotoImage(thumb)

    def _add_thumb(self, path):
        tk_img = self.thumb_cache.get(path)
        if tk_img is None:
            tk_img = self.thumb_cache[path] = self._make_thumb(path)
        frame = tk.Frame(self.strip_inner, bg=C["bg2"], cursor="hand2",
                         highlightthickness=3, highlightbackground=C["bg2"])
        frame.pack(pady=2, padx=6)
        lbl = tk.Label(frame, image=tk_img, bg=C["bg3"], cursor="hand2", bd=0)
        lbl.pack()
        name = os.path.basename(path)
        name_lbl = tk.Label(frame, text=name if len(name) <= 22 else name[:20] + "…",
                            bg=C["bg2"], fg=C["text3"], font=("Helvetica", 8))
        name_lbl.pack()
        cap = tk.Label(frame, text="", bg=C["bg2"], font=("Helvetica", 9, "bold"))
        for w in (frame, lbl, name_lbl, cap):
            w.bind("<Button-1>", lambda e, p=path: self._load_image(p))
        self.cells[path] = (frame, cap)
        self._set_caption(path)

    def _set_caption(self, path):
        cell = self.cells.get(path)
        if not cell:
            return
        info = self.focus.get(path)
        if info:
            cell[1].config(text=f"● {self.t[info['cat']]}  {info['score']:.0f}",
                           fg=FOCUS_COLORS[info["cat"]])
            cell[1].pack()
        else:
            cell[1].pack_forget()

    def _highlight(self):
        """Light up the thumbnail being edited and say which photo it is."""
        for path, (frame, _cap) in self.cells.items():
            frame.config(highlightbackground=C["accent"] if path == self.image_path else C["bg2"])
        shown = self._shown()
        text = ""
        if self.image_path:
            text = os.path.basename(self.image_path)
            if self.image_path in shown:
                text += f"   ·   {shown.index(self.image_path) + 1} {self.t['of']} {len(shown)}"
            info = self.focus.get(self.image_path)
            if info:
                text += f"   ·   {self.t[info['cat']]} {info['score']:.0f}"
                if info["cat"] != "sharp" and info["blur"] != "unknown":
                    kind = self.t["motion_blur"] if info["blur"] == "motion" else self.t["focus_error"]
                    text += f" ({kind}, {shutter_str(info['shutter'])})"
        self.info_lbl.config(text=text)
        cell = self.cells.get(self.image_path)
        if cell:
            self.root.after_idle(lambda f=cell[0]: self._scroll_to(f))

    def _scroll_to(self, frame):
        try:
            total = max(1, self.strip_inner.winfo_height())
            top, bottom = frame.winfo_y(), frame.winfo_y() + frame.winfo_height()
            view_top = self.strip_canvas.canvasy(0)
            view_bottom = view_top + self.strip_canvas.winfo_height()
            if top < view_top:
                self.strip_canvas.yview_moveto(top / total)
            elif bottom > view_bottom:
                self.strip_canvas.yview_moveto((bottom - self.strip_canvas.winfo_height()) / total)
        except tk.TclError:
            pass

    def show_neighbor(self, step):
        shown = self._shown()
        if not shown:
            return
        index = shown.index(self.image_path) + step if self.image_path in shown else 0
        if 0 <= index < len(shown):
            self._load_image(shown[index])

    # ─── DELETE ───────────────────────────────────────────────────────────────

    def _to_trash(self, path):
        from send2trash import send2trash
        send2trash(os.path.normpath(path))

    def _forget(self, path):
        if path in self.folder_images:
            self.folder_images.remove(path)
        self.focus.pop(path, None)
        self.thumb_cache.pop(path, None)

    def _clear_photo(self, message):
        self.image_path = None
        self.base = None
        self.preview_base = None
        self.canvas.delete("all")
        self.canvas.create_text(self.canvas.winfo_width() // 2, self.canvas.winfo_height() // 2,
                                text=message, fill=C["text3"], font=("Helvetica", 14))
        self.size_lbl.config(text="")

    def delete_current(self):
        path = self.image_path
        if not path or not self.base:
            return
        if not messagebox.askyesno(self.t["delete"],
                                   self.t["delete_confirm"].format(name=os.path.basename(path))):
            return
        try:
            self._to_trash(path)
        except Exception as ex:
            messagebox.showerror(self.t["error"], f"{self.t['delete_fail']}\n\n{ex}")
            return
        shown = self._shown()
        index = shown.index(path) if path in shown else 0
        self._forget(path)
        self._clear_photo(self.t["moved_trash"])
        self._update_focus_controls()
        self._populate_filmstrip()
        shown = self._shown()
        if shown:
            self._load_image(shown[min(index, len(shown) - 1)])
        else:
            self._highlight()

    # ─── FOCUS CHECK ──────────────────────────────────────────────────────────

    def stop_focus_check(self):
        if self._scan:
            self._scan["stop"] = True
            self._scan = None
        try:
            self.focus_btn.config(text=self.t["focus_run"])
        except tk.TclError:
            pass

    def run_focus_check(self):
        if self._scan:                         # the button says Stop while scanning
            self.stop_focus_check()
            self.focus_summary.config(text=self.t["stopped"], fg=C["text2"])
            return
        if not self.folder_images:
            messagebox.showinfo(self.t["focus_run"], self.t["need_folder"])
            return
        scan = {"stop": False, "done": 0, "results": {}, "finished": False,
                "files": list(self.folder_images)}
        self._scan = scan

        def work():
            for path in scan["files"]:
                if scan["stop"]:
                    return
                scan["results"][path] = {"score": score_image(path), "shutter": get_shutter(path)}
                scan["done"] += 1
            scan["finished"] = True

        threading.Thread(target=work, daemon=True).start()
        self.focus_btn.config(text=self.t["stop"])
        self._poll_scan(scan)

    def _poll_scan(self, scan):
        if self._scan is not scan:
            return
        if not scan["finished"]:
            try:
                self.focus_summary.config(
                    text=self.t["checking"].format(i=scan["done"], n=len(scan["files"])), fg=C["text2"])
            except tk.TclError:
                pass
            self.root.after(120, lambda: self._poll_scan(scan))
            return
        self._scan = None
        results = {p: r for p, r in scan["results"].items() if p in self.folder_images}
        limits = calibrate([r["score"] for r in results.values()])
        for r in results.values():
            r["cat"] = category(r["score"], *limits)
            r["blur"] = blur_type(r["shutter"])
        self.focus = results
        self.focus_limits = limits
        self.focus_btn.config(text=self.t["focus_run"])
        self._update_focus_controls()
        for path in self.cells:
            self._set_caption(path)
        self._highlight()

    def _update_focus_controls(self):
        have = bool(self.focus)
        if not have:
            self.focus_show.clear()
        count = {"sharp": 0, "fixable": 0, "rejected": 0}
        for r in self.focus.values():
            count[r["cat"]] += 1
        self.order_btn.set_enabled(have)
        if have and not self.focus_show:
            self.order_btn.set_colors(C["accent"], C["bg"])
        else:
            self.order_btn.set_colors(C["bg3"], C["text"])
        for cat, btn in self.show_btns.items():
            btn.config(text=f"{self._show_name(cat)} {count[cat]}" if have else self._show_name(cat))
            if cat in self.focus_show:
                btn.set_colors(FOCUS_COLORS[cat], "#111111")
            else:
                btn.set_colors(C["bg3"], FOCUS_COLORS[cat])
            btn.set_enabled(have)
        self.recover_btn.set_enabled(have)
        self.trash_btn.set_enabled(have)
        if not have:
            if not self._scan:
                self.focus_summary.config(text="")
            return
        count = {"sharp": 0, "fixable": 0, "rejected": 0}
        for r in self.focus.values():
            count[r["cat"]] += 1
        self.focus_summary.config(
            fg=C["text"],
            text=f"{self.t['sharp']} {count['sharp']}  ·  {self.t['fixable']} {count['fixable']}"
                 f"  ·  {self.t['rejected']} {count['rejected']}")

    def recover_current(self):
        info = self.focus.get(self.image_path)
        if not info or not self.focus_limits:
            messagebox.showinfo(self.t["recover"], self.t["need_scan"])
            return
        sharp_t = self.focus_limits[0]
        deficit = sharp_t - info["score"]
        if deficit <= 0:
            messagebox.showinfo(self.t["recover"], self.t["already_sharp"])
            return
        self.sharpening_var.set(30 if deficit <= sharp_t * 0.3 else 60 if deficit <= sharp_t * 0.7 else 90)
        if not self.advanced:
            self._toggle_mode()                # the Sharpening slider lives in Advanced
        self.compare = True                    # show before | after straight away
        self._paint_compare_btn()
        self._schedule_render()

    def trash_rejected(self):
        rejected = [p for p in self.folder_images if self.focus.get(p, {}).get("cat") == "rejected"]
        if not rejected:
            messagebox.showinfo(self.t["trash_rejected"], self.t["no_rejected"])
            return
        if not messagebox.askyesno(self.t["trash_rejected"],
                                   self.t["trash_confirm"].format(n=len(rejected))):
            return
        failed = 0
        for path in rejected:
            try:
                self._to_trash(path)
            except Exception:
                failed += 1
                continue
            self._forget(path)
        if self.image_path not in self.folder_images:
            self._clear_photo(self.t["moved_trash"])
        self.focus_show.clear()
        self._update_focus_controls()
        self._populate_filmstrip()
        if failed:
            messagebox.showwarning(self.t["error"], f"{self.t['delete_fail']} ({failed})")
        if self.image_path is None and self.folder_images:
            self._load_image(self.folder_images[0])

    # ─── IMAGE LOAD & DISPLAY ─────────────────────────────────────────────────

    def open_image(self):
        path = filedialog.askopenfilename(
            filetypes=[("Images", "*.jpg *.jpeg *.png *.webp *.bmp *.tiff *.tif"),
                       ("All files", "*.*")])
        if path:
            self._load_image(path)

    def _read(self, path):
        with Image.open(path) as img:
            exif = img.getexif()
            img = ImageOps.exif_transpose(img).convert("RGB")     # vertical shots upright
        if 0x0112 in exif:
            exif[0x0112] = 1
        try:
            self.exif = exif.tobytes()
        except Exception:
            self.exif = None
        return img

    def _load_image(self, path):
        try:
            img = self._read(path)
        except Exception as ex:
            messagebox.showerror(self.t["error"], str(ex))
            return
        self.image_path = path
        self._cropping = False
        self.crop_box = None
        self._paint_crop_btn()
        self.picking_grey = False
        self._paint_grey_btn()
        self._reset_vars()
        self._set_base(img)
        self._highlight()

    def _set_base(self, img):
        """A new full-size picture: after loading, rotating, cropping or resizing."""
        self.base = img
        self.preview_base = img.copy()
        self.preview_base.thumbnail((PREVIEW_MAX, PREVIEW_MAX), Image.BILINEAR)
        self.zoom = None
        self.center = None
        self._proc_cache = (None, None)
        self._render()
        self._update_status()

    def _reset_vars(self):
        self.brightness_var.set(1.0)
        self.contrast_var.set(1.0)
        self.exposure_var.set(0.0)
        self.whites_var.set(0.0)
        self.blacks_var.set(0.0)
        self.highlights_var.set(0.0)
        self.shadows_var.set(0.0)
        self.saturation_var.set(0.0)
        self.temperature_var.set(0.0)
        self.tint_var.set(0.0)
        self.sharpening_var.set(0.0)
        self.dehaze_var.set(0.0)

    def _values(self):
        return (self.brightness_var.get(), self.contrast_var.get(), self.exposure_var.get(),
                self.whites_var.get(), self.blacks_var.get(), self.temperature_var.get(),
                self.tint_var.get(), self.dehaze_var.get(), self.sharpening_var.get(),
                self.highlights_var.get(), self.shadows_var.get(), self.saturation_var.get())

    def process(self, img):
        """All the slider corrections, applied to any copy of the photo."""
        bright, contrast, exp, w, b, temp, tint, dh, sh, hl, shd, sat = self._values()
        if bright != 1.0:
            img = ImageEnhance.Brightness(img).enhance(bright)
        if contrast != 1.0:
            img = ImageEnhance.Contrast(img).enhance(contrast)
        if exp != 0:
            img = ImageEnhance.Brightness(img).enhance(max(0.01, 1.0 + exp / 100.0))
        if w != 0 or b != 0:
            img = apply_whites_blacks(img, w, b)
        if hl != 0 or shd != 0:
            img = apply_highlights_shadows(img, hl, shd)
        if temp != 0 or tint != 0:
            img = apply_white_balance(img, temp, tint)
        if sat != 0:
            img = ImageEnhance.Color(img).enhance(1.0 + sat / 100.0)
        if dh > 0:
            img = apply_dehaze(img, dh)
        if sh > 0:
            img = apply_sharpening(img, sh)
        return img

    # ─── GREY PICKER (white balance) ──────────────────────────────────────────

    def _paint_grey_btn(self):
        try:
            if self.picking_grey:
                self.grey_btn.set_colors(C["accent"], C["bg"])
            else:
                self.grey_btn.set_colors(C["bg3"], C["text"])
        except (tk.TclError, AttributeError):
            pass

    def toggle_grey(self):
        if not self.base:
            return
        self.picking_grey = not self.picking_grey
        if self.picking_grey:
            self.cancel_crop()
            self.status_lbl.config(text=self.t["grey_hint"])
        else:
            self._update_status()
        self._paint_grey_btn()

    def _patch_rgb(self, x, y):
        """Average colour of a small patch of the picture on screen, or None."""
        v = self._view
        px, py = int(x - v["x"]), int(y - v["y"])
        if not (0 <= px < v["w"] and 0 <= py < v["h"]):
            return None
        box = (max(0, px - 5), max(0, py - 5), min(v["w"], px + 6), min(v["h"], py + 6))
        return np.asarray(self._display.crop(box), dtype=np.float32).reshape(-1, 3).mean(axis=0)

    def pick_grey(self, x, y):
        """Set Temperature and Tint so the clicked spot has no colour cast."""
        compare, self.compare = self.compare, False      # measure the corrected picture
        self._render()
        rgb = self._patch_rgb(x, y)
        message = None
        if rgb is None:
            message = self.t["grey_hint"]
        elif rgb.mean() < 12 or rgb.mean() > 247:
            message = self.t["grey_bad"]
        else:
            for _round in range(4):                      # set, look at the same spot again, refine
                r, g, b = rgb
                temp = max(-100.0, min(100.0, self.temperature_var.get() + (b - r)))
                moved = (temp - self.temperature_var.get()) * 0.5
                tint = max(-100.0, min(100.0, self.tint_var.get() + (g - (r + moved + b - moved) / 2.0) / 0.5))
                self.temperature_var.set(round(temp))
                self.tint_var.set(round(tint))
                self._render()
                rgb = self._patch_rgb(x, y)
                if rgb is None or (max(rgb) - min(rgb)) < 2.5:
                    break
        self.compare = compare
        self.picking_grey = False
        self._paint_grey_btn()
        self._render()
        if message:
            self.status_lbl.config(text=message)
        else:
            self._update_status()

    def auto_tone(self):
        """One click: exposure, white point, black point, shadows, highlights. A starting point."""
        if not self.preview_base:
            return
        for var in (self.exposure_var, self.highlights_var, self.shadows_var, self.whites_var, self.blacks_var):
            var.set(0.0)
        small = self.preview_base.copy()
        small.thumbnail((800, 800), Image.BILINEAR)
        lum = np.asarray(self.process(small).convert("L"), dtype=np.float32) / 255.0
        gain, hl, sh, wh, bl = auto_tone_values(lum)
        self.exposure_var.set(round((gain - 1.0) * 100))
        self.highlights_var.set(round(hl * 100))
        self.shadows_var.set(round(sh * 100))
        self.whites_var.set(round(wh * 100))
        self.blacks_var.set(round(bl * 100))
        self._schedule_render()

    @staticmethod
    def _split(before, after):
        """Left half before the corrections, right half after."""
        out = after.copy()
        mid = out.width // 2
        out.paste(before.crop((0, 0, mid, before.height)), (0, 0))
        out.paste((255, 255, 255), (max(0, mid - 1), 0, mid + 1, out.height))
        return out

    def _schedule_render(self):
        if self._render_job:
            self.root.after_cancel(self._render_job)
        self._render_job = self.root.after(30, self._render)

    def _apply_all(self):
        self._schedule_render()

    def _refresh_display(self):
        self._render()

    def _render(self):
        self._render_job = None
        if not self.base:
            return
        cw = max(50, self.canvas.winfo_width())
        ch = max(50, self.canvas.winfo_height())
        bw, bh = self.base.size
        if self.zoom is None:
            scale = min(cw / bw, ch / bh, 1.0)
            nw, nh = max(1, int(bw * scale)), max(1, int(bh * scale))
            key = (self._values(), id(self.preview_base), self.compare)
            if self._proc_cache[0] != key:
                shown = self.process(self.preview_base)
                if self.compare:
                    shown = self._split(self.preview_base, shown)
                self._proc_cache = (key, shown)
            display = self._proc_cache[1]
            if display.size != (nw, nh):
                display = display.resize((nw, nh), Image.BILINEAR)
            x0 = y0 = 0
            self.zoom_lbl.config(text=self.t["fit"])
        else:
            s = self.zoom
            vw, vh = min(bw, cw / s), min(bh, ch / s)       # part of the photo on screen
            cx, cy = self.center or (bw / 2.0, bh / 2.0)
            cx = min(max(cx, vw / 2.0), bw - vw / 2.0)
            cy = min(max(cy, vh / 2.0), bh - vh / 2.0)
            self.center = (cx, cy)
            x0, y0 = int(cx - vw / 2.0), int(cy - vh / 2.0)
            x1, y1 = min(bw, x0 + int(round(vw))), min(bh, y0 + int(round(vh)))
            m = 16                                          # margin so edges sharpen cleanly
            ex0, ey0, ex1, ey1 = max(0, x0 - m), max(0, y0 - m), min(bw, x1 + m), min(bh, y1 + m)
            region = self.base.crop((ex0, ey0, ex1, ey1))
            k = min(s, 1.0)
            if k < 1.0:
                region = region.resize((max(1, int(round(region.width * k))),
                                        max(1, int(round(region.height * k)))), Image.BOX)
            box = (int(round((x0 - ex0) * k)), int(round((y0 - ey0) * k)))
            box = box + (box[0] + max(1, int(round((x1 - x0) * k))),
                         box[1] + max(1, int(round((y1 - y0) * k))))
            display = self.process(region).crop(box)
            if self.compare:
                display = self._split(region.crop(box), display)
            if s > 1.0:
                display = display.resize((int(round((x1 - x0) * s)), int(round((y1 - y0) * s))),
                                         Image.NEAREST if s >= 3 else Image.BILINEAR)
            scale = s
            self.zoom_lbl.config(text=f"{s * 100:.0f}%")
        self.photo_image = ImageTk.PhotoImage(display)
        x = (cw - display.width) // 2
        y = (ch - display.height) // 2
        self.canvas.delete("all")
        self._img_item = self.canvas.create_image(x, y, anchor=tk.NW, image=self.photo_image)
        self._display, self._display_dim = display, None
        self._view = {"x": x, "y": y, "scale": scale, "x0": x0, "y0": y0,
                      "w": display.width, "h": display.height}
        self._img_offset = (x, y, scale)
        if self._cropping and self.crop_box:
            self._draw_crop_frame()

    def _update_status(self):
        if self.base:
            w, h = self.base.size
            name = os.path.basename(self.image_path) if self.image_path else ""
            self.status_lbl.config(text=name)
            self.size_lbl.config(text=f"{w} × {h} px")
        else:
            self.size_lbl.config(text="")

    # ─── ZOOM ─────────────────────────────────────────────────────────────────

    def _fit_scale(self):
        bw, bh = self.base.size
        return min(max(50, self.canvas.winfo_width()) / bw, max(50, self.canvas.winfo_height()) / bh)

    def _photo_point(self, pos):
        """Which pixel of the photo is under this spot of the screen."""
        v = self._view
        return (v["x0"] + (pos[0] - v["x"]) / v["scale"], v["y0"] + (pos[1] - v["y"]) / v["scale"])

    def zoom_to(self, scale, pos=None):
        if not self.base:
            return
        fit = self._fit_scale()
        scale = min(scale, max(MAX_ZOOM, fit))
        if scale <= fit * 1.01 and fit <= 1.0:
            return self.zoom_fit()
        v = self._view
        inside = (pos is not None and v and v["x"] <= pos[0] <= v["x"] + v["w"]
                  and v["y"] <= pos[1] <= v["y"] + v["h"])
        if inside:        # keep the spot under the pointer where it is
            px, py = self._photo_point(pos)
            cw, ch = self.canvas.winfo_width(), self.canvas.winfo_height()
            self.center = (px - (pos[0] - cw / 2.0) / scale, py - (pos[1] - ch / 2.0) / scale)
        elif self.center is None:
            self.center = (self.base.width / 2.0, self.base.height / 2.0)
        self.zoom = scale
        self._render()

    def zoom_by(self, factor, pos=None):
        if not self.base:
            return
        self.zoom_to((self.zoom or min(self._fit_scale(), 1.0)) * factor, pos)

    def zoom_fit(self):
        self.zoom = None
        self.center = None
        if self.base:
            self._render()

    def _wheel_zoom(self, e):
        steps = e.delta / 120.0 if abs(e.delta) >= 120 else float(e.delta)   # Windows / Mac
        steps = max(-3.0, min(3.0, steps))
        if steps:
            self.zoom_by(1.2 ** steps, (e.x, e.y))

    def _click_zoom(self, e):
        """Click on the photo: jump to 100 % on that spot; click again for the whole photo."""
        if not self.base or self._cropping:
            return
        if self.picking_grey:
            return self.pick_grey(e.x, e.y)
        if self.zoom is None:
            self.zoom_to(1.0, (e.x, e.y))
        else:
            self.zoom_fit()

    def toggle_compare(self):
        self.compare = not self.compare
        self._paint_compare_btn()
        self._schedule_render()

    def _paint_compare_btn(self):
        if self.compare:
            self.compare_btn.set_colors(C["accent"], C["bg"])
        else:
            self.compare_btn.set_colors(C["bg3"], C["text"])

    # ─── SAVE ─────────────────────────────────────────────────────────────────

    def save_image(self, path=None):
        if not self.base:
            return
        path = path or filedialog.asksaveasfilename(
            defaultextension=".jpg",
            filetypes=[("JPEG", "*.jpg"), ("PNG", "*.png"),
                       ("WebP", "*.webp"), ("BMP", "*.bmp"),
                       ("TIFF", "*.tiff")])
        if not path:
            return
        self.status_lbl.config(text=self.t["saving"])
        self.root.update_idletasks()
        try:
            img = self.process(self.base)              # full size, full quality
            extra = {}
            if self.exif and path.lower().endswith((".jpg", ".jpeg", ".webp", ".tif", ".tiff", ".png")):
                extra["exif"] = self.exif              # keep camera data and captions
            try:
                img.save(path, quality=95, **extra)
            except Exception:
                img.save(path, quality=95)
        except Exception as ex:
            messagebox.showerror(self.t["error"], str(ex))
            self._update_status()
            return
        self.status_lbl.config(text=self.t["saved"])
        self._show_thanks()
        self.root.after(3000, self._update_status)

    # ─── TRANSFORMS ───────────────────────────────────────────────────────────

    def rotate_left(self):
        if self.base:
            self._set_base(self.base.transpose(Image.ROTATE_90))

    def rotate_right(self):
        if self.base:
            self._set_base(self.base.transpose(Image.ROTATE_270))

    def flip_h(self):
        if self.base:
            self._set_base(self.base.transpose(Image.FLIP_LEFT_RIGHT))

    def flip_v(self):
        if self.base:
            self._set_base(self.base.transpose(Image.FLIP_TOP_BOTTOM))

    def reset_all(self):
        if not self.image_path:
            return
        try:
            img = self._read(self.image_path)
        except Exception as ex:
            messagebox.showerror(self.t["error"], str(ex))
            return
        self._reset_vars()
        self._set_base(img)

    # ─── MOUSE ON THE PHOTO: CROP OR MOVE ─────────────────────────────────────

    def _paint_crop_btn(self):
        try:
            if self._cropping:
                self.crop_btn.config(text="✓  " + self.t["apply"])
                self.crop_btn.set_colors(C["accent"], C["bg"])
                self.crop_cancel_btn.pack(fill=tk.X, padx=12, pady=3, after=self.crop_btn)
            else:
                self.crop_btn.config(text="✂  " + self.t["crop"])
                self.crop_btn.set_colors(C["bg3"], C["text"])
                self.crop_cancel_btn.pack_forget()
        except (tk.TclError, AttributeError):
            pass

    def start_crop(self):
        """First press shows an adjustable frame; pressing again applies it."""
        if not self.base:
            return
        if self._cropping:
            return self.apply_crop()
        self.picking_grey = False
        self._paint_grey_btn()
        bw, bh = self.base.size
        self.crop_box = [bw * 0.08, bh * 0.08, bw * 0.92, bh * 0.92]
        self._cropping = True
        self._crop_mode = None
        self.zoom = None
        self.center = None
        self._paint_crop_btn()
        self.status_lbl.config(text=self.t["crop_hint"])
        self._render()

    def apply_crop(self):
        if not (self._cropping and self.crop_box and self.base):
            return
        bw, bh = self.base.size
        x0, y0, x1, y1 = self.crop_box
        box = (max(0, int(round(x0))), max(0, int(round(y0))), min(bw, int(round(x1))), min(bh, int(round(y1))))
        self._cropping = False
        self.crop_box = None
        self._paint_crop_btn()
        self.canvas.config(cursor="crosshair")
        if box[2] - box[0] >= 2 and box[3] - box[1] >= 2 and box != (0, 0, bw, bh):
            self._set_base(self.base.crop(box))
        else:
            self._render()
            self._update_status()

    def cancel_crop(self):
        if self._cropping:
            self._cropping = False
            self.crop_box = None
            self._crop_mode = None
            self._paint_crop_btn()
            self.canvas.config(cursor="crosshair")
            self._render()
            self._update_status()

    def _box_on_screen(self):
        v = self._view
        x0, y0, x1, y1 = self.crop_box
        return (v["x"] + (x0 - v["x0"]) * v["scale"], v["y"] + (y0 - v["y0"]) * v["scale"],
                v["x"] + (x1 - v["x0"]) * v["scale"], v["y"] + (y1 - v["y0"]) * v["scale"])

    def _draw_crop_frame(self):
        c, v = self.canvas, self._view
        c.delete("crop")
        sx0, sy0, sx1, sy1 = self._box_on_screen()
        # darken everything outside the frame (done in the picture itself, so it
        # looks the same on Mac, Windows and Linux)
        if self._display_dim is None:
            self._display_dim = self._display.point(lambda p: p * 0.35)
        shaded = self._display_dim.copy()
        box = (max(0, int(sx0 - v["x"])), max(0, int(sy0 - v["y"])),
               min(v["w"], int(sx1 - v["x"])), min(v["h"], int(sy1 - v["y"])))
        if box[2] > box[0] and box[3] > box[1]:
            shaded.paste(self._display.crop(box), box[:2])
        self.photo_image = ImageTk.PhotoImage(shaded)
        c.itemconfigure(self._img_item, image=self.photo_image)
        c.create_rectangle(sx0, sy0, sx1, sy1, outline=C["accent"], width=2, tags="crop")
        for i in (1, 2):      # rule-of-thirds guides
            gx, gy = sx0 + (sx1 - sx0) * i / 3, sy0 + (sy1 - sy0) * i / 3
            c.create_line(gx, sy0, gx, sy1, fill="#bbbbbb", tags="crop")
            c.create_line(sx0, gy, sx1, gy, fill="#bbbbbb", tags="crop")
        mx, my = (sx0 + sx1) / 2, (sy0 + sy1) / 2
        for hx in (sx0, mx, sx1):          # grips: corners and sides
            for hy in (sy0, my, sy1):
                if not (hx == mx and hy == my):
                    c.create_rectangle(hx - 5, hy - 5, hx + 5, hy + 5,
                                       fill=C["accent"], outline=C["bg"], tags="crop")

    def _crop_zone(self, x, y):
        """What the pointer would grab: a corner, a side, the frame itself, or nothing."""
        sx0, sy0, sx1, sy1 = self._box_on_screen()
        nl, nr = abs(x - sx0) <= GRIP, abs(x - sx1) <= GRIP
        nt, nb = abs(y - sy0) <= GRIP, abs(y - sy1) <= GRIP
        if sx0 - GRIP <= x <= sx1 + GRIP and sy0 - GRIP <= y <= sy1 + GRIP:
            if nt and nl: return "tl"
            if nt and nr: return "tr"
            if nb and nl: return "bl"
            if nb and nr: return "br"
            if nl: return "l"
            if nr: return "r"
            if nt: return "t"
            if nb: return "b"
            if sx0 <= x <= sx1 and sy0 <= y <= sy1: return "move"
        return "new"

    _CURSORS = {"tl": "top_left_corner", "br": "bottom_right_corner", "tr": "top_right_corner",
                "bl": "bottom_left_corner", "l": "sb_h_double_arrow", "r": "sb_h_double_arrow",
                "t": "sb_v_double_arrow", "b": "sb_v_double_arrow", "move": "fleur", "new": "crosshair"}

    def _hover(self, e):
        if self._cropping and self.crop_box and self._view and not self._crop_mode:
            self.canvas.config(cursor=self._CURSORS[self._crop_zone(e.x, e.y)])

    def _press(self, e):
        if self._cropping and self.crop_box and self._view:
            self._crop_mode = self._crop_zone(e.x, e.y)
            self._crop_grab = self._photo_point((e.x, e.y))
            self._crop_start = list(self.crop_box)
            if self._crop_mode == "new":
                bw, bh = self.base.size
                self._crop_anchor = (min(max(self._crop_grab[0], 0), bw),
                                     min(max(self._crop_grab[1], 0), bh))
            elif len(self._crop_mode) == 2:      # a corner: redraw from the opposite corner
                x0, y0, x1, y1 = self.crop_box
                self._crop_anchor = (x1 if "l" in self._crop_mode else x0,
                                     y1 if "t" in self._crop_mode else y0)
        elif self.base:
            self._press_at = (e.x, e.y)       # a click zooms; a drag moves the view
            self._dragged = False
            self._pan_from = (e.x, e.y)

    def _drag(self, e):
        if self._cropping and self._crop_mode:
            bw, bh = self.base.size
            px, py = self._photo_point((e.x, e.y))
            px, py = min(max(px, 0), bw), min(max(py, 0), bh)
            small = 8.0
            x0, y0, x1, y1 = self._crop_start
            mode = self._crop_mode
            if mode == "move":
                dx = min(max(px - self._crop_grab[0], -x0), bw - x1)
                dy = min(max(py - self._crop_grab[1], -y0), bh - y1)
                self.crop_box = [x0 + dx, y0 + dy, x1 + dx, y1 + dy]
            elif mode == "l":
                self.crop_box = [min(px, x1 - small), y0, x1, y1]
            elif mode == "r":
                self.crop_box = [x0, y0, max(px, x0 + small), y1]
            elif mode == "t":
                self.crop_box = [x0, min(py, y1 - small), x1, y1]
            elif mode == "b":
                self.crop_box = [x0, y0, x1, max(py, y0 + small)]
            else:                                # a corner, or a brand-new frame
                ax, ay = self._crop_anchor
                self.crop_box = [min(ax, px), min(ay, py), max(ax, px), max(ay, py)]
            self._draw_crop_frame()
        elif self._pan_from:
            if not self._dragged:
                if abs(e.x - self._press_at[0]) + abs(e.y - self._press_at[1]) < 5:
                    return                    # still a click, not a drag
                self._dragged = True
                self.canvas.config(cursor="fleur")
            if self.zoom is None or not self.center:
                return
            dx, dy = e.x - self._pan_from[0], e.y - self._pan_from[1]
            self._pan_from = (e.x, e.y)
            self.center = (self.center[0] - dx / self.zoom, self.center[1] - dy / self.zoom)
            self._render()

    def _release(self, e):
        if self._pan_from:
            self._pan_from = None
            self.canvas.config(cursor="crosshair")
            if not self._dragged and not self._cropping:
                self._click_zoom(e)
            return
        if self._cropping and self._crop_mode:
            self._crop_mode = None
            x0, y0, x1, y1 = self.crop_box
            if x1 - x0 < 8 or y1 - y0 < 8:       # a tap, not a drag: keep the old frame
                self.crop_box = list(self._crop_start)
            self._draw_crop_frame()

    # ─── RESIZE ───────────────────────────────────────────────────────────────

    def resize_dialog(self):
        if not self.base:
            return
        w, h = self.base.size
        d = tk.Toplevel(self.root)
        d.title(self.t["resize_title"])
        d.configure(bg=C["bg"])
        d.geometry("300x190")
        d.resizable(False, False)

        for row, label in enumerate([self.t["width"], self.t["height"]]):
            tk.Label(d, text=label + ":", bg=C["bg"], fg=C["text"],
                     font=("Helvetica", 12)).grid(row=row, column=0, padx=20, pady=12, sticky=tk.W)
        w_v = tk.StringVar(value=str(w))
        h_v = tk.StringVar(value=str(h))
        w_e = tk.Entry(d, textvariable=w_v, width=8, bg=C["bg3"], fg=C["text"],
                       insertbackground=C["text"])
        h_e = tk.Entry(d, textvariable=h_v, width=8, bg=C["bg3"], fg=C["text"],
                       insertbackground=C["text"])
        w_e.grid(row=0, column=1, padx=10)
        h_e.grid(row=1, column=1, padx=10)

        # typing one side fills the other, so the photo keeps its shape
        def follow(source, target, ratio):
            try:
                target.set(str(max(1, int(round(int(source.get()) * ratio)))))
            except ValueError:
                pass
        w_e.bind("<KeyRelease>", lambda e: follow(w_v, h_v, h / float(w)))
        h_e.bind("<KeyRelease>", lambda e: follow(h_v, w_v, w / float(h)))

        def apply():
            try:
                nw, nh = int(w_v.get()), int(h_v.get())
                if nw < 1 or nh < 1 or nw > 30000 or nh > 30000:
                    raise ValueError(f"{nw} × {nh}")
                self._set_base(self.base.resize((nw, nh), Image.LANCZOS))
                d.destroy()
            except Exception as ex:
                messagebox.showerror(self.t["error"], str(ex))

        bf = tk.Frame(d, bg=C["bg"])
        bf.grid(row=2, column=0, columnspan=2, pady=14)
        FlatButton(bf, self.t["apply"], apply, C["accent"], fg=C["bg"],
                   font=("Helvetica", 11, "bold"), padx=14).pack(side=tk.LEFT, padx=6)
        FlatButton(bf, self.t["cancel"], d.destroy, C["bg3"], padx=14).pack(side=tk.LEFT, padx=6)


# ─── ENTRY ────────────────────────────────────────────────────────────────────

if __name__ == "__main__":
    root = tk.Tk()
    app = LocalShot(root)
    root.mainloop()
