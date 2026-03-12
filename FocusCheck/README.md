![FocusCheck](https://raw.githubusercontent.com/The-ArtMedium/ImageStream/main/banners/file_00000000079871fd8d89be264c45c681.png)

# FocusCheck

**Scan a folder. Score every shot. Keep the sharp. Drop the rest.**

FocusCheck is a free, offline photo culling tool built for photographers who shoot volume — sports, equestrian, events. It scans a folder of images, scores every one for sharpness, and sorts them automatically into three groups so you spend minutes culling instead of hours.

Part of the [ImageStream Local Suite](https://the-artmedium.github.io/ImageStream/).

---

## How It Works

FocusCheck uses Laplacian variance — a proven computer vision technique — to measure the sharpness of every image in a folder. It then copies each image into a sorted output folder.

| Folder | What it means |
|--------|--------------|
| ✅ `sharp/` | In focus. Keepers. Ready to use. |
| 🔧 `fixable/` | Soft but salvageable. Worth sharpening. |
| 🗑️ `rejected/` | Too soft to rescue. Review before deleting. |

Your originals are **never touched**. Everything is copied. You decide what to remove.

---

## Features

- Scores every image using Laplacian variance focus detection
- Visual GUI — see thumbnails of each category before you delete anything
- Summary report after each scan — count per category, sharpest image, softest image
- Non-destructive — originals never modified or deleted
- Works on JPG, JPEG, PNG, TIFF, BMP, WebP
- Runs fully offline — no internet, no account, no cloud
- Works on old hardware — built for field use

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

If you prefer to run the Python script directly:

```bash
# Install dependencies
pip install opencv-python Pillow

# Run
python focus_check.py
```

**Requirements:** Python 3.8+, opencv-python, Pillow

---

## Sharpness Thresholds

FocusCheck uses two thresholds based on Laplacian variance scores:

| Score | Category |
|-------|----------|
| 150 and above | Sharp ✅ |
| 50 – 149 | Fixable 🔧 |
| Below 50 | Rejected 🗑️ |

These values work well for most camera systems. If you shoot with a very soft lens or want stricter culling, you can adjust `SHARP_THRESHOLD` and `FIXABLE_THRESHOLD` at the top of `focus_check.py`.

---

## Output Structure

After each scan, FocusCheck creates a `FocusCheck_Results/` folder next to your source images:

```
FocusCheck_Results/
├── sharp/
│   ├── IMG_001.jpg
│   └── IMG_005.jpg
├── fixable/
│   ├── IMG_003.jpg
│   └── IMG_009.jpg
└── rejected/
    ├── IMG_002.jpg
    └── IMG_007.jpg
```

---

## Part of the ImageStream Local Suite

| Tool | What it does |
|------|-------------|
| [LocalBeat](../LocalBeat/) | Audio preparation |
| [LocalShot](../LocalShot/) | Screenshot capture |
| [LocalClip](../LocalClip/) | Video clipping |
| [LocalEdit](../LocalEdit/) | Video editor |
| [LocalRAW](../LocalRAW/) | RAW file processor |
| **FocusCheck** | Sharpness scoring and culling |
| [BokehProStudio](../BokehProStudio/) | Depth-of-field effects |

All tools are free forever. All run offline. No subscriptions, no accounts, no tracking.

---

## License

MIT License with Commons Clause.
Free to use, modify and distribute personally.
May not be bundled into commercial products or used as a promotional feature without written permission from The Art Medium.

---

Built by [The Art Medium](https://github.com/The-ArtMedium) · theartsmedium@gmail.com
