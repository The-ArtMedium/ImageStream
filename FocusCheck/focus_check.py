#!/usr/bin/env python3
"""
FocusCheck — Culling & Sharpness Recovery Tool
Part of the ImageStream Local Suite — The Art Medium

Languages: English · Español · Français · Português · العربية · 中文 · हिन्दी
Arabic uses RTL layout automatically.

Features:
  • Laplacian variance scoring
  • Auto-calibrated thresholds per shoot
  • EXIF shutter speed — distinguishes motion blur from focus error
  • Thumbnail strip in the image list
  • Color-coded preview border — green / yellow / red at a glance
  • Mode overlay on canvas — ORIGINAL / PREVIEW / SPLIT / RECOVERED
  • Three-tier Laplacian-guided recovery (Gentle / Medium / Strong)
  • Split-screen before/after compare
  • Batch recovery — all fixable in one click
  • Delete individual or all rejected
  • Open Results Folder

Originals are never modified.
Supports JPG PNG TIFF BMP WebP + RAW (CR2 NEF ARW DNG RAF ORF RW2 CR3)
"""

import cv2
import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk, ImageFilter, ImageDraw
import threading
from fractions import Fraction

# ── RAW ──────────────────────────────────────────────────
try:
    import rawpy
    RAW_AVAILABLE = True
except ImportError:
    RAW_AVAILABLE = False

# ── EXIF ─────────────────────────────────────────────────
try:
    from PIL.ExifTags import TAGS
    EXIF_AVAILABLE = True
except ImportError:
    EXIF_AVAILABLE = False

# ── FORMATS ──────────────────────────────────────────────
STD_FMT = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp"}
RAW_FMT = {".cr2", ".nef", ".arw", ".dng", ".raf", ".orf", ".rw2", ".raw", ".cr3"}

def supported():
    return STD_FMT | RAW_FMT if RAW_AVAILABLE else STD_FMT

MOTION_SHUTTER = Fraction(1, 250)

