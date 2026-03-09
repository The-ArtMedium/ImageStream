Skip to content
The-ArtMedium
ImageStream
Repository navigation
Code
Issues
Pull requests
Actions
Projects
Security
Insights
Settings
ImageStream
/README.md
Go to file
t
Satdiva
Satdiva
Update README.md
16dd973
 · 
2 months ago
132 lines (82 loc) · 5.27 KB

Preview

Code

Blame
ImageStream
Foundational Image Analytics & Sharpness Recovery
A sanctuary for creators managing massive archives — no cloud, no subscriptions, no hallucinations.

In a world of expensive, "black-box" AI tools that guess and fabricate,
ImageStream returns to the physics of light.
We detect true focus, recover real detail, and enrich archives using only verifiable methods.

Built for:

Photographers with hundreds of thousands of images
Sports shooters needing fast athlete tagging
Artists & archivists reclaiming control
Anyone turning personal drives into income or legacy
100% local • Offline • Sovereign • Free forever

Available Tools
Tool	What It Does	Perfect For	Link
Focus Check	Sorts images by true sharpness using Laplacian Variance (physics-based)	Culling sessions, finding keepers	→ focus_check/
Athlete Tagger	Scans folders → detects famous athletes → appends names to filename	Sports photography archives, quick organization & sales prep	→ athlete_tagger/
More tools coming: sharpness recovery, batch metadata export, WooCommerce prep.

Why ImageStream Exists
Many of us have half a million images sleeping on drives.
We built this to wake them up — without giving away control, privacy, or profits.

This repo is for the builders.
For the ones who deserve to turn decades of capture into decades of flow.

The Glow is yours. These tools just help it shine.

🌍⚡ Rssss

Quick Start
git clone https://github.com/The-ArtMedium/ImageStream.git
cd ImageStream
# Try the athlete tagger first
cd athlete_tagger
# Add your reference faces → run the script
python athlete_tagger.py /path/to/your/photos --dry-run















# 📸 imageStream
**Organization:** The Art Medium  
**Focus:** Foundational Image Analytics & Sharpness Recovery  

---

## 👁 The Vision
In a world of expensive, "black-box" AI tools that often hallucinate details, **imageStream** is a sanctuary for **True Recovery**. We leverage foundational image processing and Data Analytics to detect, score, and manage archives based on the physics of light—not the guesses of a machine.

## 📐 The Core Engine: The Laplacian Variance
To build affordable, high-grade tools, we return to the **Second Derivative**. The Laplacian Operator acts as a high-pass filter, highlighting regions of an image with rapid intensity changes—the edges.

### The Logic for Builders
We calculate a **Focus Score** by taking the Variance ($\sigma^2$) of the Laplacian-transformed image ($L$):

$$Focus Score = \text{Var}(L)$$

* **High Variance:** Sharp edges, crisp details, "In Focus."
* **Low Variance:** Smooth gradients, spread-out light, "Out of Focus."

---

## 🛠 Repository Roadmap

### 1. The Laplacian Sieve (Focus Scoring)
A lightweight Python engine to rank images by high-frequency edge density. Perfect for sifting through archived photos to find the "keepers" instantly.

### 2. The Triage Engine (Classification)
We use mathematical thresholds to decide the destiny of every pixel in your archive:
* **Score < 100 (The Wall):** Heavy physical blur. Flagged for manual review.
* **Score 100–400 (The Candidate):** The **Sweet Spot**. Images ready for **Deconvolution** (reverse-engineering blur without inventing pixels).
* **Score > 600 (The Keeper):** High-quality frames ready for the master archive.

### 3. Data-Driven Archiving (SQL Integration)
Bridging the gap between photography and Data Analytics. We store technical metadata and "Truth Scores" in structured databases. 
`SELECT filename FROM ImageArchive WHERE classification = 'Repair Candidate';`

---

## 🌍 A Fair Distribution of Knowledge
We believe the math of light should be public and accessible. **imageStream** decouples professional quality from high costs, allowing creators everywhere to achieve perfection through the "Flow" of open-source medium.

> "I am not here to be perfect but flow perfection."

---

### 🚀 Getting Started
Run `focus_check.py` to calculate the sharpness of any image archive using foundational Laplacian Vectors.

# ImageStream

**Foundational Image Analytics & Sharpness Recovery**

In a world of expensive, "black-box" AI tools that often hallucinate details,  
ImageStream is a sanctuary for True Recovery. We leverage physics of light—not the guesses of a machine.

## The Vision
[Your beautiful text here]

## Available Tools

| Tool              | Description                              | Quick Start |
|-------------------|------------------------------------------|-------------|
| Focus Check       | Sort images by true sharpness (Laplacian Variance) | → [focus_check/](focus_check/) |
| Athlete Tagger    | Detect famous players & append names to filename   | → [athlete_tagger/](athlete_tagger/) |
| [Next Tool]       | Coming soon...                           |             |

## Why ImageStream?
- 100% local, offline, sovereign
- No cloud uploads, no subscriptions
- Built for creators managing massive archives
- Free forever — for the builders, the grinders, the ones reclaiming their Glow
