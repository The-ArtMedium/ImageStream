# 📸 ImageStream Athlete Tagger (Pro Edition)

**"Because tools should empower people, not just budgets."**

ImageStream Pro is a high-performance archival scanner built for sports photographers. Whether you have 300 photos or 300,000, this tool helps you reclaim your time by automatically identifying athletes and organizing your history.

---

## 🚀 Why Use ImageStream Pro?

In a world where advanced technology is often kept behind paywalls, ImageStream Pro is built on the principle of **Cooperation over Capital**. 

* **⚡ High Velocity:** Uses every core in your CPU to scan images in parallel—don't wait for one photo at a time.
* **🧠 Smart Memory:** Features an intelligent caching system. After the first scan, it remembers your athletes and starts instantly.
* **🎯 Pro Accuracy:** Uses mathematical "Distance-Matching" to find the best possible match for every face.
* **🛡️ Safe Archiving:** Intelligent collision handling ensures no files are ever overwritten. If a file exists, it simply adds a counter (e.g., _1, _2).

---

## 🛠 Quick Start Guide

### 1. Requirements
You will need Python installed. Open your terminal and run:
pip install face_recognition pillow numpy tqdm

### 2. Setup Your Reference Library
Create a folder named references/ in the same folder as the script. Put one clear headshot of each athlete inside.
Example: references/Lionel_Messi.jpg

### 3. Run the Scan
Point the script at your archive folder. It will scan every sub-folder automatically:
python tagger.py "C:/Your/Photo/Archive"

### 4. Test Mode (Safe Scan)
To see what would happen without actually changing your files, use the "Dry Run" flag:
python tagger.py "C:/Your/Photo/Archive" --dry-run

---

## 🤝 The Vision

This folder is shared for the LinkedIn Photo Hub community. 

I was recently told that this technology is only for "PhDs" or those who want to profit. I disagree. I believe in the flow of perfection and the power of sharing. When we give each other the tools to succeed, the whole community moves faster.

No PhD required. No money needed. Just better photography.

---
*Created with the spirit of cooperation.*