# ── TRANSLATIONS ─────────────────────────────────────────
LANGUAGES = {
    "en": {
        "name": "English", "dir": "ltr",
        "open_folder":      "▶  OPEN FOLDER",
        "open_results":     "📁  OPEN RESULTS FOLDER",
        "sharp":            "SHARP",
        "fixable":          "FIXABLE",
        "rejected":         "REJECTED",
        "recovery":         "RECOVERY",
        "strength":         "STRENGTH",
        "preview":          "👁  PREVIEW",
        "split":            "⧉  SPLIT COMPARE",
        "apply":            "✓  APPLY → SHARP",
        "batch":            "⚡  BATCH ALL FIXABLE",
        "skip":             "→  SKIP",
        "delete_this":      "⬛  DELETE THIS",
        "delete_rejected":  "⬛  DELETE ALL REJECTED",
        "no_recovery":      "Sharp\nNo recovery needed.",
        "fixable_status":   "Fixable — adjust &\napply recovery.",
        "rejected_status":  "Rejected — try recovery\nbefore deleting.",
        "all_done":         "All fixable images\nprocessed ✓",
        "welcome":          "▶  OPEN FOLDER TO BEGIN\n\nFocusCheck will score every image,\ncalibrate thresholds to your shoot,\nand sort into sharp / fixable / rejected.",
        "scanning":         "Scoring images…",
        "sorting":          "Sorting…",
        "no_images":        "No supported images found.",
        "calibrated":       "Calibrated:  Sharp ≥ {}  Fixable ≥ {}",
        "need":             "Need {}",
        "deficit":          "Deficit  −{}",
        "threshold":        "Threshold: {}",
        "laplacian":        "Laplacian score",
        "passes":           "Passes: {}  ·  Kernel: {}px",
        "strategy_dir":     "Strategy: directional",
        "strategy_rad":     "Strategy: radial",
        "strength_auto":    "Strength auto-set from deficit",
        "motion_blur":      "  〜  MOTION BLUR  ",
        "focus_error":      "  ⊙  FOCUS ERROR  ",
        "blur_unknown":     "  BLUR UNKNOWN  ",
        "motion":           "MOTION",
        "focus":            "FOCUS",
        "no_exif":          "NO EXIF",
        "original":         " ORIGINAL ",
        "preview_mode":     " PREVIEW ",
        "split_mode":       " SPLIT ",
        "recovered_mode":   " RECOVERED ",
        "recovered_save":   "✓ Saved to sharp/  ·  Strength {}",
        "rec_saved":        "Recovered ✓\nSaved to sharp/",
        "batch_confirm":    "Apply recovery (strength {}) to {} fixable images?\n\nEach uses its own calibrated parameters. Saved to sharp/.",
        "batch_none":       "No unrecovered fixable images.",
        "batch_done":       "✓ Recovered {} images → sharp/",
        "batch_progress":   "Processing…",
        "delete_confirm":   "Delete:\n{}\n\nCannot be undone.",
        "delete_all_confirm": "Permanently delete {} rejected images?\n\nCannot be undone.",
        "delete_none":      "No rejected images left.",
        "deleted_msg":      "✓ Deleted {} rejected images.\nSpace freed.",
        "deleted_title":    "✓ Deleted {} rejected images.",
        "sharp_badge":      "  SHARP ✓  ",
        "pos":              "{} / {}",
        "split_label_orig": "ORIGINAL",
        "split_label_rec":  "RECOVERED",
        "raw_ok":           "● RAW",
        "raw_fail":         "○ RAW",
        "exif_ok":          "● EXIF",
        "exif_fail":        "○ EXIF",
        "language":         "Language",
        "open_begin":       "Open a folder\nto begin culling",
    },
    "es": {
        "name": "Español", "dir": "ltr",
        "open_folder":      "▶  ABRIR CARPETA",
        "open_results":     "📁  ABRIR RESULTADOS",
        "sharp":            "NITIDO",
        "fixable":          "RECUPERABLE",
        "rejected":         "RECHAZADO",
        "recovery":         "RECUPERACIÓN",
        "strength":         "INTENSIDAD",
        "preview":          "👁  VISTA PREVIA",
        "split":            "⧉  COMPARAR",
        "apply":            "✓  APLICAR → NÍTIDO",
        "batch":            "⚡  PROCESAR TODOS",
        "skip":             "→  OMITIR",
        "delete_this":      "⬛  ELIMINAR ESTE",
        "delete_rejected":  "⬛  ELIMINAR RECHAZADOS",
        "no_recovery":      "Nítido\nNo se necesita recuperación.",
        "fixable_status":   "Recuperable — ajusta\ny aplica la recuperación.",
        "rejected_status":  "Rechazado — prueba antes\nde eliminar.",
        "all_done":         "Todas las imágenes\nprocesadas ✓",
        "welcome":          "▶  ABRE UNA CARPETA PARA COMENZAR\n\nFocusCheck puntuará cada imagen,\ncalibrará los umbrales a tu sesión\ny ordenará en nítido / recuperable / rechazado.",
        "scanning":         "Puntuando imágenes…",
        "sorting":          "Ordenando…",
        "no_images":        "No se encontraron imágenes compatibles.",
        "calibrated":       "Calibrado:  Nítido ≥ {}  Recuperable ≥ {}",
        "need":             "Necesita {}",
        "deficit":          "Déficit  −{}",
        "threshold":        "Umbral: {}",
        "laplacian":        "Puntuación Laplaciana",
        "passes":           "Pasadas: {}  ·  Núcleo: {}px",
        "strategy_dir":     "Estrategia: direccional",
        "strategy_rad":     "Estrategia: radial",
        "strength_auto":    "Intensidad ajustada automáticamente",
        "motion_blur":      "  〜  MOVIMIENTO  ",
        "focus_error":      "  ⊙  ERROR DE ENFOQUE  ",
        "blur_unknown":     "  DESENFOQUE DESCONOCIDO  ",
        "motion":           "MOVIMIENTO",
        "focus":            "ENFOQUE",
        "no_exif":          "SIN EXIF",
        "original":         " ORIGINAL ",
        "preview_mode":     " VISTA PREVIA ",
        "split_mode":       " COMPARAR ",
        "recovered_mode":   " RECUPERADA ",
        "recovered_save":   "✓ Guardada en nítido/  ·  Intensidad {}",
        "rec_saved":        "Recuperada ✓\nGuardada en nítido/",
        "batch_confirm":    "¿Aplicar recuperación (intensidad {}) a {} imágenes recuperables?\n\nCada una usa sus propios parámetros. Guardadas en nítido/.",
        "batch_none":       "No hay imágenes recuperables pendientes.",
        "batch_done":       "✓ Recuperadas {} imágenes → nítido/",
        "batch_progress":   "Procesando…",
        "delete_confirm":   "Eliminar:\n{}\n\nNo se puede deshacer.",
        "delete_all_confirm": "¿Eliminar permanentemente {} imágenes rechazadas?\n\nNo se puede deshacer.",
        "delete_none":      "No quedan imágenes rechazadas.",
        "deleted_msg":      "✓ Eliminadas {} imágenes rechazadas.\nEspacio liberado.",
        "deleted_title":    "✓ Eliminadas {} imágenes rechazadas.",
        "sharp_badge":      "  NÍTIDO ✓  ",
        "pos":              "{} / {}",
        "split_label_orig": "ORIGINAL",
        "split_label_rec":  "RECUPERADA",
        "raw_ok":           "● RAW",
        "raw_fail":         "○ RAW",
        "exif_ok":          "● EXIF",
        "exif_fail":        "○ EXIF",
        "language":         "Idioma",
        "open_begin":       "Abre una carpeta\npara comenzar",
    },
    "fr": {
        "name": "Français", "dir": "ltr",
        "open_folder":      "▶  OUVRIR DOSSIER",
        "open_results":     "📁  OUVRIR RÉSULTATS",
        "sharp":            "NET",
        "fixable":          "RÉCUPÉRABLE",
        "rejected":         "REJETÉ",
        "recovery":         "RÉCUPÉRATION",
        "strength":         "INTENSITÉ",
        "preview":          "👁  APERÇU",
        "split":            "⧉  COMPARAISON",
        "apply":            "✓  APPLIQUER → NET",
        "batch":            "⚡  TRAITER TOUT",
        "skip":             "→  PASSER",
        "delete_this":      "⬛  SUPPRIMER CELUI-CI",
        "delete_rejected":  "⬛  SUPPRIMER LES REJETÉS",
        "no_recovery":      "Net\nAucune récupération nécessaire.",
        "fixable_status":   "Récupérable — ajustez\net appliquez la récupération.",
        "rejected_status":  "Rejeté — essayez la récupération\navant de supprimer.",
        "all_done":         "Toutes les images\ntraitées ✓",
        "welcome":          "▶  OUVREZ UN DOSSIER POUR COMMENCER\n\nFocusCheck notera chaque image,\ncalibrera les seuils pour votre session\net triera en net / récupérable / rejeté.",
        "scanning":         "Notation des images…",
        "sorting":          "Tri en cours…",
        "no_images":        "Aucune image compatible trouvée.",
        "calibrated":       "Calibré:  Net ≥ {}  Récupérable ≥ {}",
        "need":             "Besoin de {}",
        "deficit":          "Déficit  −{}",
        "threshold":        "Seuil: {}",
        "laplacian":        "Score Laplacien",
        "passes":           "Passes: {}  ·  Noyau: {}px",
        "strategy_dir":     "Stratégie: directionnelle",
        "strategy_rad":     "Stratégie: radiale",
        "strength_auto":    "Intensité auto-réglée depuis le déficit",
        "motion_blur":      "  〜  FLOU DE MOUVEMENT  ",
        "focus_error":      "  ⊙  ERREUR DE MISE AU POINT  ",
        "blur_unknown":     "  FLOU INCONNU  ",
        "motion":           "MOUVEMENT",
        "focus":            "MISE AU POINT",
        "no_exif":          "SANS EXIF",
        "original":         " ORIGINAL ",
        "preview_mode":     " APERÇU ",
        "split_mode":       " COMPARAISON ",
        "recovered_mode":   " RÉCUPÉRÉE ",
        "recovered_save":   "✓ Sauvegardée dans net/  ·  Intensité {}",
        "rec_saved":        "Récupérée ✓\nSauvegardée dans net/",
        "batch_confirm":    "Appliquer la récupération (intensité {}) à {} images récupérables?\n\nChacune utilise ses propres paramètres. Sauvegardées dans net/.",
        "batch_none":       "Aucune image récupérable en attente.",
        "batch_done":       "✓ Récupérées {} images → net/",
        "batch_progress":   "Traitement…",
        "delete_confirm":   "Supprimer:\n{}\n\nImpossible d'annuler.",
        "delete_all_confirm": "Supprimer définitivement {} images rejetées?\n\nImpossible d'annuler.",
        "delete_none":      "Aucune image rejetée restante.",
        "deleted_msg":      "✓ Supprimées {} images rejetées.\nEspace libéré.",
        "deleted_title":    "✓ Supprimées {} images rejetées.",
        "sharp_badge":      "  NET ✓  ",
        "pos":              "{} / {}",
        "split_label_orig": "ORIGINAL",
        "split_label_rec":  "RÉCUPÉRÉE",
        "raw_ok":           "● RAW",
        "raw_fail":         "○ RAW",
        "exif_ok":          "● EXIF",
        "exif_fail":        "○ EXIF",
        "language":         "Langue",
        "open_begin":       "Ouvrez un dossier\npour commencer",
    },
    "pt": {
        "name": "Português", "dir": "ltr",
        "open_folder":      "▶  ABRIR PASTA",
        "open_results":     "📁  ABRIR RESULTADOS",
        "sharp":            "NÍTIDO",
        "fixable":          "RECUPERÁVEL",
        "rejected":         "REJEITADO",
        "recovery":         "RECUPERAÇÃO",
        "strength":         "INTENSIDADE",
        "preview":          "👁  PRÉ-VISUALIZAR",
        "split":            "⧉  COMPARAR",
        "apply":            "✓  APLICAR → NÍTIDO",
        "batch":            "⚡  PROCESSAR TODOS",
        "skip":             "→  PULAR",
        "delete_this":      "⬛  EXCLUIR ESTE",
        "delete_rejected":  "⬛  EXCLUIR REJEITADOS",
        "no_recovery":      "Nítido\nSem necessidade de recuperação.",
        "fixable_status":   "Recuperável — ajuste\ne aplique a recuperação.",
        "rejected_status":  "Rejeitado — tente recuperar\nantes de excluir.",
        "all_done":         "Todas as imagens\nprocessadas ✓",
        "welcome":          "▶  ABRA UMA PASTA PARA COMEÇAR\n\nFocusCheck pontuará cada imagem,\ncalibrará os limiares para sua sessão\ne ordenará em nítido / recuperável / rejeitado.",
        "scanning":         "Pontuando imagens…",
        "sorting":          "Ordenando…",
        "no_images":        "Nenhuma imagem compatível encontrada.",
        "calibrated":       "Calibrado:  Nítido ≥ {}  Recuperável ≥ {}",
        "need":             "Precisa de {}",
        "deficit":          "Déficit  −{}",
        "threshold":        "Limiar: {}",
        "laplacian":        "Pontuação Laplaciana",
        "passes":           "Passes: {}  ·  Núcleo: {}px",
        "strategy_dir":     "Estratégia: direcional",
        "strategy_rad":     "Estratégia: radial",
        "strength_auto":    "Intensidade ajustada automaticamente",
        "motion_blur":      "  〜  MOVIMENTO  ",
        "focus_error":      "  ⊙  ERRO DE FOCO  ",
        "blur_unknown":     "  DESFOQUE DESCONHECIDO  ",
        "motion":           "MOVIMENTO",
        "focus":            "FOCO",
        "no_exif":          "SEM EXIF",
        "original":         " ORIGINAL ",
        "preview_mode":     " PRÉ-VISUALIZAÇÃO ",
        "split_mode":       " COMPARAÇÃO ",
        "recovered_mode":   " RECUPERADA ",
        "recovered_save":   "✓ Salva em nítido/  ·  Intensidade {}",
        "rec_saved":        "Recuperada ✓\nSalva em nítido/",
        "batch_confirm":    "Aplicar recuperação (intensidade {}) a {} imagens recuperáveis?\n\nCada uma usa seus próprios parâmetros. Salvas em nítido/.",
        "batch_none":       "Nenhuma imagem recuperável pendente.",
        "batch_done":       "✓ Recuperadas {} imagens → nítido/",
        "batch_progress":   "Processando…",
        "delete_confirm":   "Excluir:\n{}\n\nNão pode ser desfeito.",
        "delete_all_confirm": "Excluir permanentemente {} imagens rejeitadas?\n\nNão pode ser desfeito.",
        "delete_none":      "Nenhuma imagem rejeitada restante.",
        "deleted_msg":      "✓ Excluídas {} imagens rejeitadas.\nEspaço liberado.",
        "deleted_title":    "✓ Excluídas {} imagens rejeitadas.",
        "sharp_badge":      "  NÍTIDO ✓  ",
        "pos":              "{} / {}",
        "split_label_orig": "ORIGINAL",
        "split_label_rec":  "RECUPERADA",
        "raw_ok":           "● RAW",
        "raw_fail":         "○ RAW",
        "exif_ok":          "● EXIF",
        "exif_fail":        "○ EXIF",
        "language":         "Idioma",
        "open_begin":       "Abra uma pasta\npara começar",
    },
    "ar": {
        "name": "العربية", "dir": "rtl",
        "open_folder":      "افتح مجلداً  ▶",
        "open_results":     "📁  فتح مجلد النتائج",
        "sharp":            "حاد",
        "fixable":          "قابل للإصلاح",
        "rejected":         "مرفوض",
        "recovery":         "الاسترداد",
        "strength":         "الشدة",
        "preview":          "👁  معاينة",
        "split":            "⧉  مقارنة مقسومة",
        "apply":            "✓  تطبيق ← حاد",
        "batch":            "⚡  معالجة الكل",
        "skip":             "→  تخطي",
        "delete_this":      "⬛  حذف هذه",
        "delete_rejected":  "⬛  حذف كل المرفوضة",
        "no_recovery":      "حادة\nلا حاجة للاسترداد.",
        "fixable_status":   "قابلة للإصلاح — اضبط\nوطبّق الاسترداد.",
        "rejected_status":  "مرفوضة — جرّب الاسترداد\nقبل الحذف.",
        "all_done":         "تمت معالجة جميع الصور ✓",
        "welcome":          "▶  افتح مجلداً للبدء\n\nسيقيّم FocusCheck كل صورة،\nويعيّر العتبات لجلستك،\nويرتبها في حاد / قابل للإصلاح / مرفوض.",
        "scanning":         "تقييم الصور…",
        "sorting":          "فرز…",
        "no_images":        "لم يتم العثور على صور مدعومة.",
        "calibrated":       "معاير:  حاد ≥ {}  قابل للإصلاح ≥ {}",
        "need":             "يحتاج {}",
        "deficit":          "عجز  −{}",
        "threshold":        "العتبة: {}",
        "laplacian":        "درجة لابلاسيان",
        "passes":           "تمريرات: {}  ·  نواة: {}px",
        "strategy_dir":     "الاستراتيجية: اتجاهية",
        "strategy_rad":     "الاستراتيجية: شعاعية",
        "strength_auto":    "الشدة مضبوطة تلقائياً من العجز",
        "motion_blur":      "  〜  ضبابية الحركة  ",
        "focus_error":      "  ⊙  خطأ في التركيز  ",
        "blur_unknown":     "  ضبابية مجهولة  ",
        "motion":           "حركة",
        "focus":            "تركيز",
        "no_exif":          "بدون EXIF",
        "original":         " الأصلية ",
        "preview_mode":     " معاينة ",
        "split_mode":       " مقارنة ",
        "recovered_mode":   " مستردة ",
        "recovered_save":   "✓ محفوظة في حاد/  ·  الشدة {}",
        "rec_saved":        "مستردة ✓\nمحفوظة في حاد/",
        "batch_confirm":    "تطبيق الاسترداد (شدة {}) على {} صورة قابلة للإصلاح؟\n\nكل صورة تستخدم معاملاتها الخاصة. محفوظة في حاد/.",
        "batch_none":       "لا توجد صور قابلة للإصلاح معلقة.",
        "batch_done":       "✓ تم استرداد {} صورة → حاد/",
        "batch_progress":   "جارٍ المعالجة…",
        "delete_confirm":   "حذف:\n{}\n\nلا يمكن التراجع.",
        "delete_all_confirm": "حذف {} صورة مرفوضة نهائياً؟\n\nلا يمكن التراجع.",
        "delete_none":      "لا توجد صور مرفوضة متبقية.",
        "deleted_msg":      "✓ تم حذف {} صورة مرفوضة.\nتم تحرير المساحة.",
        "deleted_title":    "✓ تم حذف {} صورة مرفوضة.",
        "sharp_badge":      "  حاد ✓  ",
        "pos":              "{} / {}",
        "split_label_orig": "الأصلية",
        "split_label_rec":  "المستردة",
        "raw_ok":           "● RAW",
        "raw_fail":         "○ RAW",
        "exif_ok":          "● EXIF",
        "exif_fail":        "○ EXIF",
        "language":         "اللغة",
        "open_begin":       "افتح مجلداً\nللبدء",
    },
    "zh": {
        "name": "中文", "dir": "ltr",
        "open_folder":      "▶  打开文件夹",
        "open_results":     "📁  打开结果文件夹",
        "sharp":            "清晰",
        "fixable":          "可修复",
        "rejected":         "已拒绝",
        "recovery":         "修复",
        "strength":         "强度",
        "preview":          "👁  预览",
        "split":            "⧉  对比",
        "apply":            "✓  应用 → 清晰",
        "batch":            "⚡  批量处理",
        "skip":             "→  跳过",
        "delete_this":      "⬛  删除此图",
        "delete_rejected":  "⬛  删除所有拒绝",
        "no_recovery":      "清晰\n无需修复。",
        "fixable_status":   "可修复 — 调整强度\n并应用修复。",
        "rejected_status":  "已拒绝 — 删除前\n请尝试修复。",
        "all_done":         "所有可修复图像\n已处理完成 ✓",
        "welcome":          "▶  打开文件夹开始\n\nFocusCheck 将评分每张图像，\n根据您的拍摄校准阈值，\n并分类为清晰 / 可修复 / 已拒绝。",
        "scanning":         "正在评分图像…",
        "sorting":          "正在排序…",
        "no_images":        "未找到支持的图像。",
        "calibrated":       "已校准:  清晰 ≥ {}  可修复 ≥ {}",
        "need":             "需要 {}",
        "deficit":          "差距  −{}",
        "threshold":        "阈值: {}",
        "laplacian":        "拉普拉斯分数",
        "passes":           "通道: {}  ·  核: {}px",
        "strategy_dir":     "策略: 定向锐化",
        "strategy_rad":     "策略: 径向锐化",
        "strength_auto":    "强度根据差距自动设置",
        "motion_blur":      "  〜  运动模糊  ",
        "focus_error":      "  ⊙  对焦错误  ",
        "blur_unknown":     "  模糊未知  ",
        "motion":           "运动",
        "focus":            "对焦",
        "no_exif":          "无EXIF",
        "original":         " 原始 ",
        "preview_mode":     " 预览 ",
        "split_mode":       " 对比 ",
        "recovered_mode":   " 已修复 ",
        "recovered_save":   "✓ 已保存到清晰/  ·  强度 {}",
        "rec_saved":        "已修复 ✓\n已保存到清晰/",
        "batch_confirm":    "对 {} 张可修复图像应用修复（强度 {}）？\n\n每张使用自己的校准参数。保存到清晰/。",
        "batch_none":       "没有待处理的可修复图像。",
        "batch_done":       "✓ 已修复 {} 张图像 → 清晰/",
        "batch_progress":   "处理中…",
        "delete_confirm":   "删除:\n{}\n\n无法撤销。",
        "delete_all_confirm": "永久删除 {} 张已拒绝图像？\n\n无法撤销。",
        "delete_none":      "没有剩余的已拒绝图像。",
        "deleted_msg":      "✓ 已删除 {} 张已拒绝图像。\n空间已释放。",
        "deleted_title":    "✓ 已删除 {} 张已拒绝图像。",
        "sharp_badge":      "  清晰 ✓  ",
        "pos":              "{} / {}",
        "split_label_orig": "原始",
        "split_label_rec":  "已修复",
        "raw_ok":           "● RAW",
        "raw_fail":         "○ RAW",
        "exif_ok":          "● EXIF",
        "exif_fail":        "○ EXIF",
        "language":         "语言",
        "open_begin":       "打开文件夹\n开始处理",
    },
    "hi": {
        "name": "हिन्दी", "dir": "ltr",
        "open_folder":      "▶  फ़ोल्डर खोलें",
        "open_results":     "📁  परिणाम फ़ोल्डर खोलें",
        "sharp":            "तीक्ष्ण",
        "fixable":          "ठीक करने योग्य",
        "rejected":         "अस्वीकृत",
        "recovery":         "पुनर्प्राप्ति",
        "strength":         "तीव्रता",
        "preview":          "👁  पूर्वावलोकन",
        "split":            "⧉  विभाजित तुलना",
        "apply":            "✓  लागू करें → तीक्ष्ण",
        "batch":            "⚡  सभी ठीक करें",
        "skip":             "→  छोड़ें",
        "delete_this":      "⬛  इसे हटाएं",
        "delete_rejected":  "⬛  सभी अस्वीकृत हटाएं",
        "no_recovery":      "तीक्ष्ण\nपुनर्प्राप्ति की आवश्यकता नहीं।",
        "fixable_status":   "ठीक करने योग्य — तीव्रता\nसमायोजित करें और लागू करें।",
        "rejected_status":  "अस्वीकृत — हटाने से पहले\nपुनर्प्राप्ति आज़माएं।",
        "all_done":         "सभी छवियां\nप्रसंस्कृत ✓",
        "welcome":          "▶  शुरू करने के लिए फ़ोल्डर खोलें\n\nFocusCheck हर छवि को स्कोर करेगा,\nआपकी शूट के अनुसार थ्रेशोल्ड कैलिब्रेट करेगा,\nऔर तीक्ष्ण / ठीक करने योग्य / अस्वीकृत में सॉर्ट करेगा।",
        "scanning":         "छवियां स्कोर हो रही हैं…",
        "sorting":          "सॉर्ट हो रहा है…",
        "no_images":        "कोई समर्थित छवि नहीं मिली।",
        "calibrated":       "कैलिब्रेटेड:  तीक्ष्ण ≥ {}  ठीक योग्य ≥ {}",
        "need":             "आवश्यक {}",
        "deficit":          "कमी  −{}",
        "threshold":        "थ्रेशोल्ड: {}",
        "laplacian":        "लाप्लेशियन स्कोर",
        "passes":           "पास: {}  ·  कर्नेल: {}px",
        "strategy_dir":     "रणनीति: दिशात्मक",
        "strategy_rad":     "रणनीति: रेडियल",
        "strength_auto":    "तीव्रता कमी से स्वतः सेट",
        "motion_blur":      "  〜  गति धुंधलापन  ",
        "focus_error":      "  ⊙  फ़ोकस त्रुटि  ",
        "blur_unknown":     "  धुंधलापन अज्ञात  ",
        "motion":           "गति",
        "focus":            "फ़ोकस",
        "no_exif":          "EXIF नहीं",
        "original":         " मूल ",
        "preview_mode":     " पूर्वावलोकन ",
        "split_mode":       " विभाजित ",
        "recovered_mode":   " पुनर्प्राप्त ",
        "recovered_save":   "✓ तीक्ष्ण/ में सहेजा  ·  तीव्रता {}",
        "rec_saved":        "पुनर्प्राप्त ✓\nतीक्ष्ण/ में सहेजा",
        "batch_confirm":    "{} ठीक करने योग्य छवियों पर पुनर्प्राप्ति (तीव्रता {}) लागू करें?\n\nप्रत्येक अपने कैलिब्रेटेड पैरामीटर उपयोग करती है। तीक्ष्ण/ में सहेजा।",
        "batch_none":       "कोई लंबित ठीक करने योग्य छवि नहीं।",
        "batch_done":       "✓ {} छवियां पुनर्प्राप्त → तीक्ष्ण/",
        "batch_progress":   "प्रसंस्करण…",
        "delete_confirm":   "हटाएं:\n{}\n\nपूर्ववत नहीं किया जा सकता।",
        "delete_all_confirm": "{} अस्वीकृत छवियां स्थायी रूप से हटाएं?\n\nपूर्ववत नहीं किया जा सकता।",
        "delete_none":      "कोई अस्वीकृत छवि शेष नहीं।",
        "deleted_msg":      "✓ {} अस्वीकृत छवियां हटाई गईं।\nस्थान मुक्त हुआ।",
        "deleted_title":    "✓ {} अस्वीकृत छवियां हटाई गईं।",
        "sharp_badge":      "  तीक्ष्ण ✓  ",
        "pos":              "{} / {}",
        "split_label_orig": "मूल",
        "split_label_rec":  "पुनर्प्राप्त",
        "raw_ok":           "● RAW",
        "raw_fail":         "○ RAW",
        "exif_ok":          "● EXIF",
        "exif_fail":        "○ EXIF",
        "language":         "भाषा",
        "open_begin":       "फ़ोल्डर खोलें\nशुरू करने के लिए",
    },
}

