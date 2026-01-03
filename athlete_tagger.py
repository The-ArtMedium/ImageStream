import os
import argparse
from pathlib import Path
import face_recognition
from PIL import Image
import numpy as np

# ==================== CONFIGURATION ====================
# Add your reference images here: one clear face photo per athlete
# Format: "Athlete Name": "path/to/reference_face.jpg"
KNOWN_ATHLETES = {
    "Usain Bolt": "references/usain_bolt.jpg",
    "Serena Williams": "references/serena_williams.jpg",
    "Lionel Messi": "references/lionel_messi.jpg",
    "Michael Jordan": "references/michael_jordan.jpg",
    "Cristiano Ronaldo": "references/cristiano_ronaldo.jpg",
    # Add as many as you want — crop tight on face for best results
}

# Load known faces once at startup
print("Loading known athlete faces...")
known_encodings = []
known_names = []

for name, path in KNOWN_ATHLETES.items():
    if not os.path.exists(path):
        print(f"Warning: Reference image not found: {path}")
        continue
    image = face_recognition.load_image_file(path)
    encoding = face_recognition.face_encodings(image)
    if encoding:
        known_encodings.append(encoding[0])
        known_names.append(name)
    else:
        print(f"Warning: No face found in reference: {path}")

print(f"Loaded {len(known_encodings)} athlete face encodings.\n")
# ======================================================

def rename_with_athletes(image_path):
    try:
        image = face_recognition.load_image_file(image_path)
        face_locations = face_recognition.face_locations(image)
        face_encodings = face_recognition.face_encodings(image, face_locations)

        detected_athletes = set()
        for face_encoding in face_encodings:
            matches = face_recognition.compare_faces(known_encodings, face_encoding, tolerance=0.55)
            if True in matches:
                first_match_index = matches.index(True)
                name = known_names[first_match_index]
                # Clean name for filename
                clean_name = name.replace(" ", "").replace("-", "")
                detected_athletes.add(clean_name)

        if detected_athletes:
            athletes_str = "_".join(sorted(detected_athletes))
            path = Path(image_path)
            new_name = f"{path.stem}_{athletes_str}{path.suffix}"
            new_path = path.parent / new_name

            # Avoid overwrite
            counter = 1
            while new_path.exists():
                new_name = f"{path.stem}_{athletes_str}_{counter}{path.suffix}"
                new_path = path.parent / new_name
                counter += 1

            os.rename(image_path, new_path)
            print(f"Renamed: {path.name} → {new_path.name}")
        else:
            print(f"No known athletes found: {Path(image_path).name}")

    except Exception as e:
        print(f"Error processing {image_path}: {e}")

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
