import os
import argparse
import pickle
import hashlib
import logging
from pathlib import Path
from concurrent.futures import ProcessPoolExecutor
import multiprocessing

try:
    import face_recognition
    import numpy as np
    from tqdm import tqdm
    import yaml
except ImportError as e:
    print(f"❌ Missing required library: {e}")
    print("📦 Install with: pip install -r requirements.txt")
    exit(1)

# ==================== CONFIGURATION ====================
CONFIG_FILE = "config.yaml"
CACHE_FILE = "athlete_encodings.cache"
DEFAULT_THRESHOLD = 0.55

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('athlete_tagger.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# ==================== STATISTICS TRACKER ====================
class Stats:
    def __init__(self):
        self.total_processed = 0
        self.faces_detected = 0
        self.matches_found = 0
        self.files_renamed = 0
        self.errors = 0
    
    def print_summary(self):
        print("\n" + "="*50)
        print("📊 PROCESSING SUMMARY")
        print("="*50)
        print(f"Total images processed:     {self.total_processed}")
        print(f"Images with faces detected: {self.faces_detected}")
        print(f"Images with athlete matches: {self.matches_found}")
        print(f"Files successfully renamed: {self.files_renamed}")
        print(f"Errors encountered:         {self.errors}")
        print("="*50)

stats = Stats()

# ==================== CONFIGURATION LOADER ====================
def load_config(config_path=CONFIG_FILE):
    """Load athlete configuration from YAML file."""
    if not os.path.exists(config_path):
        logger.error(f"❌ Config file not found: {config_path}")
        logger.info("📝 Creating template config.yaml...")
        create_template_config(config_path)
        logger.info("✅ Template created! Edit config.yaml and add your athlete photos.")
        exit(1)
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    athletes = config.get('athletes', {})
    threshold = config.get('match_threshold', DEFAULT_THRESHOLD)
    
    if not athletes:
        logger.error("❌ No athletes defined in config.yaml!")
        exit(1)
    
    return athletes, threshold

def create_template_config(config_path):
    """Create a template configuration file."""
    template = """# ImageStream Athlete Tagger Configuration
# Add your athletes below with paths to their reference photos

# Match threshold: Lower = stricter (0.4-0.6 recommended)
# 0.4 = very strict, 0.6 = more lenient
match_threshold: 0.55

# Athletes: Add name and path to reference photo
athletes:
  "Usain Bolt": "references/usain_bolt.jpg"
  "Serena Williams": "references/serena_williams.jpg"
  "Lionel Messi": "references/lionel_messi.jpg"
  # Add more athletes below:
  # "Athlete Name": "path/to/photo.jpg"
"""
    with open(config_path, 'w') as f:
        f.write(template)

# ==================== ENCODING CACHE ====================
def load_or_compute_encodings(athlete_dict, threshold):
    """Load cached encodings or compute new ones if config changed."""
    config_hash = hashlib.md5(
        str(sorted(athlete_dict.items())).encode()
    ).hexdigest()
    
    # Try loading from cache
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, 'rb') as f:
                cache_data = pickle.load(f)
                if cache_data.get('hash') == config_hash:
                    logger.info("⚡ Loaded athlete encodings from cache")
                    return cache_data['encodings'], cache_data['names']
        except Exception as e:
            logger.warning(f"Cache load failed: {e}")
    
    # Compute new encodings
    logger.info("🔍 Computing face encodings for reference library...")
    encodings, names = [], []
    
    for name, path in athlete_dict.items():
        if not os.path.exists(path):
            logger.warning(f"⚠️  Reference image not found: {path}")
            continue
        
        try:
            image = face_recognition.load_image_file(path)
            face_encodings = face_recognition.face_encodings(image)
            
            if face_encodings:
                encodings.append(face_encodings[0])
                names.append(name)
                logger.info(f"✓ Loaded: {name}")
            else:
                logger.warning(f"⚠️  No face detected in: {path}")
        except Exception as e:
            logger.error(f"❌ Error loading {path}: {e}")
    
    if not encodings:
        logger.error("❌ No valid reference faces found!")
        exit(1)
    
    # Save to cache
    cache_data = {
        'hash': config_hash,
        'encodings': encodings,
        'names': names
    }
    with open(CACHE_FILE, 'wb') as f:
        pickle.dump(cache_data, f)
    
    logger.info(f"✅ Encoded {len(encodings)} athlete reference faces")
    return encodings, names

