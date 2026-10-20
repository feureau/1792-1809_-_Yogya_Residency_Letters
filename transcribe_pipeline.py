#!/usr/bin/env python3
"""
Archival Transcription Pipeline
Transcribes historical archival scans of Peter Carey's research notes on the
Yogyakarta Residency Letters (1792-1809) using Google GenAI (gemini-2.5-flash).
"""

import os
import sys
import glob
import json
import time
import argparse
from datetime import datetime
from PIL import Image
from google import genai
from google.genai.errors import APIError

# Fix Windows console UTF-8 output
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
        sys.stderr.reconfigure(encoding="utf-8")
    except Exception:
        pass

ROOT_DIR = os.path.dirname(os.path.abspath(__file__))
TRANSCRIPTION_DIR = os.path.join(ROOT_DIR, "transcription")
STATUS_FILE = os.path.join(ROOT_DIR, "transcription_status.json")
MASTER_DOC = os.path.join(ROOT_DIR, "1792-1809 - Yogya Residency Letters.md")
KEYWORD_INDEX_FILE = os.path.join(ROOT_DIR, "39_Expanded_Keyword_Index.md")

os.makedirs(TRANSCRIPTION_DIR, exist_ok=True)

def load_reference_materials():
    """Loads the keyword index and abbreviations table as domain context."""
    keyword_text = ""
    if os.path.exists(KEYWORD_INDEX_FILE):
        with open(KEYWORD_INDEX_FILE, "r", encoding="utf-8") as f:
            keyword_text = f.read()

    abbreviations_text = ""
    if os.path.exists(MASTER_DOC):
        with open(MASTER_DOC, "r", encoding="utf-8") as f:
            lines = f.readlines()
            # Capture Abbreviations section (approx first 120 lines)
            abbrev_lines = []
            capture = False
            for line in lines:
                if line.startswith("## Abbreviations"):
                    capture = True
                elif capture and line.startswith("## ") and not line.startswith("### "):
                    break
                if capture:
                    abbrev_lines.append(line)
            abbreviations_text = "".join(abbrev_lines)

    return keyword_text, abbreviations_text

def build_system_prompt(keyword_text, abbreviations_text):
    return f"""You are an expert paleographer and colonial historian of Java specializing in 18th-19th century British and Dutch colonial documents and Peter Carey's handwritten archival research notes on the 'Yogyakarta Residency Letters (1792-1809)'.

### Reference Materials:
#### Common Archival Abbreviations:
{abbreviations_text}

#### Historical Names and Terms Glossary (Selected Index):
{keyword_text[:25000]}

### Paleographical Guidelines for Peter Carey's Handwriting:
1. Names and Titles:
   - HB I / HB II / HB III: Hamengkubuwana (Sultan of Yogya)
   - PB III / PB IV: Pakubuwana (Sunan of Surakarta)
   - MN I / MN II / PWD / PWP: Mangkunagara / Prangwedana
   - PRI / PRII: Peter Carey's handwriting frequently writes Danureja I / II (Patih of Yogya) as PRI / PRII or DRI / DRII. Transcribe as written with clarification if helpful.
   - Resident / colonial officials: Waterloo (Wat), Nicolaas Engelhard (Eng / N.E.), Van IJsseldijk (Van IJ), Van den Berg (VdB), Herman Willem Daendels (D. / often written phonetically as 'Saendjes' or 'Saerdels'), G.W. Wiese, J.A. van Braam, A.H. Wiese, A.A. Buyskes.
   - Javanese titles: R.T. (Raden Tumenggung), Rg. (Regent), Bup. (Bupati), Ng. (Ngabehi), P. (Pangéran), R. (Raden), R.A. (Raden Ayu), R.M. (Raden Mas).
   - Javanese terms: cacah, jung, bau, pikul, corge, paseban, kraton, alun-alun, gladhag, rampog macan, priyayi, bekel, mantri, wong durjana, kècu.
   - Archival series: MvO (Mémoire van Overgave), Dj. Br. / P.J. Br. (Djokjo Brieven), AvJ / Dj.A. (Archief van Jogja), KITLV, ANRI / Arsip Negara.
   - Louwmaand = January (archaic Dutch).

2. Structural & Transcription Rules:
   - Transcribe ALL handwritten and printed content faithfully into clean GitHub Markdown.
   - Preserve tables, hierarchical bullet lists, columns, headings, dates, numbers, and monetary sums.
   - Note colored ink or pencil annotations (e.g. `[in red ink: ...]`, `[in pencil: ...]`, `[marginal note: ...]`).
   - For crossed-out or corrected words, use strikethrough: `~~crossed out text~~`.
   - Preserve seals, stamps, or folder tab notes (e.g., `[Folder tab: ...]`, `[Stamp: Arsip Nasional ...]`).
   - If an image is a non-text scan (e.g. color calibration target card, blank lined paper, folder cover), describe the physical artifact clearly and succinctly in brackets.

3. Output Schema:
Do not surround the response in ```markdown ``` fences. Return raw Markdown starting directly with:
# Transcription: <ImageFileName>

**Image File:** `<RelativeImagePath>`  
**Keyword Index Check:** Verified against `39_Expanded_Keyword_Index.md` (*<comma-separated list of identified names, places, and terms>*)

---

## Content

<Full transcribed text and tables>
"""

