# Digital Archival Collection & Transcription Template

A modular, zero-dependency, dark-mode static website blueprint designed for historical document archives, manuscripts, and transcription projects.

---

## 🚀 Key Features

- **Side-by-side Transcription Viewer (`transcriptions.html`)**:
  - High-resolution manuscript scan on the left with **mouse-wheel zoom** and **drag-to-pan**.
  - Markdown-rendered transcription on the right.
- **Context-Aware GitHub Issue Reporting**:
  - Highlights selected text from the document and pre-fills a GitHub Issue template automatically with the `Transcription ID` and `Original Text`.
- **Continuous Reading Scroll (`full.html`)**:
  - Renders all transcriptions sequentially in a single scrollable document.
- **Dual-Mode Serving**:
  - Works live over HTTP(S) (fetching `.txt` files directly on refresh) **AND** works completely offline (`file://`) using an auto-generated JSON fallback script.
- **Anti-Caching Protection**:
  - Pre-configured `<meta>` cache-control headers prevent browsers from locking onto stale versions.

---

## 📁 Repository Structure

```
site-template/
├── index.html                 # Main portal / Home page
├── transcriptions.html        # Side-by-side manuscript & transcription viewer
├── full.html                  # Continuous scroll viewer for all documents
├── dictionary.html            # Keyword dictionary / Glossary reference page
│
├── js/
│   ├── viewer.js              # Side-by-side viewer logic & GitHub Issue generator
│   ├── render.js              # Continuous scroll loader
│   ├── marked.min.js          # Lightweight client-side Markdown parser
│   ├── transcriptions-data.js # Index mapping image files to text files
│   └── transcriptions-content.js # Auto-generated offline JSON bundle
│
├── sample_images/             # Folder containing manuscript scan images (.jpg/.png)
├── sample_transcriptions/     # Folder containing Markdown text transcriptions (.txt/.md)
│
└── scripts/
    └── build-transcriptions.py # Python script to update js/transcriptions-content.js
```

---

## 🛠️ How to Customize for a New Project

### Step 1: Set your GitHub Repository
Open `js/viewer.js` and `js/render.js` in a text editor and update the top variable with your GitHub repository path:
```javascript
const GITHUB_REPO = "YourUsername/YourRepoName";
```

### Step 2: Add Your Manuscript Scans & Transcriptions
1. Drop your scanned manuscript images into `sample_images/` (e.g., `IMG_0001.jpg`).
2. Create matching `.txt` transcription files in `sample_transcriptions/` (e.g., `IMG_0001.txt`).

### Step 3: Register Items in `js/transcriptions-data.js`
Update `js/transcriptions-data.js` to map your image files to their text files:
```javascript
window.__TRANSCRIPTIONS_DATA__ = [
  { "id": "IMG_0001", "image": "sample_images/IMG_0001.jpg", "text": "sample_transcriptions/IMG_0001.txt" },
  { "id": "IMG_0002", "image": "sample_images/IMG_0002.jpg", "text": "sample_transcriptions/IMG_0002.txt" }
];
```

### Step 4: Rebuild the Offline Content Bundle
Whenever you add or modify `.txt` files, run the Python build script from the command line:
```bash
python scripts/build-transcriptions.py
```
This updates `js/transcriptions-content.js` so users viewing the site locally without a server can view the latest text.

---

## 🌐 Deployment to GitHub Pages

1. Commit and push the folder contents to a public GitHub repository.
2. Go to **Repository Settings -> Pages**.
3. Select the `main` branch and `/ (root)` folder as the source.
4. Save, and your site will be live at `https://yourusername.github.io/your-repo-name/`.