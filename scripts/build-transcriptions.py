#!/usr/bin/env python3
"""
Generate js/transcriptions-data.js and js/transcriptions-content.js
from the jpg/ and transcription/ directories.
"""
import json
from pathlib import Path

BASE = Path(__file__).parent.parent
JPG_DIR = BASE / "jpg"
MD_DIR = BASE / "transcription"
DATA_JS = BASE / "js" / "transcriptions-data.js"
CONTENT_JS = BASE / "js" / "transcriptions-content.js"

def build():
    # Gather all jpg files
    jpg_files = sorted([f for f in JPG_DIR.iterdir() if f.is_file() and f.suffix.lower() in ['.jpg', '.jpeg']])

    data_entries = []
    content = {}
    missing_md = []

    for jpg in jpg_files:
        base_name = jpg.stem
        md_file = MD_DIR / f"{base_name}.md"

        # We store the posix path relative to the BASE directory for the web frontend
        image_path = f"jpg/{jpg.name}"
        text_path = f"transcription/{md_file.name}"

        entry = {
            "id": base_name,
            "image": image_path,
            "text": text_path
        }
        data_entries.append(entry)

        if md_file.exists():
            content[base_name] = md_file.read_text(encoding="utf-8")
        else:
            missing_md.append(text_path)

    # 1. Write transcriptions-data.js
    data_payload = json.dumps(data_entries, indent=2, ensure_ascii=False)
    DATA_JS.write_text(
        f"/* AUTO-GENERATED — do not edit by hand. */\nwindow.__TRANSCRIPTIONS_DATA__ = {data_payload};\n",
        encoding="utf-8"
    )

    # 2. Write transcriptions-content.js
    content_payload = json.dumps(content, ensure_ascii=False)
    content_payload = content_payload.replace("\u2028", "\\u2028").replace("\u2029", "\\u2029")

    CONTENT_JS.write_text(
        f"/* AUTO-GENERATED from transcriptions — do not edit by hand. */\nwindow.__TRANSCRIPTIONS_CONTENT__ = {content_payload};\n",
        encoding="utf-8"
    )

    print(f"Successfully generated data and content for {len(data_entries)} entries.")
    if missing_md:
        print(f"WARNING: {len(missing_md)} missing transcription file(s):", missing_md)

if __name__ == "__main__":
    build()