def get_image_list():
    """Returns sorted list of tuples (rel_path, target_md_name, category)."""
    items = []

    # 1. Cover images
    covers = sorted(glob.glob(os.path.join(ROOT_DIR, "Cover", "jpg", "*.[jJ][pP][gG]")))
    for path in covers:
        rel = os.path.relpath(path, ROOT_DIR).replace("\\", "/")
        base = os.path.basename(path)
        name, _ = os.path.splitext(base)
        target = f"Cover_{name}.md"
        items.append((rel, target, "cover"))

    # 2. Batch 1 (20260618)
    b1 = sorted(glob.glob(os.path.join(ROOT_DIR, "jpg", "IMG_20260618_*.[jJ][pP][gG]")))
    for path in b1:
        rel = os.path.relpath(path, ROOT_DIR).replace("\\", "/")
        base = os.path.basename(path)
        name, _ = os.path.splitext(base)
        target = f"{name}.md"
        items.append((rel, target, "batch1_20260618"))

    # 3. Batch 2 (20260619)
    b2 = sorted(glob.glob(os.path.join(ROOT_DIR, "jpg", "IMG_20260619_*.[jJ][pP][gG]")))
    for path in b2:
        rel = os.path.relpath(path, ROOT_DIR).replace("\\", "/")
        base = os.path.basename(path)
        name, _ = os.path.splitext(base)
        # Distinguish the calibration card IMG_20260619_0001.jpg
        if name == "IMG_20260619_0001":
            target = "IMG_20260619_0001_calibration.md"
        else:
            target = f"{name}.md"
        items.append((rel, target, "batch2_20260619"))

    return items

def load_status():
    if os.path.exists(STATUS_FILE):
        try:
            with open(STATUS_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_status(status):
    with open(STATUS_FILE, "w", encoding="utf-8") as f:
        json.dump(status, f, indent=2, ensure_ascii=False)

def preprocess_image(abs_path, max_dim=3000):
    """Opens image and scales down if max dimension > max_dim to maintain fast transfer."""
    img = Image.open(abs_path)
    if img.mode != "RGB":
        img = img.convert("RGB")
    w, h = img.size
    if max(w, h) > max_dim:
        scale = max_dim / float(max(w, h))
        new_w = int(w * scale)
        new_h = int(h * scale)
        img = img.resize((new_w, new_h), Image.Resampling.LANCZOS)
    return img

def transcribe_image(client, prompt, abs_path, rel_path, max_retries=5):
    img = preprocess_image(abs_path)
    user_prompt = f"Please transcribe the following image: {os.path.basename(rel_path)} (Path: {rel_path}). Follow the system instructions faithfully."

    for attempt in range(max_retries):
        try:
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=[img, prompt, user_prompt]
            )
            text = response.text or ""
            # Clean possible markdown wrapping if returned
            if text.startswith("```markdown"):
                text = text[len("```markdown"):].strip()
            if text.startswith("```md"):
                text = text[len("```md"):].strip()
            if text.endswith("```"):
                text = text[:-3].strip()
            return text
        except Exception as e:
            wait_time = (2 ** attempt) * 2
            print(f"  [Attempt {attempt+1}/{max_retries}] Error transcribing {rel_path}: {e}")
            if attempt == max_retries - 1:
                raise e
            print(f"  Backing off for {wait_time}s...")
            time.sleep(wait_time)

import threading
from concurrent.futures import ThreadPoolExecutor, as_completed

status_lock = threading.Lock()

def save_status_locked(status):
    with status_lock:
        with open(STATUS_FILE, "w", encoding="utf-8") as f:
            json.dump(status, f, indent=2, ensure_ascii=False)