# ==================== IMAGE PROCESSING ====================
def process_image(args):
    """Process a single image (worker function)."""
    image_path, known_encodings, known_names, threshold = args
    
    try:
        # Load image
        image = face_recognition.load_image_file(image_path)
        
        # Detect faces (HOG is faster for CPU)
        face_locations = face_recognition.face_locations(image, model="hog")
        
        if not face_locations:
            return None, False
        
        stats.faces_detected += 1
        face_encodings = face_recognition.face_encodings(image, face_locations)
        
        # Match faces to known athletes
        detected_athletes = set()
        for face_encoding in face_encodings:
            distances = face_recognition.face_distance(known_encodings, face_encoding)
            
            if len(distances) > 0:
                min_distance = min(distances)
                
                if min_distance <= threshold:
                    best_match_idx = np.argmin(distances)
                    athlete_name = known_names[best_match_idx]
                    clean_name = athlete_name.replace(" ", "").replace("-", "")
                    detected_athletes.add(clean_name)
                    logger.debug(f"  Match: {athlete_name} (distance: {min_distance:.3f})")
        
        if not detected_athletes:
            return None, True
        
        # Generate new filename
        stats.matches_found += 1
        athletes_str = "_".join(sorted(detected_athletes))
        path = Path(image_path)
        new_name = f"{path.stem}_{athletes_str}{path.suffix}"
        new_path = path.parent / new_name
        
        # Handle filename collisions
        counter = 1
        while new_path.exists():
            new_name = f"{path.stem}_{athletes_str}_{counter}{path.suffix}"
            new_path = path.parent / new_name
            counter += 1
        
        return (image_path, new_path), True
        
    except Exception as e:
        logger.error(f"Error processing {image_path}: {e}")
        stats.errors += 1
        return None, False

# ==================== FOLDER SCANNER ====================
def scan_folder(folder_path, known_encodings, known_names, threshold, dry_run=False, max_workers=None):
    """Scan folder and process all images."""
    supported_formats = ('.jpg', '.jpeg', '.png', '.JPG', '.JPEG', '.PNG')
    
    # Collect all image paths
    image_paths = []
    for root, _, files in os.walk(folder_path):
        for file in files:
            if file.lower().endswith(supported_formats):
                image_paths.append(os.path.join(root, file))
    
    if not image_paths:
        logger.warning("⚠️  No images found in target folder")
        return
    
    logger.info(f"📸 Found {len(image_paths)} images to process")
    
    if dry_run:
        logger.info("🔍 DRY RUN MODE - No files will be renamed")
        sample_paths = image_paths[:min(10, len(image_paths))]
        for path in sample_paths:
            logger.info(f"  Would process: {path}")
        logger.info(f"... and {len(image_paths) - len(sample_paths)} more")
        return
    
    # Determine worker count
    if max_workers is None:
        max_workers = multiprocessing.cpu_count()
    
    logger.info(f"🚀 Processing with {max_workers} CPU cores...")
    
    # Prepare arguments for workers
    worker_args = [
        (path, known_encodings, known_names, threshold) 
        for path in image_paths
    ]
    
    # Process in parallel with progress bar
    with ProcessPoolExecutor(max_workers=max_workers) as executor:
        results = list(tqdm(
            executor.map(process_image, worker_args),
            total=len(image_paths),
            desc="Scanning photos",
            unit="img"
        ))
    
    # Apply renames
    for result, has_faces in results:
        stats.total_processed += 1
        if result:
            old_path, new_path = result
            try:
                os.rename(old_path, new_path)
                stats.files_renamed += 1
                logger.info(f"✓ Renamed: {Path(old_path).name} → {Path(new_path).name}")
            except Exception as e:
                logger.error(f"❌ Failed to rename {old_path}: {e}")
                stats.errors += 1

# ==================== MAIN ====================
def main():
    parser = argparse.ArgumentParser(
        description="ImageStream Athlete Tagger - Organize photos by detected athletes",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python athlete_tagger.py /path/to/photos
  python athlete_tagger.py /path/to/photos --dry-run
  python athlete_tagger.py /path/to/photos --threshold 0.50
  python athlete_tagger.py /path/to/photos --workers 4
        """
    )
    
    parser.add_argument('folder', help='Path to folder containing photos to process')
    parser.add_argument('--dry-run', action='store_true', help='Preview without making changes')
    parser.add_argument('--threshold', type=float, help=f'Face matching threshold (default from config)')
    parser.add_argument('--workers', type=int, help='Number of CPU cores to use (default: all)')
    parser.add_argument('--config', default=CONFIG_FILE, help=f'Path to config file (default: {CONFIG_FILE})')
    
    args = parser.parse_args()
    
    # Validate folder
    if not os.path.isdir(args.folder):
        logger.error(f"❌ Folder not found: {args.folder}")
        exit(1)
    
    print("="*50)
    print("🏃 ImageStream Athlete Tagger")
    print("="*50)
    
    # Load configuration
    athletes, threshold = load_config(args.config)
    
    # Override threshold if specified
    if args.threshold:
        threshold = args.threshold
        logger.info(f"Using custom threshold: {threshold}")
    
    # Load/compute encodings
    known_encodings, known_names = load_or_compute_encodings(athletes, threshold)
    
    # Process folder
    scan_folder(
        args.folder,
        known_encodings,
        known_names,
        threshold,
        dry_run=args.dry_run,
        max_workers=args.workers
    )
    
    # Print summary
    if not args.dry_run:
        stats.print_summary()
    
    print("\n✅ Processing complete!")

if __name__ == "__main__":
    main()
Copy that entire block ☝️ and save it as athlete_tagger.py
When you're done, say "next" and I'll give you the next file!