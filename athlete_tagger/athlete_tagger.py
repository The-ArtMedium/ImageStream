import os
import argparse
import pickle
import hashlib
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

# Third-party libraries (Install via: pip install face_recognition numpy tqdm)
import face_recognition
import numpy as np
from tqdm import tqdm

# ==================== CONFIGURATION ====================
# Add your reference images here: "Athlete Name": "path/to/reference_face.jpg"
KNOWN_ATHLETES = {
    "Usain Bolt": "references/usain_bolt.jpg",
    "Serena Williams": "references/serena_williams.jpg",
    "Lionel Messi": "references/lionel_messi.jpg",
    "Michael Jordan": "references/michael_jordan.jpg",
    "Cristiano Ronaldo": "references/cristiano_ronaldo.jpg",
}

CACHE_FILE = "athlete_encodings.cache"
MATCH_THRESHOLD = 0.55  # Lower is stricter accuracy
# ======================================================

def get_encodings_with_cache(athlete_dict):
    """Loads encodings from cache or computes them if files changed."""
    # Create a unique key based on the current athlete list
    config_hash = hashlib.md5(str(sorted(athlete_dict.items())).encode()).hexdigest()
    
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                data = pickle.load(f)
                if data.get('key') == config_hash:
                    print("⚡ Loaded athlete encodings from cache.")
                    return data['encodings'], data['names']
        except:
            pass

    print("🔍 Computing new face encodings for reference library...")
    encodings, names = [], []
    for name, path in athlete_dict.items():
        if os.path.exists(path):
            img = face_recognition.load_image_file(path)
            enc = face_recognition.face_encodings(img)
            if enc:
                encodings.append(enc[0])
                names.append(name)
            else:
                print(f"⚠️ No face found in: {path}")
    
    # Save to cache
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump({'key': config_hash, 'encodings': encodings, 'names': names}, f)
    
    return encodings, names

# Load global variables for worker processes
known_encodings, known_names = get_encodings_with_cache(KNOWN_ATHLETES)

def rename_with_athletes(image_path):
    """Processes a single image: detects, matches, and renames."""
    try:
        image = face_recognition.load_image_file(image_path)
        # Fast detection (hog) is better for CPUs; 'cnn' is for GPUs
        face_locations = face_recognition.face_locations(image, model="hog")
        face_encodings = face_recognition.face_encodings(image, face_locations)

        detected_athletes = set()
        for face_encoding in face_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            if len(distances) > 0:
                best_match_idx = np.argmin(distances)
                if distances[best_match_idx] <= MATCH_THRESHOLD:
                    clean_name = known_names[best_match_idx].replace(" ", "").replace("-", "")
                    detected_athletes.add(clean_name)

        if detected_athletes:
            athletes_str = "_".join(sorted(detected_athletes))
            path = Path(image_path)
            new_name = f"{path.stem}_{athletes_str}{path.suffix}"
            new_path = path.parent / new_name

            # Collision handling (prevents overwriting)
            counter = 1
            while new_path.exists():
                new_name = f"{path.stem}_{athletes_str}_{counter}{path.suffix}"
                new_path = path.parent / new_name
                counter += 1

            os.rename(image_path, new_path)
            return True
    except Exception:
        return False
    return False

def process_archive(folder_path, dry_run=False):
    supported = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    image_paths = [
        os.path.join(root, f) 
        for root, _, files in os.walk(folder_path) 
        for f in files if f.lower().endswith(supported)
    ]

    if not image_paths:
        print("No images found in the target folder.")
        return

    if dry_run:
        print(f"[DRY RUN] Would process {len(image_paths)} images.")
        return

    # Use all CPU cores for parallel scanning
    num_workers = multiprocessing.cpu_count()
    print(f"🚀 Scanning {len(image_paths)} images using {num_workers} cores...")

    with ProcessPoolExecutor(max_workers=num_workers) as executor:
        # tqdm provides the progress bar
        list(tqdm(executor.map(rename_with_athletes, image_paths), total=len(image_paths), desc="Processing"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ImageStream Athlete Archival Scanner")
    parser.add_argument("folder", help="Path to the photo archive folder")
    parser.add_argument("--dry-run", action="store_true", help="Scan without renaming")
    args = parser.parse_args()

    process_archive(args.folder, dry_run=args.dry_run)
    print("\n✅ Task Complete. Your archive is now searchable by athlete name.")
                files_to_process.append(os.path.join(root, file))

    if dry_run:
        print(f"[DRY RUN] Found {len(files_to_process)} images to analyze.")
        return

    # Using all available CPU cores for massive speed boost
    cpus = multiprocessing.cpu_count()
    print(f"Starting scan using {cpus} CPU cores...")
    
    with ProcessPoolExecutor(max_workers=cpus) as executor:
        # tqdm creates the visual progress bar photographers will love
        list(tqdm(executor.map(rename_with_athletes, files_to_process), 
                  total=len(files_to_process), 
                  desc="Scanning Archive"))

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ImageStream Pro: Athlete Tagger")
    parser.add_argument("folder", help="Target folder")
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()

    run_scanner(args.folder, dry_run=args.dry_run)
    print("\nScan Complete.")
def process_folder(folder_path, dry_run=False):
    supported = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(supported):
                image_path = os.path.join(root, file)
                if dry_run:
                    print(f"[DRY RUN] Would process: {image_path}")
                else:
                    rename_with_athletes(image_path)

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="ImageStream Athlete Tagger: Append detected athlete names to filenames")
    parser.add_argument("folder", help="Path to folder to scan recursively")
    parser.add_argument("--dry-run", action="store_true", help="Test without renaming files")
    args = parser.parse_args()

    print(f"Scanning folder: {args.folder}")
    if args.dry_run:
        print("DRY RUN MODE — no files will be renamed\n")
    process_folder(args.folder, dry_run=args.dry_run)
    print("\nDone.")