LANG_ORDER = ["en", "es", "fr", "pt", "ar", "zh", "hi"]

# ── PALETTE ──────────────────────────────────────────────
BG      = "#0a0a0a"
BG2     = "#111111"
BG3     = "#1a1a1a"
BG4     = "#222222"
BG5     = "#2a2a2a"
ACCENT  = "#f5a623"
ACCENT2 = "#e8941a"
GREEN   = "#4ade80"
GREEN2  = "#166534"
YELLOW  = "#fbbf24"
YELLOW2 = "#78350f"
RED     = "#f87171"
RED2    = "#7f1d1d"
BLUE    = "#60a5fa"
PURPLE  = "#c084fc"
TEXT    = "#f5f5f5"
TEXT2   = "#888888"
TEXT3   = "#444444"

CAT_COLOR  = {"sharp": GREEN,  "fixable": YELLOW,  "rejected": RED}
CAT_COLOR2 = {"sharp": GREEN2, "fixable": YELLOW2, "rejected": RED2}

THUMB_W = 56
THUMB_H = 42

# ── IMAGE IO ─────────────────────────────────────────────
def open_pil(path):
    if Path(path).suffix.lower() in RAW_FMT and RAW_AVAILABLE:
        with rawpy.imread(str(path)) as r:
            rgb = r.postprocess(use_camera_wb=True, half_size=True,
                                no_auto_bright=False, output_bps=8)
        return Image.fromarray(rgb)
    return Image.open(str(path)).convert("RGB")

