#!/usr/bin/env python3
"""
FocusCheck — Culling & Sharpness Recovery Tool
Part of the ImageStream Local Suite — The Art Medium

Workflow:
  1. Open folder
  2. Every image scored by Laplacian variance
  3. Copied into FocusCheck_Results/sharp/ fixable/ rejected/
  4. Fixable images get a targeted recovery panel driven by their score
  5. Apply recovery — saved into sharp/
  6. Delete rejected in one click
  7. Open Results Folder — straight to your keepers

Supports JPG PNG TIFF BMP WebP + RAW (CR2 NEF ARW DNG RAF ORF RW2 CR3)
Originals are never touched.
"""

import cv2
import os
import shutil
import subprocess
import sys
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk, ImageFilter
import threading

# ── RAW ──────────────────────────────────────────────────
try:
    import rawpy
    RAW_AVAILABLE = True
except ImportError:
    RAW_AVAILABLE = False

# ── FORMATS ──────────────────────────────────────────────
STD_FMT = {".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp"}
RAW_FMT = {".cr2", ".nef", ".arw", ".dng", ".raf", ".orf", ".rw2", ".raw", ".cr3"}

def supported():
    return STD_FMT | RAW_FMT if RAW_AVAILABLE else STD_FMT

# ── THRESHOLDS ───────────────────────────────────────────
SHARP    = 150
FIXABLE  = 50

# ── PALETTE ──────────────────────────────────────────────
BG     = "#0f0f0f"
BG2    = "#161616"
BG3    = "#1f1f1f"
BG4    = "#252525"
ACCENT = "#f5a623"
GREEN  = "#52b788"
RED    = "#e63946"
YELLOW = "#f4d35e"
BLUE   = "#7eb8f7"
TEXT   = "#f0f0f0"
TEXT2  = "#999999"
TEXT3  = "#555555"

# ── IMAGE IO ─────────────────────────────────────────────
def open_pil(path):
    if Path(path).suffix.lower() in RAW_FMT and RAW_AVAILABLE:
        with rawpy.imread(str(path)) as r:
            rgb = r.postprocess(use_camera_wb=True, half_size=True,
                                no_auto_bright=False, output_bps=8)
        return Image.fromarray(rgb)
    return Image.open(str(path))

def open_cv2(path):
    if Path(path).suffix.lower() in RAW_FMT and RAW_AVAILABLE:
        with rawpy.imread(str(path)) as r:
            rgb = r.postprocess(use_camera_wb=True, half_size=True,
                                no_auto_bright=False, output_bps=8)
        return cv2.cvtColor(rgb, cv2.COLOR_RGB2BGR)
    return cv2.imread(str(path))

# ── SCORING ──────────────────────────────────────────────
def score_image(path):
    try:
        img = open_cv2(path)
        if img is None:
            return 0.0
        gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
        return float(cv2.Laplacian(gray, cv2.CV_64F).var())
    except Exception:
        return 0.0

def category(score):
    if score >= SHARP:   return "sharp"
    if score >= FIXABLE: return "fixable"
    return "rejected"

# ── RECOVERY PARAMS (driven by Laplacian score) ──────────
def recovery_params(score):
    """
    The further below SHARP, the harder we push.
    Returns dict consumed by apply_recovery().
    """
    deficit = SHARP - score
    if deficit <= 50:          # score 100-149 — slightly soft
        return dict(radius=1, percent=130, threshold=3,
                    edge=False, passes=1, label="Gentle")
    elif deficit <= 100:       # score 50-99 — moderately soft
        return dict(radius=2, percent=170, threshold=2,
                    edge=True,  passes=1, label="Medium")
    else:                      # score < 50 — significantly soft
        return dict(radius=2, percent=210, threshold=1,
                    edge=True,  passes=2, label="Strong")

