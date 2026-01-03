# references/ Folder – Your Athlete Face Database

This folder is where the magic starts.

### How It Works
The `athlete_tagger.py` script compares faces in your images against clear reference photos stored here.  
One high-quality, front-facing photo per athlete = high accuracy.

### Quick Setup
1. Drop a clear photo of each athlete into this folder  
   (any filename is fine, e.g., `bolt.jpg`, `messi_portrait.png`)
2. Open `athlete_tagger.py` and add entries to the `KNOWN_ATHLETES` dictionary:

```python
KNOWN_ATHLETES = {
    "Usain Bolt": "references/bolt.jpg",
    "Lionel Messi": "references/messi_portrait.png",
    "Serena Williams": "references/serena.jpg",
    # Add your athletes here — name exactly as you want it in filenames
}
