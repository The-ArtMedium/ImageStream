"""
localsuite_db.py — Shared database and thumbnail logic for the
ImageStream Local Suite.

Every tool that touches a photo can write what it learned here, and
every tool can read the same thumbnails instead of each generating
its own. No server, no setup — just one small SQLite file sitting
next to the LocalSuite/Saved/ folder the tools already share.

To use this in a tool: copy this file into that tool's folder and
import it. No extra installation beyond Pillow, which most of the
suite already depends on.
"""
import sqlite3
import hashlib
from pathlib import Path
from datetime import datetime

try:
    from PIL import Image
except ImportError:
    Image = None

SUITE_DIR = Path.home() / "Documents" / "LocalSuite"
DB_PATH = SUITE_DIR / "index.db"
THUMB_DIR = SUITE_DIR / "thumbnails"
THUMB_SIZE = 512


def _ensure_dirs():
    SUITE_DIR.mkdir(parents=True, exist_ok=True)
    THUMB_DIR.mkdir(parents=True, exist_ok=True)


def get_connection():
    """Open the shared database, creating the table on first use."""
    _ensure_dirs()
    conn = sqlite3.connect(str(DB_PATH))
    conn.execute("""
        CREATE TABLE IF NOT EXISTS photos (
            id TEXT PRIMARY KEY,
            filepath TEXT UNIQUE NOT NULL,
            filename TEXT,
            date_added TEXT,
            format TEXT,
            sharpness_verdict TEXT,
            sharpness_score REAL,
            athlete_tag TEXT,
            edited INTEGER DEFAULT 0,
            thumbnail_path TEXT
        )
    """)
    conn.commit()
    return conn


def _make_id(filepath):
    """Stable ID derived from the file's absolute path."""
    abs_path = str(Path(filepath).resolve())
    return hashlib.sha1(abs_path.encode("utf-8")).hexdigest()[:16]


def get_or_create_thumbnail(filepath):
    """
    Return the path to this photo's thumbnail, creating it if it
    doesn't exist yet. The first tool to see a photo makes the
    thumbnail; every tool after that just reuses the same file.
    Returns None if Pillow isn't available or the image can't be read.
    """
    _ensure_dirs()
    photo_id = _make_id(filepath)
    thumb_path = THUMB_DIR / f"{photo_id}.jpg"

    if thumb_path.exists():
        return str(thumb_path)

    if Image is None:
        return None

    try:
        img = Image.open(filepath)
        img = img.convert("RGB")
        img.thumbnail((THUMB_SIZE, THUMB_SIZE), Image.LANCZOS)
        img.save(str(thumb_path), "JPEG", quality=85)
        return str(thumb_path)
    except Exception:
        return None


def upsert_photo(filepath, **fields):
    """
    Insert or update a photo's record. Pass only the fields your tool
    actually knows about — fields written by other tools are left
    untouched.

    Example:
        upsert_photo(path, sharpness_verdict="sharp", sharpness_score=142.7)
    """
    conn = get_connection()
    photo_id = _make_id(filepath)
    thumb = get_or_create_thumbnail(filepath)

    existing = conn.execute(
        "SELECT id FROM photos WHERE id=?", (photo_id,)
    ).fetchone()

    if existing:
        if fields or thumb:
            updates = dict(fields)
            if thumb:
                updates["thumbnail_path"] = thumb
            set_clause = ", ".join(f"{k}=?" for k in updates)
            conn.execute(
                f"UPDATE photos SET {set_clause} WHERE id=?",
                (*updates.values(), photo_id),
            )
    else:
        base = {
            "id": photo_id,
            "filepath": str(Path(filepath).resolve()),
            "filename": Path(filepath).name,
            "date_added": datetime.now().isoformat(),
            "thumbnail_path": thumb,
        }
        base.update(fields)
        cols = ", ".join(base.keys())
        placeholders = ", ".join("?" for _ in base)
        conn.execute(
            f"INSERT INTO photos ({cols}) VALUES ({placeholders})",
            tuple(base.values()),
        )

    conn.commit()
    conn.close()
    return photo_id
