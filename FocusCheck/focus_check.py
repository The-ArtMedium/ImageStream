#!/usr/bin/env python3
"""
FocusCheck — Visual photo culling tool.
Part of the ImageStream Local Suite.

Scans a folder, scores every image for sharpness,
groups them into Sharp / Fixable / Rejected,
and lets you preview and delete rejects visually.

Non-destructive until YOU choose to delete.
"""

import cv2
import os
import sys
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox
from pathlib import Path
from PIL import Image, ImageTk
import threading

# ── THRESHOLDS ───────────────────────────────────────────
SHARP_THRESHOLD   = 150
FIXABLE_THRESHOLD = 50
SUPPORTED_FORMATS = (".jpg", ".jpeg", ".png", ".tiff", ".tif", ".bmp", ".webp")

# ── COLORS ───────────────────────────────────────────────
BG        = "#0f0f0f"
BG2       = "#161616"
BG3       = "#1f1f1f"
ACCENT    = "#f5a623"
GREEN     = "#52b788"
RED       = "#e63946"
YELLOW    = "#f4d35e"
TEXT      = "#f0f0f0"
TEXT2     = "#999999"
TEXT3     = "#555555"

# ── FOCUS SCORING ────────────────────────────────────────
def calculate_focus_score(image_path):
    image = cv2.imread(str(image_path))
    if image is None:
        return 0
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    laplacian = cv2.Laplacian(gray, cv2.CV_64F)
    return laplacian.var()

def get_category(score):
    if score >= SHARP_THRESHOLD:
        return "sharp"
    elif score >= FIXABLE_THRESHOLD:
        return "fixable"
    else:
        return "rejected"

