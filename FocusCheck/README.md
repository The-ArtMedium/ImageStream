![FocusCheck](https://raw.githubusercontent.com/The-ArtMedium/ImageStream/main/banners/file_00000000db6471fd80cf4807d128341a.png)

# FocusCheck

**Scan. Score. Select. Recover. Keep the sharp. Drop the rest.**

FocusCheck is a free, offline photo culling and sharpness recovery tool built for photographers who shoot volume — sports, equestrian, events. It scores every image, auto-copies the sharp ones, then opens a contact sheet of fixable and rejected images so you decide what is worth your storage — before anything is copied.

Part of the [ImageStream Local Suite](https://the-artmedium.github.io/ImageStream/).

---

## How It Works

FocusCheck uses Laplacian variance — a proven computer vision technique — to measure the sharpness of every image in your folder. It then copies each image into a sorted output folder.

| Folder | What it means |
|--------|--------------|
| ✅ `sharp/` | In focus. Keepers. Ready to edit. |
| 🔧 `fixable/` | Soft but worth recovering. |
| 🗑️ `rejected/` | Too soft to rescue. Delete in one click. |

Your originals are **never touched**. Everything is copied. You decide what to remove.

---

## Features

### Contact Sheet — Select Before You Copy
Sharp images copy automatically. Fixable and rejected images go to a **contact sheet first** — a tap-to-select grid where you decide what is worth keeping before anything touches your storage.

- 6-column thumbnail grid — fixable section first, rejected below
- Every image pre-selected by default
- Click or tap to deselect — bad composition, wrong moment, not worth recovering
- **Select All / Deselect All** per section
- **Copy Selected** shows the count before you commit
- Non-selected images are never copied — storage saved instantly

### Scoring & Sorting
- Laplacian variance scoring — fast, accurate, proven
- **Auto-calibrated thresholds** — thresholds are set relative to your actual shoot, not a fixed global number. A dark arena shoot and a bright outdoor shoot are judged on their own terms
- Images copied into `sharp/` `fixable/` `rejected/` automatically on scan
- Visual list with score displayed per image

### EXIF Blur Detection
- Reads shutter speed from EXIF on every image
- **Distinguishes motion blur from focus error** — a critical difference for recovery
  - Shot at 1/250s or slower → flagged as **Motion Blur** — directional sharpening strategy
  - Shot faster → flagged as **Focus Error** — radial unsharp mask strategy
- Shutter speed and blur type shown in the info bar for every image
- List shows blur type marker: `〜` motion · `⊙` focus

### Recovery Panel
- Recovery panel pre-loaded for every fixable and rejected image
- **Strength slider auto-set from the score deficit** — the further below sharp threshold, the higher the starting point
- Three recovery tiers (Gentle / Medium / Strong) driven by the Laplacian score
- **Preview** — see the recovered result before committing
- **Split Compare** — left half original, right half recovered, white divider, judge instantly
- **Apply & Save to Sharp** — recovered file saved into `sharp/` folder, auto-advances to next
- **Batch Recovery** — apply to all fixable images in one click, each using its own calibrated parameters, runs in background

### Workflow
- **Open Results Folder** button — opens `FocusCheck_Results/` directly in your file manager
- Delete individual files or wipe the entire rejected folder in one click
- Recovered images marked with ✓ in the list

### Languages
7 languages built in — switch from the topbar, no restart needed. Arabic switches the full interface to right-to-left automatically.

🇺🇸 English · 🇪🇸 Español · 🇫🇷 Français · 🇵🇹 Português · 🇸🇦 العربية · 🇨🇳 中文 · 🇮🇳 हिन्दी
- Auto-jumps to first fixable image after scan

### Formats
- JPG · JPEG · PNG · TIFF · BMP · WebP
- RAW: CR2 · NEF · ARW · DNG · RAF · ORF · RW2 · CR3 *(requires rawpy)*

---

## Install

### Windows
1. Download `FocusCheck-focuscheck-v0.1.0-Windows.zip`
2. Unzip
3. Double-click `FocusCheck.exe`

### Mac
1. Download `FocusCheck-focuscheck-v0.1.0-Mac.zip`
2. Unzip
3. Open `FocusCheck.app`
   - If blocked: System Preferences → Security → Open Anyway

### Linux
1. Download `FocusCheck-focuscheck-v0.1.0-Linux.zip`
2. Unzip
3. Run in terminal:
```bash
chmod +x FocusCheck
./FocusCheck
```

---

## Run from Source

```bash
# Core dependencies (required)
pip install opencv-python Pillow

# RAW support (optional — enables CR2, NEF, ARW, DNG, etc.)
pip install rawpy

# Run
python focus_check.py
```

**Requirements:** Python 3.8+

---

## Output Structure

```
YourShootFolder/
└── FocusCheck_Results/
    ├── sharp/
    │   ├── IMG_001.jpg
    │   └── IMG_005_recovered.jpg    ← recovered fixable
    ├── fixable/
    │   └── IMG_003.jpg
    └── rejected/
        └── IMG_002.jpg
```

---

## Understanding the Recovery

FocusCheck does not just apply a generic sharpening filter. Every recovery is guided by three pieces of data:

**1. The Laplacian score deficit**
How far below the sharp threshold is this image? The larger the deficit, the stronger the recovery pass. The strength slider is pre-set from this deficit automatically.

**2. The blur type (from EXIF)**
Motion blur and focus error respond to different techniques. Motion blur benefits from directional edge enhancement. Focus error responds better to radial unsharp mask. FocusCheck reads your shutter speed and picks the right strategy.

**3. Your manual strength override**
The slider lets you push harder or softer. Use Split Compare to judge whether the recovery is helping or adding noise before you commit.

---

## Part of the ImageStream Local Suite

| Tool | What it does |
|------|-------------|
| [LocalBeat](../LocalBeat/) | Audio preparation |
| [LocalShot](../LocalShot/) | Offline image editor — tone, color, crop, dehaze |
| [LocalClip](../LocalClip/) | Video clipping |
| [LocalEdit](../LocalEdit/) | Video editor |
| [LocalRAW](../LocalRAW/) | RAW file processor |
| **FocusCheck** | Sharpness scoring, culling and recovery |
| [BokehProStudio](../BokehProStudio/) | Depth-of-field effects |

All tools are free forever. All run offline. No subscriptions, no accounts, no tracking.

---

## License

GPL v3 — Free to use, modify and distribute.
Cannot be resold or bundled into commercial products.
See [LICENSE](../LICENSE) for full terms.

---

Built by [The Art Medium](https://github.com/The-ArtMedium) · theartsmedium@gmail.com