def open_cv2(path):
    if Path(path).suffix.lower() in RAW_FMT and RAW_AVAILABLE:
        with rawpy.imread(str(path)) as r:
            rgb = r.postprocess(use_camera_wb=True, half_size=True,
                                no_auto_bright=False, output_bps=8)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return cv2.imread(str(path))

def make_thumb(pil_img):
    t = pil_img.copy()
    t.thumbnail((THUMB_W, THUMB_H), Image.LANCZOS)
    canvas = Image.new("RGB", (THUMB_W, THUMB_H), (18, 18, 18))
    x = (THUMB_W - t.width)  // 2
    y = (THUMB_H - t.height) // 2
    canvas.paste(t, (x, y))
    return canvas

# ── EXIF ─────────────────────────────────────────────────
def get_shutter(path):
    try:
        img  = Image.open(str(path))
        exif = img._getexif()
        if not exif: return None
        for tag_id, val in exif.items():
            if TAGS.get(tag_id) == "ExposureTime":
                if isinstance(val, tuple): return Fraction(val[0], val[1])
                return Fraction(val).limit_denominator(100000)
    except Exception:
        pass
    return None

def blur_type(shutter):
    if shutter is None:            return "unknown"
    if shutter <= MOTION_SHUTTER:  return "motion"
    return "focus"

def shutter_str(shutter):
    if shutter is None: return "—"
    if shutter >= 1:    return f"{float(shutter):.1f}s"
    return f"1/{int(round(1/shutter))}s"

# ── SCORING ──────────────────────────────────────────────
def score_image(path):
    try:
        img = open_cv2(path)
        if img is None: return 0.0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())
    except Exception:
        return 0.0

# ── AUTO-THRESHOLD ────────────────────────────────────────
def calibrate(scores):
    if not scores: return 150, 50
    s = sorted(scores)
    n = len(s)
    return max(s[int(n * 0.60)], 80), max(s[int(n * 0.30)], 20)

def make_cat_fn(sharp_t, fix_t):
    def cat(score):
        if score >= sharp_t: return "sharp"
        if score >= fix_t:   return "fixable"
        return "rejected"
    return cat

# ── RECOVERY ─────────────────────────────────────────────
def recovery_params(score, sharp_t, blur):
    deficit = sharp_t - score
    if blur == "motion":
        if deficit <= sharp_t * 0.3:
            return dict(radius=1, percent=110, threshold=4, edge=True,  passes=1, label_key="gentle_motion")
        elif deficit <= sharp_t * 0.7:
            return dict(radius=2, percent=145, threshold=2, edge=True,  passes=1, label_key="medium_motion")
        else:
            return dict(radius=2, percent=175, threshold=1, edge=True,  passes=2, label_key="strong_motion")
    else:
        if deficit <= sharp_t * 0.3:
            return dict(radius=1, percent=130, threshold=3, edge=False, passes=1, label_key="gentle_focus")
        elif deficit <= sharp_t * 0.7:
            return dict(radius=2, percent=170, threshold=2, edge=True,  passes=1, label_key="medium_focus")
        else:
            return dict(radius=2, percent=220, threshold=1, edge=True,  passes=2, label_key="strong_focus")

# Recovery label map per language
REC_LABELS = {
    "gentle_motion": {"en":"Motion · Gentle","es":"Movimiento · Suave","fr":"Mouvement · Doux",
                      "pt":"Movimento · Suave","ar":"حركة · خفيف","zh":"运动 · 轻柔","hi":"गति · हल्का"},
    "medium_motion": {"en":"Motion · Medium","es":"Movimiento · Medio","fr":"Mouvement · Moyen",
                      "pt":"Movimento · Médio","ar":"حركة · متوسط","zh":"运动 · 中等","hi":"गति · मध्यम"},
    "strong_motion": {"en":"Motion · Strong","es":"Movimiento · Fuerte","fr":"Mouvement · Fort",
                      "pt":"Movimento · Forte","ar":"حركة · قوي","zh":"运动 · 强力","hi":"गति · तीव्र"},
    "gentle_focus":  {"en":"Focus · Gentle","es":"Enfoque · Suave","fr":"Mise au point · Douce",
                      "pt":"Foco · Suave","ar":"تركيز · خفيف","zh":"对焦 · 轻柔","hi":"फ़ोकस · हल्का"},
    "medium_focus":  {"en":"Focus · Medium","es":"Enfoque · Medio","fr":"Mise au point · Moyenne",
                      "pt":"Foco · Médio","ar":"تركيز · متوسط","zh":"对焦 · 中等","hi":"फ़ोकस · मध्यम"},
    "strong_focus":  {"en":"Focus · Strong","es":"Enfoque · Fuerte","fr":"Mise au point · Forte",
                      "pt":"Foco · Forte","ar":"تركيز · قوي","zh":"对焦 · 强力","hi":"फ़ोकस · तीव्र"},
}

def apply_recovery(pil_img, params, strength):
    img     = pil_img.copy()
    percent = max(100, min(int(params["percent"] * strength), 500))
    for _ in range(params["passes"]):
        img = img.filter(ImageFilter.UnsharpMask(
            radius=params["radius"], percent=percent,
            threshold=params["threshold"]))
    if params["edge"] and strength > 0.3:
        img = img.filter(ImageFilter.EDGE_ENHANCE)
    return img

