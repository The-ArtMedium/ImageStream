![LocalBeat](https://raw.githubusercontent.com/The-ArtMedium/ImageStream/main/banners/1767458151897.jpg)

# 🏃 ImageStream Athlete Tagger

Automatically detect athletes in your photo archive and rename files for easy searching.

## ✨ Features

- 🎯 Fast parallel processing using all CPU cores
- 📊 Progress bar and detailed statistics
- 💾 Smart caching - only recomputes when needed
- 🎛️ Configurable matching threshold
- 🔍 Dry-run mode to preview changes
- 📝 Clear logging of all operations

## 🚀 Quick Start

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

**Note:** On some systems you may need additional dependencies for `face_recognition`:
- **macOS**: `brew install cmake`
- **Ubuntu/Debian**: `sudo apt-get install cmake`
- **Windows**: Install Visual Studio Build Tools

### 2. Setup Reference Photos

1. Create a `references` folder
2. Add one clear photo of each athlete's face
3. Update `config.yaml` with athlete names and photo paths

Example structure:
```
athlete_tagger/
├── athlete_tagger.py
├── config.yaml
├── requirements.txt
└── references/
    ├── usain_bolt.jpg
    ├── serena_williams.jpg
    └── lionel_messi.jpg
```

### 3. Run the Tool

```bash
python athlete_tagger.py /path/to/photos --dry-run
python athlete_tagger.py /path/to/photos
```

## 📖 Usage Examples

```bash
python athlete_tagger.py /path/to/photos
python athlete_tagger.py /path/to/photos --dry-run
python athlete_tagger.py /path/to/photos --threshold 0.45
python athlete_tagger.py /path/to/photos --workers 4
python athlete_tagger.py /path/to/photos --config my_config.yaml
```

## ⚙️ Configuration

Edit `config.yaml`:

```yaml
match_threshold: 0.55

athletes:
  "Athlete Name": "path/to/reference.jpg"
```

### Threshold Guide
- **0.45-0.50**: Very strict (fewer false positives)
- **0.55**: Balanced (recommended)
- **0.60-0.65**: Lenient (more matches, some false positives)

## 📝 How It Works

1. Loads athlete reference photos from your config
2. Scans your photo folder recursively
3. Detects faces in each image
4. Matches faces against known athletes
5. Renames files: `IMG_1234.jpg` → `IMG_1234_UsainBolt.jpg`

## 🛡️ Safety Features

- **Collision handling**: Won't overwrite existing files
- **Dry-run mode**: Preview changes before applying
- **Detailed logging**: Track all operations in `athlete_tagger.log`
- **Error recovery**: Continues processing if individual files fail

## 🎯 Tips for Best Results

1. Use clear, well-lit reference photos showing the athlete's face straight-on
2. Start with dry-run to verify detection accuracy
3. Adjust threshold if getting too many or too few matches
4. Keep reference photos updated if athlete appearance changes significantly

## 🐛 Troubleshooting

**"No face detected in reference photo"**
- Use a clearer photo with face clearly visible
- Ensure photo shows face straight-on, not at extreme angle

**"Too many false positives"**
- Lower the threshold (try 0.45-0.50)
- Use more distinctive reference photos

**"Missing some matches"**
- Raise the threshold slightly (try 0.60)
- Add multiple reference photos per athlete

## 📊 Output

After processing, you'll see:
- Total images processed
- Images with faces detected
- Images with athlete matches
- Files successfully renamed
- Any errors encountered

## 📄 License

MIT License - Feel free to use and modify!

## 🙏 Credits

Built with [face_recognition](https://github.com/ageitgey/face_recognition) by Adam Geitgey

Part of the ImageStream toolkit by The-ArtMedium
```

**Use the copy icon ☝️ Save as `README.md` and you're done!** 🎉
