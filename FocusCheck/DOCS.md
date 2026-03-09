# 📄 imageStream: The Fact Sheet
### *Understanding Sharpness through Data Analytics*

---

## 📐 The Science of the "Eye"
In photography, we talk about **Acutance** (the sharpness of an edge). In the world of **The Art Medium**, we use the **Laplacian Operator**.

* **The Edge:** This is where light transitions from dark to light.
* **The Laplacian:** This is a second-order derivative. It measures the *rate of change* of those edges. A sharp photo has "spiky" changes; a blurry photo has "flat" changes.

## 📊 The Sharpness Scale (Reference Guide)
While every camera sensor behaves differently, use this scale as a foundational start for your Python classifier:

| Focus Score | Visual Quality | Action / Status |
| :--- | :--- | :--- |
| **0 - 50** | Heavy Blur / Bokeh | Delete / Non-recoverable |
| **50 - 150** | "Soft" Focus | Technical failure or intentional blur |
| **150 - 500** | Acceptable | Good for web/social; soft for print |
| **500 - 1000** | **Sharp** | The Professional "Keeper" Zone |
| **1000+** | High Acutance | Macro, Architecture, or High-Contrast |

---

## 🛠 Troubleshooting the "Walls"
To create a fair distribution of knowledge, we must address the technical "walls" photographers face when using code.

### 1. The Noise Trap (High ISO)
**The Problem:** Digital grain (noise) looks like "sharpness" to the math because it creates tiny sharp dots. A grainy, blurry photo might accidentally get a high score.
**The Flow:** We must apply a **Gaussian Blur** (a light smoothing filter) to the image *before* we run the Laplacian. This removes the "noise" and forces the math to look at the actual subject.

### 2. The Subject Bias
**The Problem:** A sharp photo of a plain white wall will score lower than a blurry photo of a brick wall. 
**The Flow:** The Laplacian requires texture to work. Only compare scores between similar shots (e.g., comparing the 10 photos you took of the same person in a burst).

---

## 💡 The Philosophy
This repository is about **Foundational Clarity**. We do not use expensive cloud GPUs. We use the logic of the lens and the efficiency of Python to empower artists who have been left behind by high-cost tech.

> "I am not here to be perfect but flow perfection."  
> — *The Art Medium*
