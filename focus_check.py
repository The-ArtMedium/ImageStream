
import cv2
import os

def calculate_focus_score(image_path):
    # 1. Load the image
    image = cv2.imread(image_path)
    if image is None: return 0
    
    # 2. Convert to Grayscale (Color is noise for focus)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    
    # 3. Apply the Laplacian Operator (The Second Derivative)
    # This finds the edges/vectors in the image
    laplacian_matrix = cv2.Laplacian(gray, cv2.CV_64F)
    
    # 4. Calculate Variance
    # High variance = sharp edges (In Focus)
    # Low variance = spread out light (Out of Focus)
    score = laplacian_matrix.var()
    return score

# Path to your archive folder
folder_path = "path/to/your/photos"
results = {}

for filename in os.listdir(folder_path):
    if filename.endswith((".jpg", ".png", ".jpeg")):
        path = os.path.join(folder_path, filename)
        score = calculate_focus_score(path)
        results[filename] = score
        print(f"{filename}: Focus Score = {score:.2f}")

# Find the winner
best_photo = max(results, key=results.get)
print(f"\n--- SHARPEST IMAGE: {best_photo} ---")