# ── MAIN APP ─────────────────────────────────────────────
class FocusCheckApp:
    def __init__(self, root):
        self.root = root
        self.root.title("FocusCheck — ImageStream Local Suite")
        self.root.configure(bg=BG)
        self.root.geometry("1100x700")
        self.root.minsize(900, 600)

        self.images = []          # list of dicts: {path, score, category, deleted}
        self.current_index = None
        self.folder_path = None
        self.scan_thread = None

        self._build_ui()

    # ── UI BUILD ─────────────────────────────────────────
    def _build_ui(self):
        # Top bar
        topbar = tk.Frame(self.root, bg=BG2, height=54)
        topbar.pack(fill="x", side="top")
        topbar.pack_propagate(False)

        tk.Label(topbar, text="Focus", font=("Helvetica", 18, "bold"),
                 bg=BG2, fg=TEXT).pack(side="left", padx=(20, 0), pady=10)
        tk.Label(topbar, text="Check", font=("Helvetica", 18, "bold"),
                 bg=BG2, fg=ACCENT).pack(side="left", pady=10)
        tk.Label(topbar, text="— Visual Culling Tool",
                 font=("Helvetica", 12), bg=BG2, fg=TEXT2).pack(side="left", padx=10, pady=10)

        self.btn_open = tk.Button(topbar, text="📂  Open Folder",
                                  font=("Helvetica", 11, "bold"),
                                  bg=ACCENT, fg=BG, relief="flat",
                                  padx=16, pady=6, cursor="hand2",
                                  command=self.open_folder)
        self.btn_open.pack(side="right", padx=20, pady=10)

        # Main area
        main = tk.Frame(self.root, bg=BG)
        main.pack(fill="both", expand=True)

        # Left panel — image list
        left = tk.Frame(main, bg=BG2, width=260)
        left.pack(side="left", fill="y")
        left.pack_propagate(False)

        # Stats row
        self.stats_frame = tk.Frame(left, bg=BG2)
        self.stats_frame.pack(fill="x", padx=12, pady=(12, 0))
        self._build_stats()

        # Category sections
        list_container = tk.Frame(left, bg=BG2)
        list_container.pack(fill="both", expand=True, padx=0, pady=8)

        canvas = tk.Canvas(list_container, bg=BG2, highlightthickness=0)
        scrollbar = tk.Scrollbar(list_container, orient="vertical", command=canvas.yview)
        self.list_frame = tk.Frame(canvas, bg=BG2)

        self.list_frame.bind("<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all")))

        canvas.create_window((0, 0), window=self.list_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        # Right panel — preview
        right = tk.Frame(main, bg=BG)
        right.pack(side="left", fill="both", expand=True)

        # Preview area
        self.preview_frame = tk.Frame(right, bg=BG)
        self.preview_frame.pack(fill="both", expand=True, padx=20, pady=20)

        self.preview_label = tk.Label(self.preview_frame, bg=BG,
                                       text="Open a folder to begin",
                                       font=("Helvetica", 14), fg=TEXT3)
        self.preview_label.pack(expand=True)

        # Image info
        self.info_frame = tk.Frame(right, bg=BG2, height=50)
        self.info_frame.pack(fill="x", side="bottom")
        self.info_frame.pack_propagate(False)

        self.info_name = tk.Label(self.info_frame, text="", font=("Helvetica", 11, "bold"),
                                   bg=BG2, fg=TEXT)
        self.info_name.pack(side="left", padx=16, pady=12)

        self.info_score = tk.Label(self.info_frame, text="", font=("Helvetica", 11),
                                    bg=BG2, fg=TEXT2)
        self.info_score.pack(side="left", padx=8, pady=12)

        # Action buttons
        btn_frame = tk.Frame(right, bg=BG3, height=64)
        btn_frame.pack(fill="x", side="bottom")
        btn_frame.pack_propagate(False)

        self.btn_prev = tk.Button(btn_frame, text="◀  Prev",
                                   font=("Helvetica", 11), bg=BG2, fg=TEXT2,
                                   relief="flat", padx=16, pady=8, cursor="hand2",
                                   command=self.prev_image)
        self.btn_prev.pack(side="left", padx=(16, 4), pady=12)

        self.btn_next = tk.Button(btn_frame, text="Next  ▶",
                                   font=("Helvetica", 11), bg=BG2, fg=TEXT2,
                                   relief="flat", padx=16, pady=8, cursor="hand2",
                                   command=self.next_image)
        self.btn_next.pack(side="left", padx=4, pady=12)

        self.btn_delete = tk.Button(btn_frame, text="🗑  Delete File",
                                     font=("Helvetica", 11, "bold"),
                                     bg=RED, fg=TEXT, relief="flat",
                                     padx=20, pady=8, cursor="hand2",
                                     command=self.delete_current)
        self.btn_delete.pack(side="right", padx=(4, 16), pady=12)

        self.btn_delete_folder = tk.Button(btn_frame, text="🗑  Delete Entire Rejected Folder",
                                            font=("Helvetica", 11, "bold"),
                                            bg="#8b0000", fg=TEXT, relief="flat",
                                            padx=20, pady=8, cursor="hand2",
                                            command=self.delete_rejected_folder)
        self.btn_delete_folder.pack(side="right", padx=4, pady=12)

        # Progress bar
        self.progress_frame = tk.Frame(right, bg=BG, height=4)
        self.progress_frame.pack(fill="x", side="bottom")
        self.progress_bar = tk.Frame(self.progress_frame, bg=ACCENT, height=4, width=0)
        self.progress_bar.pack(side="left")

    def _build_stats(self):
        for w in self.stats_frame.winfo_children():
            w.destroy()

        sharp   = sum(1 for i in self.images if i["category"] == "sharp"    and not i["deleted"])
        fixable = sum(1 for i in self.images if i["category"] == "fixable"  and not i["deleted"])
        rejected= sum(1 for i in self.images if i["category"] == "rejected" and not i["deleted"])

        for label, count, color in [
            ("✅ Sharp",    sharp,    GREEN),
            ("🔧 Fixable",  fixable,  YELLOW),
            ("🗑 Rejected", rejected, RED),
        ]:
            f = tk.Frame(self.stats_frame, bg=BG3, pady=6)
            f.pack(fill="x", pady=2)
            tk.Label(f, text=label, font=("Helvetica", 10),
                     bg=BG3, fg=TEXT2).pack(side="left", padx=10)
            tk.Label(f, text=str(count), font=("Helvetica", 10, "bold"),
                     bg=BG3, fg=color).pack(side="right", padx=10)

    # ── OPEN FOLDER ──────────────────────────────────────
    def open_folder(self):
        folder = filedialog.askdirectory(title="Select photos folder")
        if not folder:
            return
        self.folder_path = Path(folder)
        self.images = []
        self._clear_list()
        self.preview_label.configure(text="Scanning...", image="")
        self.preview_label.image = None
        self.scan_thread = threading.Thread(target=self._scan_folder, daemon=True)
        self.scan_thread.start()

    def _scan_folder(self):
        files = sorted([
            f for f in self.folder_path.iterdir()
            if f.is_file() and f.suffix.lower() in SUPPORTED_FORMATS
        ])
        total = len(files)
        if total == 0:
            self.root.after(0, lambda: self.preview_label.configure(
                text="No supported images found."))
            return

        for i, f in enumerate(files):
            score = calculate_focus_score(f)
            category = get_category(score)
            self.images.append({
                "path": f,
                "score": score,
                "category": category,
                "deleted": False
            })
            progress = int(((i + 1) / total) * self.root.winfo_width())
            self.root.after(0, lambda p=progress: self.progress_bar.configure(width=p))
            self.root.after(0, self._rebuild_list)

        self.root.after(0, lambda: self.progress_bar.configure(width=0))
        self.root.after(0, self._rebuild_list)
        if self.images:
            self.root.after(0, lambda: self.show_image(0))

    # ── LIST ─────────────────────────────────────────────
    def _clear_list(self):
        for w in self.list_frame.winfo_children():
            w.destroy()

    def _rebuild_list(self):
        self._clear_list()
        self._build_stats()

        for cat, label, color in [
            ("rejected", "🗑  REJECTED", RED),
            ("fixable",  "🔧  FIXABLE",  YELLOW),
            ("sharp",    "✅  SHARP",    GREEN),
        ]:
            items = [i for i, img in enumerate(self.images)
                     if img["category"] == cat and not img["deleted"]]
            if not items:
                continue

            # Category header
            hdr = tk.Frame(self.list_frame, bg=BG3)
            hdr.pack(fill="x", pady=(8, 2))
            tk.Label(hdr, text=f"{label}  ({len(items)})",
                     font=("Helvetica", 9, "bold"),
                     bg=BG3, fg=color).pack(side="left", padx=12, pady=4)

            # Image rows
            for idx in items:
                img = self.images[idx]
                row = tk.Frame(self.list_frame, bg=BG2, cursor="hand2")
                row.pack(fill="x", pady=1)

                name = img["path"].name
                short = name[:28] + "…" if len(name) > 28 else name
                score_str = f"{img['score']:.0f}"

                tk.Label(row, text=short, font=("Helvetica", 9),
                         bg=BG2, fg=TEXT, anchor="w").pack(side="left", padx=10, pady=5)
                tk.Label(row, text=score_str, font=("Helvetica", 9),
                         bg=BG2, fg=TEXT3).pack(side="right", padx=10, pady=5)

                row.bind("<Button-1>", lambda e, i=idx: self.show_image(i))
                for child in row.winfo_children():
                    child.bind("<Button-1>", lambda e, i=idx: self.show_image(i))

    # ── PREVIEW ──────────────────────────────────────────
    def show_image(self, index):
        if index < 0 or index >= len(self.images):
            return
        self.current_index = index
        img_data = self.images[index]

        # Load and display image
        try:
            pil_img = Image.open(img_data["path"])
            # Fit to preview area
            w = self.preview_frame.winfo_width() or 700
            h = self.preview_frame.winfo_height() or 500
            pil_img.thumbnail((w - 40, h - 40), Image.LANCZOS)
            photo = ImageTk.PhotoImage(pil_img)
            self.preview_label.configure(image=photo, text="")
            self.preview_label.image = photo
        except Exception as e:
            self.preview_label.configure(text=f"Cannot open image: {e}", image="")
            self.preview_label.image = None

        # Info bar
        cat = img_data["category"]
        color = {"sharp": GREEN, "fixable": YELLOW, "rejected": RED}[cat]
        self.info_name.configure(text=img_data["path"].name)
        self.info_score.configure(
            text=f"Score: {img_data['score']:.2f}  |  {cat.upper()}",
            fg=color)

    # ── NAVIGATION ───────────────────────────────────────
    def prev_image(self):
        if self.current_index is None:
            return
        active = [i for i, img in enumerate(self.images) if not img["deleted"]]
        if not active:
            return
        pos = active.index(self.current_index) if self.current_index in active else 0
        if pos > 0:
            self.show_image(active[pos - 1])

    def next_image(self):
        if self.current_index is None:
            return
        active = [i for i, img in enumerate(self.images) if not img["deleted"]]
        if not active:
            return
        pos = active.index(self.current_index) if self.current_index in active else 0
        if pos < len(active) - 1:
            self.show_image(active[pos + 1])

    # ── DELETE ───────────────────────────────────────────
    def delete_current(self):
        if self.current_index is None:
            return
        img = self.images[self.current_index]
        if img["deleted"]:
            return

        confirm = messagebox.askyesno(
            "Delete File",
            f"Permanently delete:\n{img['path'].name}\n\nThis cannot be undone.")
        if not confirm:
            return

        try:
            os.remove(img["path"])
            img["deleted"] = True
            self._rebuild_list()
            self.next_image()
        except Exception as e:
            messagebox.showerror("Error", f"Could not delete file:\n{e}")

    def delete_rejected_folder(self):
        rejected = [img for img in self.images
                    if img["category"] == "rejected" and not img["deleted"]]
        if not rejected:
            messagebox.showinfo("Nothing to delete", "No rejected images remaining.")
            return

        confirm = messagebox.askyesno(
            "Delete All Rejected",
            f"Permanently delete ALL {len(rejected)} rejected images?\n\nThis cannot be undone.")
        if not confirm:
            return

        deleted_count = 0
        for img in rejected:
            try:
                os.remove(img["path"])
                img["deleted"] = True
                deleted_count += 1
            except Exception:
                pass

        self._rebuild_list()
        self.preview_label.configure(text=f"Deleted {deleted_count} rejected images.", image="")
        self.preview_label.image = None
        self.info_name.configure(text="")
        self.info_score.configure(text="")
        messagebox.showinfo("Done", f"✅ Deleted {deleted_count} rejected images.\nSpace freed!")

# ── ENTRY POINT ───────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = FocusCheckApp(root)
    root.mainloop()