# ── SPLIT COMPARE ────────────────────────────────────────
def make_split(orig, rec, lbl_orig="ORIGINAL", lbl_rec="RECOVERED"):
    w, h    = orig.size
    rec_rs  = rec.resize((w, h), Image.LANCZOS)
    split_x = w // 2
    canvas  = Image.new("RGB", (w, h))
    canvas.paste(orig.crop((0, 0, split_x, h)), (0, 0))
    canvas.paste(rec_rs.crop((split_x, 0, w, h)), (split_x, 0))
    draw = ImageDraw.Draw(canvas)
    draw.line([(split_x, 0), (split_x, h)], fill=(255, 255, 255), width=2)
    draw.rectangle([(8, 8), (8 + len(lbl_orig)*7 + 8, 26)], fill=(0, 0, 0))
    draw.rectangle([(split_x+8, 8), (split_x+8+len(lbl_rec)*7+8, 26)], fill=(0, 0, 0))
    draw.text((12, 10), lbl_orig, fill=(180, 180, 180))
    draw.text((split_x+12, 10), lbl_rec, fill=(180, 180, 180))
    return canvas

# ── OUTPUT FOLDERS ───────────────────────────────────────
def make_output_dirs(folder):
    base = Path(folder) / "FocusCheck_Results"
    dirs = {k: base / k for k in ("sharp", "fixable", "rejected")}
    for d in dirs.values():
        d.mkdir(parents=True, exist_ok=True)
    return dirs

def copy_sorted(src, dest_dir):
    dest = dest_dir / Path(src).name
    shutil.copy2(str(src), str(dest))
    return dest

