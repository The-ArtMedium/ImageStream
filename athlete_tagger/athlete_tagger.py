import os
import argparse
from pathlib import Path
import face_recognition
from PIL import Image
import numpy as np
from concurrent.futures import ProcessPoolExecutor
import multiprocessing
from tqdm import tqdm

# ==================== CONFIGURATION ====================
KNOWN_ATHLETES = {
    "Usain Bolt": "references/usain_bolt.jpg",
    "Serena Williams": "references/serena_williams.jpg",
    "Lionel Messi": "references/lionel_messi.jpg",
    # Add your reference paths here
}

# Threshold: Lower is stricter (0.4 is very strict, 0.6 is loose)
MATCH_THRESHOLD = 0.55 

# Load known faces once globally for worker processes
print("Preparing reference library...")
known_encodings = []
known_names = []

for name, path in KNOWN_ATHLETES.items():
    if os.path.exists(path):
        img = face_recognition.load_image_file(path)
        enc = face_recognition.face_encodings(img)
        if enc:
            known_encodings.append(enc[0])
            known_names.append(name)
# ======================================================

def rename_with_athletes(image_path):
    """Core logic for a single image; optimized for parallel execution."""
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        detected_athletes = set()
        for face_encoding in face_encodings:
            # Use distance for better accuracy than simple compare_faces
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            if len(distances) > 0:
                best_match_index = np.argmin(distances)
                if distances[best_match_index] <= MATCH_THRESHOLD:
                    name = known_names[best_match_index]
                    detected_athletes.add(name.replace(" ", ""))

        if detected_athletes:
            athletes_str = "_".join(sorted(detected_athletes))
            path = Path(image_path)
            new_path = path.parent / f"{path.stem}_{athletes_str}{path.suffix}"
            
            # Collision handling
            counter = 1
            while new_path.exists():
                new_path = path.parent / f"{path.stem}_{athletes_str}_{counter}{path.suffix}"
                counter += 1

            os.rename(image_path, new_path)
            return True
    except Exception:
        return False
    return False

def run_scanner(folder_path, dry_run=False):
    supported = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    files_to_process = []
    
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(supported):
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
