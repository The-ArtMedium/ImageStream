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
A lightweight Python engine to rank images by high-frequency edge density. Perfect for sifting through 10,000+ archived photos to find the "keepers" instantly.

### 2. Physical Recovery (Deconvolution)
While GenAI "invents" pixels, we focus on **Richardson-Lucy Deconvolution**. We use existing light data to reverse-engineer blur, respecting the original capture.

### 3. Data-Driven Archiving (SQL Integration)
Bridging the gap between photography and Data Analytics. We store technical metadata and "Truth Scores" in structured databases for professional-grade asset management.

---

## 🌍 A Fair Distribution of Knowledge
We believe the math of light should be public and accessible. **imageStream** decouples professional quality from high costs, allowing creators everywhere to achieve perfection through the "Flow" of open-source medium.

> "I am not here to be perfect but flow perfection."

---

### 🚀 Getting Started
Run `focus_check.py` to calculate the sharpness of any image archive using foundational Laplacian Vectors.


---

### 📢 imageStream Part 2: The Triage Engine

"The eye captures the soul, but the data organizes the archive."

Now that **imageStream** can calculate a **Focus Score** using Laplacian Variance, the next step is the **Triage Engine**. We aren't just looking at a score; we are using mathematical thresholds to decide the destiny of every pixel in your archive:

* **Score < 100 (The Wall):** Heavy physical blur. These are flagged for manual review or high-level recovery.
* **Score 100–400 (The Candidate):** This is the **Sweet Spot**. The image has enough data to be restored using **Deconvolution** (mathematically reversing the blur) without inventing fake pixels.
* **Score > 600 (The Keeper):** In-focus. These are high-quality frames ready for the master archive.

#### 📊 The Data Crusade
Using the **SQL Schema** I'm building, builders can now run commands like:
`SELECT filename FROM ImageArchive WHERE classification = 'Repair Candidate';`