def apply_recovery(pil_img, params, strength):
    """
    Strength is the user slider (0.1 – 2.0).
    Scales the unsharp percent proportionally.
    """
    img     = pil_img.copy()
    percent = int(params["percent"] * strength)
    percent = max(100, min(percent, 500))
    for _ in range(params["passes"]):
        img = img.filter(ImageFilter.UnsharpMask(
            radius=params["radius"],
            percent=percent,
            threshold=params["threshold"]))
    if params["edge"] and strength > 0.3:
        img = img.filter(ImageFilter.EDGE_ENHANCE)
    return img

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
        self.root = root
        self.root.title("FocusCheck — ImageStream Local Suite")
        self.root.configure(bg=BG)
        self.root.geometry("1200x750")
        self.root.minsize(1000, 640)

        self.images     = []
        self.cur        = None   # current index
        self.dirs       = {}     # output dir dict
        self.src_folder = None
        self.pil_cache  = None   # original PIL of current image

        self.strength   = tk.DoubleVar(value=1.0)

        self._build()
        if not RAW_AVAILABLE:
            self.root.after(500, lambda: messagebox.showwarning(
                "RAW unavailable",
                "rawpy not found — RAW files will be skipped.\n\npip install rawpy"))

    # ── BUILD ────────────────────────────────────────────
    def _build(self):
        self._topbar()
        body = tk.Frame(self.root, bg=BG)
        body.pack(fill="both", expand=True)
        self._left(body)
        self._center(body)
        self._right(body)

    def _topbar(self):
        bar = tk.Frame(self.root, bg=BG2, height=54)
        bar.pack(fill="x")
        bar.pack_propagate(False)
        tk.Label(bar, text="Focus",  font=("Helvetica",18,"bold"), bg=BG2, fg=TEXT).pack(side="left", padx=(20,0), pady=10)
        tk.Label(bar, text="Check",  font=("Helvetica",18,"bold"), bg=BG2, fg=ACCENT).pack(side="left", pady=10)
        tk.Label(bar, text="— Culling & Recovery", font=("Helvetica",12), bg=BG2, fg=TEXT2).pack(side="left", padx=10)
        tk.Label(bar, text="RAW ✓" if RAW_AVAILABLE else "RAW ✗",
                 font=("Helvetica",10,"bold"), bg=BG3,
                 fg=GREEN if RAW_AVAILABLE else TEXT3,
                 padx=8, pady=3).pack(side="left", padx=8)
        tk.Button(bar, text="📂  Open Folder",
                  font=("Helvetica",11,"bold"), bg=ACCENT, fg=BG,
                  relief="flat", padx=16, pady=6, cursor="hand2",
                  command=self.open_folder).pack(side="right", padx=20, pady=10)

    def _left(self, body):
        left = tk.Frame(body, bg=BG2, width=270)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        self.stats = tk.Frame(left, bg=BG2)
        self.stats.pack(fill="x", padx=10, pady=(12,0))
        self._draw_stats()

        self.btn_results = tk.Button(left, text="📁  Open Results Folder",
            font=("Helvetica",10), bg=BG3, fg=TEXT2, relief="flat",
            pady=5, cursor="hand2", command=self.open_results, state="disabled")
        self.btn_results.pack(fill="x", padx=10, pady=(8,4))

        lc = tk.Frame(left, bg=BG2)
        lc.pack(fill="both", expand=True, pady=4)
        cv = tk.Canvas(lc, bg=BG2, highlightthickness=0)
        sb = tk.Scrollbar(lc, orient="vertical", command=cv.yview)
        self.listbox = tk.Frame(cv, bg=BG2)
        self.listbox.bind("<Configure>", lambda e: cv.configure(scrollregion=cv.bbox("all")))
        cv.create_window((0,0), window=self.listbox, anchor="nw")
        cv.configure(yscrollcommand=sb.set)
        cv.pack(side="left", fill="both", expand=True)
        sb.pack(side="right", fill="y")

    def _center(self, body):
        center = tk.Frame(body, bg=BG)
        center.pack(side="left", fill="both", expand=True)

        self.pf = tk.Frame(center, bg=BG)
        self.pf.pack(fill="both", expand=True, padx=16, pady=16)
        self.pl = tk.Label(self.pf, bg=BG,
            text="📂\n\nOpen a folder to begin",
            font=("Helvetica",14), fg=TEXT3)
        self.pl.pack(expand=True)

        info = tk.Frame(center, bg=BG2, height=44)
        info.pack(fill="x")
        info.pack_propagate(False)
        self.iname  = tk.Label(info, text="", font=("Helvetica",11,"bold"), bg=BG2, fg=TEXT)
        self.iname.pack(side="left", padx=16, pady=10)
        self.iscore = tk.Label(info, text="", font=("Helvetica",11), bg=BG2, fg=TEXT2)
        self.iscore.pack(side="left", padx=6, pady=10)

        nav = tk.Frame(center, bg=BG3, height=60)
        nav.pack(fill="x")
        nav.pack_propagate(False)
        tk.Button(nav, text="◀  Prev", font=("Helvetica",11), bg=BG2, fg=TEXT2,
                  relief="flat", padx=14, pady=8, cursor="hand2",
                  command=self.prev).pack(side="left", padx=(14,4), pady=10)
        tk.Button(nav, text="Next  ▶", font=("Helvetica",11), bg=BG2, fg=TEXT2,
                  relief="flat", padx=14, pady=8, cursor="hand2",
                  command=self.next).pack(side="left", padx=4, pady=10)
        self.btn_del_all = tk.Button(nav, text="🗑  Delete All Rejected",
            font=("Helvetica",11,"bold"), bg="#8b0000", fg=TEXT, relief="flat",
            padx=14, pady=8, cursor="hand2", state="disabled",
            command=self.delete_all_rejected)
        self.btn_del_all.pack(side="right", padx=(4,14), pady=10)
        self.btn_del_one = tk.Button(nav, text="🗑  Delete This",
            font=("Helvetica",11,"bold"), bg=RED, fg=TEXT, relief="flat",
            padx=14, pady=8, cursor="hand2", state="disabled",
            command=self.delete_one)
        self.btn_del_one.pack(side="right", padx=4, pady=10)

        self.pbar_bg = tk.Frame(center, bg=BG, height=4)
        self.pbar_bg.pack(fill="x")
        self.pbar = tk.Frame(self.pbar_bg, bg=ACCENT, height=4, width=0)
        self.pbar.pack(side="left")

    def _right(self, body):
        r = tk.Frame(body, bg=BG2, width=230)
        r.pack(side="right", fill="y")
        r.pack_propagate(False)

        tk.Label(r, text="RECOVERY", font=("Helvetica",9,"bold"),
                 bg=BG2, fg=ACCENT, pady=10).pack(fill="x", padx=14)
        tk.Frame(r, bg=BG3, height=1).pack(fill="x")

        self.rec_status = tk.Label(r,
            text="Select a fixable or\nrejected image to begin",
            font=("Helvetica",10), bg=BG2, fg=TEXT3,
            justify="center", pady=16)
        self.rec_status.pack(fill="x", padx=14)

        self.rec_score_big = tk.Label(r, text="", font=("Helvetica",26,"bold"), bg=BG2, fg=YELLOW)
        self.rec_score_big.pack()
        self.rec_score_sub = tk.Label(r, text="", font=("Helvetica",9), bg=BG2, fg=TEXT3)
        self.rec_score_sub.pack()

        tk.Frame(r, bg=BG3, height=1).pack(fill="x", pady=10)

        self.rec_label = tk.Label(r, text="", font=("Helvetica",10,"bold"), bg=BG2, fg=BLUE)
        self.rec_label.pack(padx=14, anchor="w")

        tk.Label(r, text="Strength", font=("Helvetica",10), bg=BG2, fg=TEXT2).pack(padx=14, pady=(10,2), anchor="w")

        srow = tk.Frame(r, bg=BG2)
        srow.pack(fill="x", padx=14)
        self.sval = tk.Label(srow, text="1.0", font=("Helvetica",11,"bold"), bg=BG2, fg=ACCENT)
        self.sval.pack(side="right")

        self.slider = tk.Scale(r, from_=0.1, to=2.0, resolution=0.1,
            orient="horizontal", variable=self.strength, bg=BG2, fg=TEXT2,
            troughcolor=BG3, highlightthickness=0, showvalue=False,
            command=lambda v: self.sval.configure(text=f"{float(v):.1f}"))
        self.slider.pack(fill="x", padx=14)
        self.slider.configure(state="disabled")

        tk.Frame(r, bg=BG3, height=1).pack(fill="x", pady=10)

        self.btn_preview = tk.Button(r, text="👁  Preview",
            font=("Helvetica",10,"bold"), bg=BG4, fg=TEXT, relief="flat",
            pady=8, cursor="hand2", state="disabled", command=self.preview_recovery)
        self.btn_preview.pack(fill="x", padx=14, pady=(0,6))

        self.btn_apply = tk.Button(r, text="✓  Apply & Save to Sharp",
            font=("Helvetica",10,"bold"), bg=GREEN, fg=BG, relief="flat",
            pady=10, cursor="hand2", state="disabled", command=self.do_recovery)
        self.btn_apply.pack(fill="x", padx=14, pady=(0,6))

        self.btn_skip = tk.Button(r, text="→  Skip / Keep Original",
            font=("Helvetica",10), bg=BG3, fg=TEXT2, relief="flat",
            pady=7, cursor="hand2", state="disabled", command=self.skip)
        self.btn_skip.pack(fill="x", padx=14, pady=(0,4))

        tk.Frame(r, bg=BG3, height=1).pack(fill="x", pady=10)

        self.rec_tip = tk.Label(r, text="", font=("Helvetica",9),
            bg=BG2, fg=TEXT3, wraplength=200, justify="left")
        self.rec_tip.pack(padx=14, anchor="w")

    # ── STATS ────────────────────────────────────────────
    def _draw_stats(self):
        for w in self.stats.winfo_children():
            w.destroy()
        sharp    = sum(1 for i in self.images if i["cat"] == "sharp"    and not i["del"])
        fixable  = sum(1 for i in self.images if i["cat"] == "fixable"  and not i["del"])
        rejected = sum(1 for i in self.images if i["cat"] == "rejected" and not i["del"])
        for lbl, n, col in [("✅ Sharp", sharp, GREEN), ("🔧 Fixable", fixable, YELLOW), ("🗑 Rejected", rejected, RED)]:
            f = tk.Frame(self.stats, bg=BG3, pady=5)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=lbl,  font=("Helvetica",10), bg=BG3, fg=TEXT2).pack(side="left",  padx=10)
            tk.Label(f, text=str(n), font=("Helvetica",10,"bold"), bg=BG3, fg=col).pack(side="right", padx=10)

    # ── OPEN FOLDER ──────────────────────────────────────
    def open_folder(self):
        folder = filedialog.askdirectory(title="Select photos folder")
        if not folder:
            return
        self.src_folder = Path(folder)
        self.images     = []
        self.cur        = None
        self._clear_list()
        self._reset_rec()
        self.pl.configure(text="Scanning and sorting...", image="")
        self.pl.image = None
        self.btn_del_all.configure(state="disabled")
        self.btn_del_one.configure(state="disabled")
        self.btn_results.configure(state="disabled")
        self.dirs = make_output_dirs(self.src_folder)
        threading.Thread(target=self._scan, daemon=True).start()

    def _scan(self):
        files = sorted([f for f in self.src_folder.iterdir()
                        if f.is_file() and f.suffix.lower() in supported()])
        total = len(files)
        if total == 0:
            self.root.after(0, lambda: self.pl.configure(text="No supported images found."))
            return

        for i, f in enumerate(files):
            sc  = score_image(f)
            cat = category(sc)
            par = recovery_params(sc)
            dst = copy_sorted(f, self.dirs[cat])
            self.images.append({"orig": f, "path": dst, "score": sc,
                                 "cat": cat, "par": par, "del": False, "rec": False})
            prog = int(((i+1)/total) * self.root.winfo_width())
            self.root.after(0, lambda p=prog: self.pbar.configure(width=p))
            self.root.after(0, self._redraw_list)

        self.root.after(0, lambda: self.pbar.configure(width=0))
        self.root.after(0, self._redraw_list)
        self.root.after(0, lambda: self.btn_del_all.configure(state="normal"))
        self.root.after(0, lambda: self.btn_del_one.configure(state="normal"))
        self.root.after(0, lambda: self.btn_results.configure(state="normal"))
        if self.images:
            first_fix = next((i for i, m in enumerate(self.images) if m["cat"] == "fixable"), 0)
            self.root.after(0, lambda: self.show(first_fix))

    # ── LIST ─────────────────────────────────────────────
    def _clear_list(self):
        for w in self.listbox.winfo_children():
            w.destroy()

    def _redraw_list(self):
        self._clear_list()
        self._draw_stats()
        for cat, lbl, col in [("fixable","🔧  FIXABLE",YELLOW), ("rejected","🗑  REJECTED",RED), ("sharp","✅  SHARP",GREEN)]:
            items = [i for i, m in enumerate(self.images) if m["cat"] == cat and not m["del"]]
            if not items:
                continue
            h = tk.Frame(self.listbox, bg=BG3)
            h.pack(fill="x", pady=(8,2))
            tk.Label(h, text=f"{lbl}  ({len(items)})", font=("Helvetica",9,"bold"),
                     bg=BG3, fg=col).pack(side="left", padx=12, pady=4)
            for idx in items:
                m      = self.images[idx]
                rbg    = BG4 if m["rec"] else BG2
                row    = tk.Frame(self.listbox, bg=rbg, cursor="hand2")
                row.pack(fill="x", pady=1)
                name   = m["path"].name
                short  = (name[:24]+"…") if len(name)>24 else name
                marker = " ✓" if m["rec"] else ""
                tk.Label(row, text=short+marker, font=("Helvetica",9), bg=rbg, fg=TEXT, anchor="w").pack(side="left",  padx=10, pady=5)
                tk.Label(row, text=f"{m['score']:.0f}", font=("Helvetica",9), bg=rbg, fg=TEXT3).pack(side="right", padx=10, pady=5)
                row.bind("<Button-1>", lambda e, i=idx: self.show(i))
                for c in row.winfo_children():
                    c.bind("<Button-1>", lambda e, i=idx: self.show(i))

    # ── SHOW IMAGE ───────────────────────────────────────
    def show(self, idx):
        if idx < 0 or idx >= len(self.images):
            return
        self.cur = idx
        m = self.images[idx]
        try:
            pil = open_pil(m["path"])
            self.pil_cache = pil.copy()
            w = self.pf.winfo_width()  or 700
            h = self.pf.winfo_height() or 500
            pil.thumbnail((w-20, h-20), Image.LANCZOS)
            photo = ImageTk.PhotoImage(pil)
            self.pl.configure(image=photo, text="")
            self.pl.image = photo
        except Exception as e:
            self.pl.configure(text=f"Cannot open: {e}", image="")
            self.pl.image = None
            self.pil_cache = None

        col = {"sharp": GREEN, "fixable": YELLOW, "rejected": RED}[m["cat"]]
        self.iname.configure(text=m["path"].name)
        self.iscore.configure(
            text=f"Score: {m['score']:.1f}  ·  {m['cat'].upper()}  ·  {m['par']['label']}",
            fg=col)
        self._update_rec(m)

    # ── RECOVERY PANEL ───────────────────────────────────
    def _update_rec(self, m):
        cat   = m["cat"]
        sc    = m["score"]
        par   = m["par"]

        if cat == "sharp":
            self.rec_status.configure(text="Sharp — no recovery needed.", fg=GREEN)
            self.rec_score_big.configure(text=f"{sc:.0f}", fg=GREEN)
            self.rec_score_sub.configure(text="Laplacian score")
            self.rec_label.configure(text="")
            self.rec_tip.configure(text="")
            self._rec_btns(False)
            return

        deficit   = SHARP - sc
        suggested = round(min(2.0, max(0.5, 1.0 + deficit / 200)), 1)
        self.strength.set(suggested)
        self.sval.configure(text=f"{suggested:.1f}")

        if cat == "fixable":
            self.rec_status.configure(text="Fixable — adjust strength\nand apply recovery.", fg=YELLOW)
        else:
            self.rec_status.configure(text="Rejected — try recovery\nbefore deleting.", fg=RED)

        self.rec_score_big.configure(text=f"{sc:.0f}", fg=YELLOW if cat=="fixable" else RED)
        self.rec_score_sub.configure(text=f"Need {SHARP} to be sharp  (deficit {deficit:.0f})")
        self.rec_label.configure(text=f"{par['label']} recovery")
        self.rec_tip.configure(text=f"Passes: {par['passes']}  ·  Kernel: {par['radius']}px\n"
                                     f"Slider pre-set from score deficit.")
        self._rec_btns(True)

    def _rec_btns(self, on):
        st = "normal" if on else "disabled"
        for w in [self.slider, self.btn_preview, self.btn_apply, self.btn_skip]:
            w.configure(state=st)

    def _reset_rec(self):
        self.rec_status.configure(text="Select a fixable or\nrejected image to begin", fg=TEXT3)
        self.rec_score_big.configure(text="")
        self.rec_score_sub.configure(text="")
        self.rec_label.configure(text="")
        self.rec_tip.configure(text="")
        self._rec_btns(False)

    # ── RECOVERY ACTIONS ─────────────────────────────────
    def preview_recovery(self):
        if self.pil_cache is None or self.cur is None:
            return
        m         = self.images[self.cur]
        recovered = apply_recovery(self.pil_cache, m["par"], self.strength.get())
        w = self.pf.winfo_width()  or 700
        h = self.pf.winfo_height() or 500
        p = recovered.copy()
        p.thumbnail((w-20, h-20), Image.LANCZOS)
        photo = ImageTk.PhotoImage(p)
        self.pl.configure(image=photo, text="")
        self.pl.image = photo
        self.iscore.configure(
            text=f"PREVIEW  ·  Score {m['score']:.1f}  ·  Strength {self.strength.get():.1f}",
            fg=BLUE)

    def do_recovery(self):
        if self.pil_cache is None or self.cur is None:
            return
        m         = self.images[self.cur]
        strength  = self.strength.get()
        recovered = apply_recovery(self.pil_cache, m["par"], strength)

        suffix    = m["path"].suffix.lower()
        save_suf  = ".tiff" if suffix in RAW_FMT else suffix
        save_name = f"{m['path'].stem}_recovered{save_suf}"
        save_path = self.dirs["sharp"] / save_name
        try:
            recovered.save(str(save_path), quality=95)
        except Exception:
            save_path = self.dirs["sharp"] / f"{m['path'].stem}_recovered.jpg"
            recovered.save(str(save_path), quality=95)

        m["rec"]  = True
        m["path"] = save_path
        m["cat"]  = "sharp"
        self._redraw_list()
        self.iscore.configure(text=f"✓ Recovered → sharp/  ·  Strength {strength:.1f}", fg=GREEN)
        self.rec_status.configure(text="Recovered ✓\nSaved to sharp/", fg=GREEN)
        self._rec_btns(False)
        self.root.after(700, self._next_fixable)

    def skip(self):
        self._next_fixable()

    def _next_fixable(self):
        nxt = [i for i, m in enumerate(self.images)
               if m["cat"] in ("fixable","rejected") and not m["del"] and not m["rec"]]
        if nxt:
            self.show(nxt[0])
        else:
            self.rec_status.configure(text="All fixable images\nprocessed ✓", fg=GREEN)
            self._rec_btns(False)

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
        if not messagebox.askyesno("Delete", f"Delete:\n{m['path'].name}\n\nCannot be undone."): return
        try:
            os.remove(m["path"])
            m["del"] = True
            self._redraw_list()
            self.next()
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def delete_all_rejected(self):
        rej = [m for m in self.images if m["cat"] == "rejected" and not m["del"]]
        if not rej:
            messagebox.showinfo("Nothing to delete", "No rejected images left.")
            return
        if not messagebox.askyesno("Delete All Rejected",
            f"Permanently delete {len(rej)} rejected images?\n\nCannot be undone."): return
        n = 0
        for m in rej:
            try:
                os.remove(m["path"])
                m["del"] = True
                n += 1
            except Exception: pass
        self._redraw_list()
        self.pl.configure(text=f"✅ Deleted {n} rejected images.", image="")
        self.pl.image = None
        self.iname.configure(text="")
        self.iscore.configure(text="")
        messagebox.showinfo("Done", f"✅ Deleted {n} rejected images.\nSpace freed!")

    # ── OPEN RESULTS ─────────────────────────────────────
    def open_results(self):
        if not self.dirs: return
        path = list(self.dirs.values())[0].parent
        try:
            if sys.platform == "win32":    os.startfile(str(path))
            elif sys.platform == "darwin": subprocess.Popen(["open", str(path)])
            else:                          subprocess.Popen(["xdg-open", str(path)])
        except Exception as e:
            messagebox.showerror("Error", str(e))


# ── RUN ───────────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    App(root)
    root.mainloop()