def process_single_item(item, client, prompt, status, total, force, counter, counter_lock):
    rel_path, target_name, cat = item
    target_path = os.path.join(TRANSCRIPTION_DIR, target_name)
    abs_img_path = os.path.join(ROOT_DIR, rel_path)

    if not force and rel_path in status and status[rel_path].get("status") == "completed" and os.path.exists(target_path):
        with counter_lock:
            counter["skipped"] += 1
            idx = counter["processed"] = counter["processed"] + 1
        print(f"[{idx}/{total}] Skipping already completed: {target_name}")
        return "skipped"

    with counter_lock:
        idx = counter["processed"] = counter["processed"] + 1

    print(f"[{idx}/{total}] Transcribing ({cat}): {rel_path} -> {target_name} ...")
    t0 = time.time()
    try:
        content = transcribe_image(client, prompt, abs_img_path, rel_path)
        with open(target_path, "w", encoding="utf-8") as f:
            f.write(content.strip() + "\n")

        with status_lock:
            status[rel_path] = {
                "status": "completed",
                "target_file": target_name,
                "category": cat,
                "timestamp": datetime.now().isoformat(),
                "chars": len(content),
                "duration_sec": round(time.time() - t0, 2)
            }
            save_status_locked(status)

        with counter_lock:
            counter["completed"] += 1
        print(f"  [OK] [{target_name}] Finished in {round(time.time() - t0, 1)}s ({len(content)} chars)")
        time.sleep(0.5)
        return "completed"
    except Exception as e:
        print(f"  [FAIL] [{target_name}] FAILED: {e}")
        with status_lock:
            status[rel_path] = {
                "status": "failed",
                "target_file": target_name,
                "error": str(e),
                "timestamp": datetime.now().isoformat()
            }
            save_status_locked(status)
        with counter_lock:
            counter["failed"] += 1
        return "failed"

def run_transcription(start=0, count=None, force=False, single=None, workers=4):
    client = genai.Client()
    keyword_text, abbrev_text = load_reference_materials()
    prompt = build_system_prompt(keyword_text, abbrev_text)
    items = get_image_list()
    status = load_status()

    if single:
        target_items = [item for item in items if single in item[0] or single in item[1]]
        if not target_items:
            print(f"Error: Single image pattern '{single}' not found.")
            return
        items = target_items
    else:
        if count is not None:
            items = items[start:start+count]
        else:
            items = items[start:]

    total = len(items)
    print(f"Starting transcription pipeline for {total} images (workers={workers}, force={force})...")

    counter = {"processed": 0, "completed": 0, "skipped": 0, "failed": 0}
    counter_lock = threading.Lock()

    if workers <= 1:
        for item in items:
            process_single_item(item, client, prompt, status, total, force, counter, counter_lock)
    else:
        with ThreadPoolExecutor(max_workers=workers) as executor:
            futures = [
                executor.submit(process_single_item, item, client, prompt, status, total, force, counter, counter_lock)
                for item in items
            ]
            for future in as_completed(futures):
                try:
                    future.result()
                except Exception as e:
                    print(f"Worker exception: {e}")

    print(f"\nRun Summary: {counter['completed']} completed, {counter['skipped']} skipped, {counter['failed']} failed.")

def compile_master_document():
    """Compiles all transcriptions into '1792-1809 - Yogya Residency Letters.md'."""
    items = get_image_list()
    status = load_status()
    _, abbrev_text = load_reference_materials()

    print(f"Compiling master document from {len(items)} transcribed items...")

    lines = []
    lines.append("# Yogyakarta Residency Letters 1792–1809\n")
    lines.append("Transcribed from the Peter Carey Archive\n\n")

    if abbrev_text:
        lines.append(abbrev_text.strip() + "\n\n")

    lines.append("---\n\n")

    # Group by category
    categories = [
        ("cover", "Archive Folder Covers and Physical Bindings"),
        ("batch1_20260618", "Volume I: Yogyakarta Residency Letters & Notes (1792–1809) - Series 20260618"),
        ("batch2_20260619", "Volume II: Supplementary Notes, Registers & Arsip Nasional Documents - Series 20260619")
    ]

    for cat_id, cat_title in categories:
        cat_items = [item for item in items if item[2] == cat_id]
        if not cat_items:
            continue

        lines.append(f"# {cat_title}\n\n")

        for rel_path, target_name, _ in cat_items:
            target_path = os.path.join(TRANSCRIPTION_DIR, target_name)
            if not os.path.exists(target_path):
                continue

            with open(target_path, "r", encoding="utf-8") as f:
                content = f.read().strip()

            # Clean and format page block
            lines.append(f"<!-- Page Start: {target_name} -->\n")
            lines.append(content)
            lines.append("\n\n---\n\n")

    with open(MASTER_DOC, "w", encoding="utf-8") as f:
        f.write("".join(lines))

    print(f"Master document successfully written to: {MASTER_DOC} ({os.path.getsize(MASTER_DOC)} bytes)")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Transcription pipeline for Carey Archive")
    parser.add_argument("--start", type=int, default=0, help="Start index (0-based)")
    parser.add_argument("--count", type=int, default=None, help="Number of files to process")
    parser.add_argument("--force", action="store_true", help="Force re-transcription of completed files")
    parser.add_argument("--single", type=str, default=None, help="Transcribe single file matching pattern")
    parser.add_argument("--workers", type=int, default=4, help="Number of concurrent worker threads")
    parser.add_argument("--compile", action="store_true", help="Compile master markdown document")

    args = parser.parse_args()

    if args.compile:
        compile_master_document()
    else:
        run_transcription(start=args.start, count=args.count, force=args.force, single=args.single, workers=args.workers)