# ── APP ───────────────────────────────────────────────────
class App:
    def __init__(self, root):
        self.root       = root
        self.images     = []
        self.cur        = None
        self.dirs       = {}
        self.src_folder = None
        self.pil_cache  = None
        self.rec_cache  = None
        self.sharp_t    = 150
        self.fix_t      = 50
        self.in_split   = False
        self.strength   = tk.DoubleVar(value=1.0)
        self._thumbs    = {}

        # Language
        self.lang_code  = "en"
        self.T          = LANGUAGES["en"]

        self.root.title("FocusCheck — ImageStream Local Suite")
        self.root.configure(bg=BG)
        self.root.geometry("1380x820")
        self.root.minsize(1100, 680)

        self._build()

        if not RAW_AVAILABLE:
            self.root.after(500, lambda: messagebox.showwarning(
                "RAW",
                "rawpy not found — RAW files will be skipped.\n\npip install rawpy"))

    # ── TRANSLATION HELPER ───────────────────────────────
    def t(self, key, *args):
        val = self.T.get(key, LANGUAGES["en"].get(key, key))
        if args:
            return val.format(*args)
        return val

    def set_language(self, code):
        if code not in LANGUAGES: return
        self.lang_code = code
        self.T = LANGUAGES[code]
        self._apply_translations()

    def _apply_translations(self):
        """Update every translatable widget in the UI."""
        T = self.T
        is_rtl = T["dir"] == "rtl"

        # Topbar
        self.btn_open.configure(text=T["open_folder"])
        self.raw_badge.configure(
            text=T["raw_ok"] if RAW_AVAILABLE else T["raw_fail"])
        self.exif_badge_top.configure(
            text=T["exif_ok"] if EXIF_AVAILABLE else T["exif_fail"])

        # Left panel
        self.btn_results.configure(text=T["open_results"])

        # Nav bar
        self.btn_del_all.configure(text=T["delete_rejected"])
        self.btn_del_one.configure(text=T["delete_this"])

        # Recovery panel
        self.rec_hdr.configure(text=T["recovery"])
        self.strength_hdr_lbl.configure(text=T["strength"])
        self.btn_preview.configure(text=T["preview"])
        self.btn_split.configure(text=T["split"])
        self.btn_apply.configure(text=T["apply"])
        self.btn_batch.configure(text=T["batch"])
        self.btn_skip.configure(text=T["skip"])

        # Redraw dynamic content
        self._redraw_list()
        if self.cur is not None:
            self._update_rec(self.images[self.cur])
        else:
            self._draw_welcome()
            self.rec_status.configure(text=T["open_begin"], fg=TEXT3)

    # ═══════════════════════════════════════════════════
    # BUILD
    # ═══════════════════════════════════════════════════
    def _build(self):
        self._topbar()
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)
        self._panel_left(body)
        self._panel_center(body)
        self._panel_right(body)

    def _topbar(self):
        bar = tk.Frame(self.root, bg=BG2, height=58)
        bar.pack(fill="x")
        bar.pack_propagate(False)

        # Wordmark
        wm = tk.Frame(bar, bg=BG2)
        wm.pack(side="left", padx=24)
        tk.Label(wm, text="FOCUS", font=("Courier",16,"bold"), bg=BG2, fg=TEXT).pack(side="left")
        tk.Label(wm, text="CHECK", font=("Courier",16,"bold"), bg=BG2, fg=ACCENT).pack(side="left")
        tk.Label(wm, text=" / Culling & Recovery",
                 font=("Courier",10), bg=BG2, fg=TEXT3).pack(side="left", padx=(6,0))

        right = tk.Frame(bar, bg=BG2)
        right.pack(side="right", padx=20)

        # Language selector
        self.lang_var = tk.StringVar(value="en")
        lang_names    = [LANGUAGES[c]["name"] for c in LANG_ORDER]
        lang_menu     = tk.OptionMenu(right, self.lang_var, *LANG_ORDER,
                                      command=self.set_language)
        lang_menu.configure(font=("Courier",9), bg=BG3, fg=TEXT2,
                            relief="flat", highlightthickness=0,
                            activebackground=BG4, activeforeground=TEXT,
                            indicatoron=True)
        lang_menu["menu"].configure(font=("Courier",9), bg=BG3, fg=TEXT2,
                                    activebackground=BG4, activeforeground=TEXT)
        # Rename menu options to native names
        for i, code in enumerate(LANG_ORDER):
            lang_menu["menu"].entryconfig(i, label=LANGUAGES[code]["name"])
        lang_menu.pack(side="left", padx=(0, 10))

        tk.Frame(right, bg=BG4, width=1, height=24).pack(side="left", padx=8)

        self.raw_badge = tk.Label(right,
            text="● RAW" if RAW_AVAILABLE else "○ RAW",
            font=("Courier",9,"bold"), bg=BG3,
            fg=GREEN if RAW_AVAILABLE else TEXT3,
            padx=8, pady=4)
        self.raw_badge.pack(side="left", padx=4)

        self.exif_badge_top = tk.Label(right,
            text="● EXIF" if EXIF_AVAILABLE else "○ EXIF",
            font=("Courier",9,"bold"), bg=BG3,
            fg=GREEN if EXIF_AVAILABLE else TEXT3,
            padx=8, pady=4)
        self.exif_badge_top.pack(side="left", padx=4)

        tk.Frame(right, bg=BG4, width=1, height=24).pack(side="left", padx=8)

        self.btn_open = tk.Button(right,
            text=self.t("open_folder"),
            font=("Courier",10,"bold"),
            bg=ACCENT, fg=BG, relief="flat",
            padx=18, pady=8, cursor="hand2",
            activebackground=ACCENT2, activeforeground=BG,
            command=self.open_folder)
        self.btn_open.pack(side="left")

    def _panel_left(self, body):
        left = tk.Frame(body, bg=BG2, width=300)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        self.stats_frame = tk.Frame(left, bg=BG2)
        self.stats_frame.pack(fill="x", padx=12, pady=(14,0))
        self._draw_stats()

        self.cal_label = tk.Label(left, text="",
            font=("Courier",8), bg=BG2, fg=TEXT3, justify="left")
        self.cal_label.pack(fill="x", padx=14, pady=(6,0))

        self.btn_results = tk.Button(left,
            text=self.t("open_results"),
            font=("Courier",9,"bold"),
            bg=BG3, fg=TEXT2, relief="flat",
            pady=7, cursor="hand2", state="disabled",
            activebackground=BG4, activeforeground=TEXT,
            command=self.open_results)
        self.btn_results.pack(fill="x", padx=12, pady=(10,6))

        tk.Frame(left, bg=BG4, height=1).pack(fill="x")

        lc = tk.Frame(left, bg=BG2)
        lc.pack(fill="both", expand=True)
        cv = tk.Canvas(lc, bg=BG2, highlightthickness=0)
        sb = tk.Scrollbar(lc, orient="vertical", command=cv.yview,
                          bg=BG3, troughcolor=BG2)
        self.listbox = tk.Frame(cv, bg=BG2)
        self.listbox.bind("<Configure>",
            lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0), window=self.listbox, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")
        cv.bind("<MouseWheel>",
            lambda e: cv.yview_scroll(-1*(e.delta//120), "units"))

    def _panel_center(self, body):
        self.center = tk.Frame(body, bg=BG)
        self.center.pack(side="left", fill="both", expand=True)

        self.preview_border = tk.Frame(self.center, bg=BG3, padx=3, pady=3)
        self.preview_border.pack(fill="both", expand=True, padx=14, pady=14)

        self.pf = tk.Frame(self.preview_border, bg=BG)
        self.pf.pack(fill="both", expand=True)

        self.pl = tk.Label(self.pf, bg=BG, text="",
            font=("Courier",11), fg=TEXT3, justify="center")
        self.pl.pack(expand=True)
        self._draw_welcome()

        self.mode_overlay = tk.Label(self.pf, text="",
            font=("Courier",9,"bold"), bg=BG3, fg=TEXT2, padx=10, pady=4)
        self.mode_overlay.place(relx=1.0, rely=0.0, anchor="ne", x=-8, y=8)

        info = tk.Frame(self.center, bg=BG2, height=48)
        info.pack(fill="x")
        info.pack_propagate(False)

        self.cat_indicator = tk.Frame(info, width=4, bg=BG3)
        self.cat_indicator.pack(side="left", fill="y")

        self.iname = tk.Label(info, text="",
            font=("Courier",10,"bold"), bg=BG2, fg=TEXT)
        self.iname.pack(side="left", padx=(12,6), pady=12)

        self.iscore = tk.Label(info, text="",
            font=("Courier",9), bg=BG2, fg=TEXT2)
        self.iscore.pack(side="left", pady=12)

        self.exif_badge = tk.Label(info, text="",
            font=("Courier",9,"bold"), bg=BG3, fg=TEXT2, padx=10, pady=4)
        self.exif_badge.pack(side="right", padx=12, pady=10)

        self.cat_badge = tk.Label(info, text="",
            font=("Courier",9,"bold"), padx=12, pady=4)
        self.cat_badge.pack(side="right", padx=(0,6), pady=10)

        nav = tk.Frame(self.center, bg=BG3, height=56)
        nav.pack(fill="x")
        nav.pack_propagate(False)

        tk.Button(nav, text="◀", font=("Courier",12,"bold"),
                  bg=BG3, fg=TEXT2, relief="flat", padx=18, pady=10,
                  cursor="hand2", activebackground=BG4,
                  command=self.prev).pack(side="left", padx=(12,2), pady=8)
        tk.Button(nav, text="▶", font=("Courier",12,"bold"),
                  bg=BG3, fg=TEXT2, relief="flat", padx=18, pady=10,
                  cursor="hand2", activebackground=BG4,
                  command=self.next).pack(side="left", padx=(2,12), pady=8)

        self.pos_label = tk.Label(nav, text="",
            font=("Courier",9), bg=BG3, fg=TEXT3)
        self.pos_label.pack(side="left", padx=8)

        self.btn_del_all = tk.Button(nav,
            text=self.t("delete_rejected"),
            font=("Courier",9,"bold"),
            bg=RED2, fg=RED, relief="flat",
            padx=14, pady=10, cursor="hand2", state="disabled",
            activebackground="#5c1a1a", activeforeground=RED,
            command=self.delete_all_rejected)
        self.btn_del_all.pack(side="right", padx=(4,12), pady=8)

        self.btn_del_one = tk.Button(nav,
            text=self.t("delete_this"),
            font=("Courier",9,"bold"),
            bg=RED2, fg=RED, relief="flat",
            padx=14, pady=10, cursor="hand2", state="disabled",
            activebackground="#5c1a1a", activeforeground=RED,
            command=self.delete_one)
        self.btn_del_one.pack(side="right", padx=4, pady=8)

        self.pbar_bg = tk.Frame(self.center, bg=BG3, height=3)
        self.pbar_bg.pack(fill="x")
        self.pbar = tk.Frame(self.pbar_bg, bg=ACCENT, height=3, width=0)
        self.pbar.pack(side="left")

    def _panel_right(self, body):
        r = tk.Frame(body, bg=BG2, width=250)
        r.pack(side="right", fill="y")
        r.pack_propagate(False)

        hdr = tk.Frame(r, bg=BG2)
        hdr.pack(fill="x", padx=16, pady=(16,0))
        self.rec_hdr = tk.Label(hdr, text=self.t("recovery"),
            font=("Courier",10,"bold"), bg=BG2, fg=ACCENT)
        self.rec_hdr.pack(side="left")
        tk.Frame(r, bg=BG4, height=1).pack(fill="x", pady=(12,0))

        self.rec_status = tk.Label(r,
            text=self.t("open_begin"),
            font=("Courier",10), bg=BG2, fg=TEXT3,
            justify="center", pady=18)
        self.rec_status.pack(fill="x", padx=16)

        self.blur_badge = tk.Label(r, text="",
            font=("Courier",9,"bold"), bg=BG3, fg=TEXT2, pady=5)
        self.blur_badge.pack(fill="x", padx=16, pady=(0,4))

        score_frame = tk.Frame(r, bg=BG2)
        score_frame.pack(fill="x", padx=16, pady=(0,4))
        self.rec_score_big = tk.Label(score_frame, text="",
            font=("Courier",32,"bold"), bg=BG2, fg=TEXT3)
        self.rec_score_big.pack(side="left")
        score_sub = tk.Frame(score_frame, bg=BG2)
        score_sub.pack(side="left", padx=(8,0), pady=(8,0))
        self.rec_score_sub = tk.Label(score_sub, text="",
            font=("Courier",8), bg=BG2, fg=TEXT3, justify="left")
        self.rec_score_sub.pack(anchor="w")
        self.rec_deficit = tk.Label(score_sub, text="",
            font=("Courier",8), bg=BG2, fg=TEXT3, justify="left")
        self.rec_deficit.pack(anchor="w")

        tk.Frame(r, bg=BG4, height=1).pack(fill="x", pady=10)

        self.rec_label = tk.Label(r, text="",
            font=("Courier",9,"bold"), bg=BG2, fg=BLUE)
        self.rec_label.pack(padx=16, anchor="w")

        strength_hdr = tk.Frame(r, bg=BG2)
        strength_hdr.pack(fill="x", padx=16, pady=(12,2))
        self.strength_hdr_lbl = tk.Label(strength_hdr,
            text=self.t("strength"),
            font=("Courier",8,"bold"), bg=BG2, fg=TEXT3)
        self.strength_hdr_lbl.pack(side="left")
        self.sval = tk.Label(strength_hdr, text="1.0",
            font=("Courier",11,"bold"), bg=BG2, fg=ACCENT)
        self.sval.pack(side="right")

        self.slider = tk.Scale(r, from_=0.1, to=2.0, resolution=0.1,
            orient="horizontal", variable=self.strength,
            bg=BG2, fg=TEXT3, troughcolor=BG4,
            highlightthickness=0, showvalue=False,
            command=lambda v: self.sval.configure(text=f"{float(v):.1f}"))
        self.slider.pack(fill="x", padx=16)
        self.slider.configure(state="disabled")

        tk.Frame(r, bg=BG4, height=1).pack(fill="x", pady=12)

        def rb(text, cmd, bg, fg, hover):
            b = tk.Button(r, text=text,
                font=("Courier",9,"bold"),
                bg=bg, fg=fg, relief="flat",
                pady=9, cursor="hand2", state="disabled",
                activebackground=hover, activeforeground=fg,
                command=cmd)
            b.pack(fill="x", padx=16, pady=(0,6))
            return b

        self.btn_preview = rb(self.t("preview"),        self.preview_recovery, BG4,    TEXT,   BG5)
        self.btn_split   = rb(self.t("split"),          self.split_compare,    BG4,    BLUE,   BG5)
        self.btn_apply   = rb(self.t("apply"),          self.do_recovery,      GREEN2, GREEN,  "#1a4731")
        self.btn_batch   = rb(self.t("batch"),          self.batch_recovery,   "#3b1f5e", PURPLE, "#4a2870")
        self.btn_skip    = rb(self.t("skip"),           self.skip,             BG3,    TEXT2,  BG4)

        tk.Frame(r, bg=BG4, height=1).pack(fill="x", pady=(4,10))

        self.rec_tip = tk.Label(r, text="",
            font=("Courier",8), bg=BG2, fg=TEXT3,
            wraplength=218, justify="left")
        self.rec_tip.pack(padx=16, anchor="w")

    # ── WELCOME ──────────────────────────────────────────
    def _draw_welcome(self):
        self.pl.configure(text=self.t("welcome"),
            font=("Courier",11), fg=TEXT3, justify="center", image="")
        self.pl.image = None

    # ── STATS ────────────────────────────────────────────
    def _draw_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()
        sharp    = sum(1 for i in self.images if i["cat"] == "sharp"    and not i["del"])
        fixable  = sum(1 for i in self.images if i["cat"] == "fixable"  and not i["del"])
        rejected = sum(1 for i in self.images if i["cat"] == "rejected" and not i["del"])
        total    = sharp + fixable + rejected
        for key, n, col, col2 in [
            ("sharp",    sharp,    GREEN,  GREEN2),
            ("fixable",  fixable,  YELLOW, YELLOW2),
            ("rejected", rejected, RED,    RED2),
        ]:
            f = tk.Frame(self.stats_frame, bg=col2, pady=5)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=self.t(key),
                     font=("Courier",9,"bold"), bg=col2, fg=col).pack(side="left", padx=10)
            pct = f"{int(n/total*100)}%" if total > 0 else "—"
            tk.Label(f, text=f"{n}  {pct}",
                     font=("Courier",9,"bold"), bg=col2, fg=col).pack(side="right", padx=10)

    # ── OPEN FOLDER ──────────────────────────────────────
    def open_folder(self):
        folder = filedialog.askdirectory(title="Select photos folder")
        if not folder: return
        self.src_folder = Path(folder)
        self.images     = []
        self.cur        = None
        self.in_split   = False
        self._thumbs    = {}
        self._clear_list()
        self._reset_rec()
        self._draw_welcome()
        self.pl.configure(text=self.t("scanning"), font=("Courier",11), image="")
        self.pl.image = None
        self.preview_border.configure(bg=BG3)
        self.cat_indicator.configure(bg=BG3)
        self.cat_badge.configure(text="", bg=BG2)
        self.iname.configure(text="")
        self.iscore.configure(text="")
        self.exif_badge.configure(text="")
        self.pos_label.configure(text="")
        self.mode_overlay.configure(text="")
        self.btn_del_all.configure(state="disabled")
        self.btn_del_one.configure(state="disabled")
        self.btn_results.configure(state="disabled")
        self.cal_label.configure(text="")
        self.dirs = make_output_dirs(self.src_folder)
        threading.Thread(target=self._scan, daemon=True).start()

    # ── SCAN ─────────────────────────────────────────────
    def _scan(self):
        files = sorted([f for f in self.src_folder.iterdir()
                        if f.is_file() and f.suffix.lower() in supported()])
        total = len(files)
        if total == 0:
            self.root.after(0, lambda: self.pl.configure(
                text=self.t("no_images"), font=("Courier",11)))
            return

        # Pass 1 — score
        raw_scores, file_data = [], []
        for i, f in enumerate(files):
            sc      = score_image(f)
            shutter = get_shutter(f) if EXIF_AVAILABLE else None
            bt      = blur_type(shutter)
            raw_scores.append(sc)
            file_data.append((f, sc, shutter, bt))
            prog = int(((i+1)/total) * 0.5 * self.root.winfo_width())
            self.root.after(0, lambda p=prog: self.pbar.configure(width=p))

        # Calibrate
        self.sharp_t, self.fix_t = calibrate(raw_scores)
        cat_fn   = make_cat_fn(self.sharp_t, self.fix_t)
        cal_text = self.t("calibrated", f"{self.sharp_t:.0f}", f"{self.fix_t:.0f}")
        self.root.after(0, lambda t=cal_text: self.cal_label.configure(text=t))
        self.root.after(0, lambda: self.pl.configure(text=self.t("sorting")))

        # Pass 2 — sort and copy
        for i, (f, sc, shutter, bt) in enumerate(file_data):
            cat = cat_fn(sc)
            par = recovery_params(sc, self.sharp_t, bt)
            dst = copy_sorted(f, self.dirs[cat])
            try:
                pil   = open_pil(f)
                thumb = make_thumb(pil)
            except Exception:
                thumb = Image.new("RGB", (THUMB_W, THUMB_H), (24, 24, 24))

            self.images.append({
                "orig": f, "path": dst, "score": sc,
                "cat": cat, "par": par, "shutter": shutter,
                "blur": bt, "thumb": thumb,
                "del": False, "rec": False
            })
            prog = int((0.5 + (i+1)/total * 0.5) * self.root.winfo_width())
            self.root.after(0, lambda p=prog: self.pbar.configure(width=p))
            if i % 5 == 0 or i == total - 1:
                self.root.after(0, self._redraw_list)

        self.root.after(0, lambda: self.pbar.configure(width=0))
        self.root.after(0, self._redraw_list)
        self.root.after(0, lambda: self.btn_del_all.configure(state="normal"))
        self.root.after(0, lambda: self.btn_del_one.configure(state="normal"))
        self.root.after(0, lambda: self.btn_results.configure(state="normal"))
        self.root.after(0, lambda: self.btn_batch.configure(state="normal"))

        if self.images:
            first = next((i for i, m in enumerate(self.images)
                          if m["cat"] == "fixable"), 0)
            self.root.after(0, lambda: self.show(first))

    # ── LIST ─────────────────────────────────────────────
    def _clear_list(self):
        for w in self.listbox.winfo_children():
            w.destroy()
        self._thumbs = {}

    def _redraw_list(self):
        self._clear_list()
        self._draw_stats()
        for cat, col, col2 in [
            ("fixable",  YELLOW, YELLOW2),
            ("rejected", RED,    RED2),
            ("sharp",    GREEN,  GREEN2),
        ]:
            items = [i for i, m in enumerate(self.images)
                     if m["cat"] == cat and not m["del"]]
            if not items: continue

            hdr = tk.Frame(self.listbox, bg=col2)
            hdr.pack(fill="x", pady=(10,0))
            sym = {"fixable": "🔧", "rejected": "🗑", "sharp": "✓"}[cat]
            tk.Label(hdr,
                text=f"  {sym}  {self.t(cat).upper()}  ({len(items)})",
                font=("Courier",9,"bold"), bg=col2, fg=col, pady=5).pack(side="left")

            for idx in items:
                m      = self.images[idx]
                is_cur = (idx == self.cur)
                row_bg = BG4 if is_cur else BG3 if m["rec"] else BG2
                row    = tk.Frame(self.listbox, bg=row_bg, cursor="hand2")
                row.pack(fill="x", pady=1)

                tk.Frame(row, bg=col, width=3).pack(side="left", fill="y")

                try:
                    photo = ImageTk.PhotoImage(m["thumb"])
                    self._thumbs[idx] = photo
                    tk.Label(row, image=photo, bg=row_bg).pack(
                        side="left", padx=(6,4), pady=4)
                except Exception:
                    pass

                txt = tk.Frame(row, bg=row_bg)
                txt.pack(side="left", fill="both", expand=True, padx=(2,8), pady=4)

                name  = m["path"].name
                short = (name[:22]+"…") if len(name)>22 else name
                mark  = " ✓" if m["rec"] else ""
                blur_sym = {"motion": " 〜", "focus": " ⊙", "unknown": ""}[m["blur"]]

                tk.Label(txt, text=short+mark, font=("Courier",8,"bold"),
                         bg=row_bg, fg=TEXT, anchor="w").pack(anchor="w")
                tk.Label(txt,
                    text=f"{m['score']:.0f}  {blur_sym.strip()}  {shutter_str(m['shutter'])}",
                    font=("Courier",7), bg=row_bg, fg=TEXT3,
                    anchor="w").pack(anchor="w")

                for w in [row, txt] + list(txt.winfo_children()):
                    w.bind("<Button-1>", lambda e, i=idx: self.show(i))
                row.bind("<Button-1>", lambda e, i=idx: self.show(i))

    # ── SHOW ─────────────────────────────────────────────
    def show(self, idx):
        if idx < 0 or idx >= len(self.images): return
        self.cur       = idx
        self.in_split  = False
        self.rec_cache = None
        m = self.images[idx]

        try:
            pil = open_pil(m["path"])
            self.pil_cache = pil.copy()
            self._display(pil)
        except Exception as e:
            self.pl.configure(text=f"Cannot open:\n{e}",
                              font=("Courier",10), image="")
            self.pl.image  = None
            self.pil_cache = None

        col = CAT_COLOR[m["cat"]]
        self.preview_border.configure(bg=col)
        self.cat_indicator.configure(bg=col)
        self.cat_badge.configure(
            text=f"  {self.t(m['cat']).upper()} {'✓' if m['cat']=='sharp' else ''}  ",
            bg=CAT_COLOR2[m["cat"]], fg=col)

        self.iname.configure(text=m["path"].name)
        self.iscore.configure(
            text=f"  {m['score']:.1f}  ·  {REC_LABELS[m['par']['label_key']][self.lang_code]}",
            fg=col)

        bt     = m["blur"]
        bt_col = YELLOW if bt=="motion" else BLUE if bt=="focus" else TEXT3
        bt_lbl = (self.t("motion") if bt=="motion"
                  else self.t("focus") if bt=="focus"
                  else self.t("no_exif"))
        self.exif_badge.configure(
            text=f"  {shutter_str(m['shutter'])}  ·  {bt_lbl}  ",
            fg=bt_col)

        active = [i for i, x in enumerate(self.images) if not x["del"]]
        pos    = active.index(idx)+1 if idx in active else "?"
        self.pos_label.configure(text=self.t("pos", pos, len(active)))

        self.mode_overlay.configure(text=self.t("original"), bg=BG3, fg=TEXT3)
        self._update_rec(m)
        self._redraw_list()

    def _display(self, pil):
        w = max(self.pf.winfo_width(),  400)
        h = max(self.pf.winfo_height(), 300)
        p = pil.copy()
        p.thumbnail((w-6, h-6), Image.LANCZOS)
        photo = ImageTk.PhotoImage(p)
        self.pl.configure(image=photo, text="")
        self.pl.image = photo

    # ── RECOVERY PANEL ───────────────────────────────────
    def _update_rec(self, m):
        cat = m["cat"]
        sc  = m["score"]
        par = m["par"]

        if cat == "sharp":
            self.rec_status.configure(text=self.t("no_recovery"), fg=GREEN)
            self.rec_score_big.configure(text=f"{sc:.0f}", fg=GREEN)
            self.rec_score_sub.configure(text=self.t("laplacian"))
            self.rec_deficit.configure(text=self.t("threshold", f"{self.sharp_t:.0f}"))
            self.rec_label.configure(text="")
            self.blur_badge.configure(text="")
            self.rec_tip.configure(text="")
            self._set_rec_btns(False)
            return

        deficit   = self.sharp_t - sc
        suggested = round(min(2.0, max(0.5, 1.0 + deficit/(self.sharp_t*1.5))), 1)
        self.strength.set(suggested)
        self.sval.configure(text=f"{suggested:.1f}")

        col = YELLOW if cat=="fixable" else RED
        self.rec_status.configure(
            text=self.t("fixable_status") if cat=="fixable"
                 else self.t("rejected_status"),
            fg=col)
        self.rec_score_big.configure(text=f"{sc:.0f}", fg=col)
        self.rec_score_sub.configure(text=self.t("need", f"{self.sharp_t:.0f}"))
        self.rec_deficit.configure(text=self.t("deficit", f"{deficit:.0f}"))
        self.rec_label.configure(
            text=REC_LABELS[par["label_key"]][self.lang_code])

        bt_col = YELLOW if m["blur"]=="motion" else BLUE
        self.blur_badge.configure(
            text=(self.t("motion_blur") if m["blur"]=="motion"
                  else self.t("focus_error") if m["blur"]=="focus"
                  else self.t("blur_unknown")),
            fg=bt_col)

        strat = self.t("strategy_dir") if m["blur"]=="motion" else self.t("strategy_rad")
        self.rec_tip.configure(
            text=f"{self.t('passes', par['passes'], par['radius'])}\n"
                 f"{strat}\n"
                 f"{self.t('strength_auto')}")
        self._set_rec_btns(True)

    def _set_rec_btns(self, on):
        st = "normal" if on else "disabled"
        for b in [self.slider, self.btn_preview, self.btn_split,
                  self.btn_apply, self.btn_skip]:
            b.configure(state=st)

    def _reset_rec(self):
        self.rec_status.configure(text=self.t("open_begin"), fg=TEXT3)
        self.rec_score_big.configure(text="", fg=TEXT3)
        self.rec_score_sub.configure(text="")
        self.rec_deficit.configure(text="")
        self.rec_label.configure(text="")
        self.blur_badge.configure(text="")
        self.rec_tip.configure(text="")
        self.exif_badge.configure(text="")
        self._set_rec_btns(False)
        self.btn_batch.configure(state="disabled")

    # ── RECOVERY ACTIONS ─────────────────────────────────
    def _get_recovered(self):
        if self.pil_cache is None or self.cur is None: return None
        m = self.images[self.cur]
        return apply_recovery(self.pil_cache, m["par"], self.strength.get())

    def preview_recovery(self):
        rec = self._get_recovered()
        if rec is None: return
        self.rec_cache = rec
        self.in_split  = False
        self._display(rec)
        m = self.images[self.cur]
        self.iscore.configure(
            text=f"  {self.t('preview_mode')}  ·  {self.strength.get():.1f}", fg=BLUE)
        self.mode_overlay.configure(text=self.t("preview_mode"), bg="#1a2a3a", fg=BLUE)

    def split_compare(self):
        if self.pil_cache is None or self.cur is None: return
        rec = self._get_recovered()
        if rec is None: return
        self.rec_cache = rec
        split = make_split(self.pil_cache, rec,
                           self.t("split_label_orig"),
                           self.t("split_label_rec"))
        self.in_split = True
        self._display(split)
        self.iscore.configure(
            text=f"  {self.t('split_mode')}  ·  {self.strength.get():.1f}", fg=PURPLE)
        self.mode_overlay.configure(text=self.t("split_mode"), bg="#2a1a3a", fg=PURPLE)

    def do_recovery(self):
        rec = self._get_recovered()
        if rec is None: return
        m        = self.images[self.cur]
        strength = self.strength.get()
        self._save_rec(m, rec)
        self._redraw_list()
        self.iscore.configure(
            text=f"  {self.t('recovered_save', f'{strength:.1f}')}", fg=GREEN)
        self.preview_border.configure(bg=GREEN)
        self.cat_indicator.configure(bg=GREEN)
        self.cat_badge.configure(text=self.t("sharp_badge"), bg=GREEN2, fg=GREEN)
        self.mode_overlay.configure(text=self.t("recovered_mode"), bg=GREEN2, fg=GREEN)
        self.rec_status.configure(text=self.t("rec_saved"), fg=GREEN)
        self._set_rec_btns(False)
        self.root.after(800, self._next_fixable)

    def _save_rec(self, m, rec_img):
        suffix   = m["path"].suffix.lower()
        save_suf = ".tiff" if suffix in RAW_FMT else suffix
        sp       = self.dirs["sharp"] / f"{m['path'].stem}_recovered{save_suf}"
        try:
            rec_img.save(str(sp), quality=95)
        except Exception:
            sp = self.dirs["sharp"] / f"{m['path'].stem}_recovered.jpg"
            rec_img.save(str(sp), quality=95)
        m["rec"]  = True
        m["path"] = sp
        m["cat"]  = "sharp"
        try:
            m["thumb"] = make_thumb(rec_img)
        except Exception:
            pass

    def batch_recovery(self):
        pending = [i for i, m in enumerate(self.images)
                   if m["cat"]=="fixable" and not m["del"] and not m["rec"]]
        if not pending:
            messagebox.showinfo("", self.t("batch_none"))
            return
        strength = self.strength.get()
        if not messagebox.askyesno("",
            self.t("batch_confirm", f"{strength:.1f}", len(pending))): return

        self.btn_batch.configure(state="disabled",
                                 text=self.t("batch_progress"))
        self.root.update()

        def _run():
            done = 0
            for idx in pending:
                m = self.images[idx]
                try:
                    pil = open_pil(m["path"])
                    rec = apply_recovery(pil, m["par"], strength)
                    self._save_rec(m, rec)
                    done += 1
                except Exception:
                    pass
                self.root.after(0, self._redraw_list)
            self.root.after(0, lambda: self.btn_batch.configure(
                state="normal", text=self.t("batch")))
            self.root.after(0, lambda d=done: messagebox.showinfo(
                "", self.t("batch_done", d)))

        threading.Thread(target=_run, daemon=True).start()

    def skip(self):
        self._next_fixable()

    def _next_fixable(self):
        nxt = [i for i, m in enumerate(self.images)
               if m["cat"] in ("fixable","rejected") and not m["del"] and not m["rec"]]
        if nxt:
            self.show(nxt[0])
        else:
            self.rec_status.configure(text=self.t("all_done"), fg=GREEN)
            self._set_rec_btns(False)

    # ── NAVIGATION ───────────────────────────────────────
    def prev(self):
        if self.cur is None: return
        active = [i for i, m in enumerate(self.images) if not m["del"]]
        if not active: return
        pos = active.index(self.cur) if self.cur in active else 0
        if pos > 0: self.show(active[pos-1])

    def next(self):
        if self.cur is None: return
        active = [i for i, m in enumerate(self.images) if not m["del"]]
        if not active: return
        pos = active.index(self.cur) if self.cur in active else 0
        if pos < len(active)-1: self.show(active[pos+1])

    # ── DELETE ───────────────────────────────────────────
    def delete_one(self):
        if self.cur is None: return
        m = self.images[self.cur]
        if m["del"]: return
        if not messagebox.askyesno("", self.t("delete_confirm", m["path"].name)): return
        try:
            os.remove(m["path"])
            m["del"] = True
            self._redraw_list()
            self.next()
        except Exception as e:
            messagebox.showerror("", str(e))

    def delete_all_rejected(self):
        rej = [m for m in self.images if m["cat"]=="rejected" and not m["del"]]
        if not rej:
            messagebox.showinfo("", self.t("delete_none"))
            return
        if not messagebox.askyesno("",
            self.t("delete_all_confirm", len(rej))): return
        n = 0
        for m in rej:
            try:
                os.remove(m["path"])
                m["del"] = True
                n += 1
            except Exception: pass
        self._redraw_list()
        self.pl.configure(text=self.t("deleted_msg", n),
                          font=("Courier",11), image="")
        self.pl.image = None
        self.iname.configure(text="")
        self.iscore.configure(text="")
        self.preview_border.configure(bg=BG3)
        messagebox.showinfo("", self.t("deleted_title", n))

    # ── OPEN RESULTS ─────────────────────────────────────
    def open_results(self):
        if not self.dirs: return
        path = list(self.dirs.values())[0].parent
        try:
            if sys.platform == "win32":    os.startfile(str(path))
            elif sys.platform == "darwin": subprocess.Popen(["open", str(path)])
            else:                          subprocess.Popen(["xdg-open", str(path)])
        except Exception as e:
            messagebox.showerror("", str(e))


# ── RUN ───────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
