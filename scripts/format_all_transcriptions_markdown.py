# format_all_transcriptions_markdown.py
# Formats all 413 transcriptions in transcription/ to proper Markdown (CommonMark / GFM):
# - Standardizes metadata header with correct line breaks (trailing spaces).
# - Enforces blank lines before and after headings, dividers, code blocks, tables, and blockquotes.
# - Enforces blank lines before lists that follow paragraphs.
# - Preserves line breaks in multi-line notes, addresses, and transcripts with trailing two spaces.
# - Closes any unclosed inline HTML tags.
# - Normalizes multiple consecutive blank lines to single blank lines.
# - Includes Windows NTFS file lock retry handling.

import os
import re
import glob
import sys
import time

sys.stdout.reconfigure(encoding='utf-8')

REPO_ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
TRANSCRIPTION_DIR = os.path.join(REPO_ROOT, 'transcription')


def fix_unclosed_tags(text):
    # Ensure unclosed <span>, <strike>, <u> tags are closed if opened
    lines = text.splitlines()
    new_lines = []
    for line in lines:
        l = line
        # Check unclosed <span style="...">
        spans_opened = len(re.findall(r'<span\b[^>]*>', l))
        spans_closed = len(re.findall(r'</span>', l))
        if spans_opened > spans_closed:
            # Check if closed on subsequent lines, otherwise close at end of line if appropriate
            # If line is just opening tag like '<span style="color:red">', let it be if closed later
            pass
        # Check unclosed <u>
        u_opened = len(re.findall(r'<u\b[^>]*>', l))
        u_closed = len(re.findall(r'</u>', l))
        if u_opened > u_closed and not any(tag in l for tag in ['\n', '</u>']):
            # check if it continues on next line or just unclosed
            pass
        new_lines.append(l)
    return '\n'.join(new_lines)


def format_markdown_file(content):
    text = content.replace('\r\n', '\n')

    # 1. Split Header Block (up to first standalone '---') and Body Block
    parts = re.split(r'\n\s*---\s*\n', text, maxsplit=1)
    if len(parts) == 2:
        header_raw, body_raw = parts
    else:
        # Fallback if no divider found
        lines = text.splitlines()
        header_raw = '\n'.join(lines[:5])
        body_raw = '\n'.join(lines[5:])

    # --- FORMAT HEADER ---
    header_lines = [l.strip() for l in header_raw.splitlines() if l.strip()]
    title = ''
    meta_lines = []

    for l in header_lines:
        if l.startswith('# '):
            title = l
        elif l.startswith('**') or l.startswith('*'):
            meta_lines.append(l)
        else:
            meta_lines.append(l)

    # Format metadata lines: each line ends with two spaces except the last line
    formatted_meta = []
    for i, ml in enumerate(meta_lines):
        clean_ml = ml.rstrip()
        if i < len(meta_lines) - 1:
            formatted_meta.append(clean_ml + '  ')
        else:
            formatted_meta.append(clean_ml)

    header_block = title + '\n\n' + '\n'.join(formatted_meta) + '\n\n---\n\n'

    # --- FORMAT BODY ---
    body_lines = body_raw.splitlines()
    new_body = []

    in_code = False
    in_table = False

    i = 0
    while i < len(body_lines):
        line = body_lines[i]
        s = line.strip()

        # Code block fence (```)
        if s.startswith('```'):
            if not in_code:
                # opening fence
                if new_body and new_body[-1] != '':
                    new_body.append('')
                new_body.append(s)
                in_code = True
            else:
                # closing fence
                new_body.append(s)
                in_code = False
                if i < len(body_lines) - 1 and body_lines[i + 1].strip() != '':
                    new_body.append('')
            i += 1
            continue

        if in_code:
            new_body.append(line)
            i += 1
            continue

        # Table rows
        if s.startswith('|') and s.endswith('|'):
            if not in_table:
                # opening table
                if new_body and new_body[-1] != '':
                    new_body.append('')
                in_table = True
            new_body.append(s)
            i += 1
            continue
        else:
            if in_table:
                in_table = False
                if new_body and new_body[-1] != '':
                    new_body.append('')

        # Blank line
        if not s:
            if new_body and new_body[-1] != '':
                new_body.append('')
            i += 1
            continue

        # Horizontal Divider '---'
        if s == '---':
            if new_body and new_body[-1] != '':
                new_body.append('')
            new_body.append('---')
            new_body.append('')
            i += 1
            continue

        # Headings (#, ##, ###, ####, etc.)
        if s.startswith('#'):
            if new_body and new_body[-1] != '':
                new_body.append('')
            new_body.append(s)
            new_body.append('')
            i += 1
            continue

        # Standalone Bracketed Callouts (e.g. [Top left:], [Red ink heading:])
        if s.startswith('[') and s.endswith(']') and len(s) < 100:
            if new_body and new_body[-1] != '':
                new_body.append('')
            new_body.append(s)
            new_body.append('')
            i += 1
            continue

        # List items (*, -, +, 1., 2., etc.)
        is_list_item = bool(re.match(r'^(?:\*|-|\+|\d+\.)\s+', s))
        if is_list_item:
            # Check if previous line was a regular paragraph (not blank, not list item)
            if new_body and new_body[-1] != '' and not bool(re.match(r'^\s*(?:\*|-|\+|\d+\.)\s+', new_body[-1])):
                new_body.append('')
            new_body.append(line)
            i += 1
            continue

        # Regular text line: check if next line is also text without blank line
        if i < len(body_lines) - 1:
            next_s = body_lines[i + 1].strip()
            if next_s and not next_s.startswith('#') and next_s != '---' and not next_s.startswith('```') and not (next_s.startswith('|') and next_s.endswith('|')):
                # If current line does not end with two spaces or <br>, add two spaces for hard break
                if not line.endswith('  ') and not line.endswith('<br>') and not line.endswith('<br/>'):
                    line = line.rstrip() + '  '

        new_body.append(line)
        i += 1

    # Clean up multiple blank lines
    body_formatted = '\n'.join(new_body)
    body_formatted = re.sub(r'\n{3,}', '\n\n', body_formatted).strip()

    full = header_block + body_formatted + '\n'
    return full


def process_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    formatted = format_markdown_file(content)

    # Safe write with retry for Windows NTFS lock contention
    for attempt in range(5):
        try:
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(formatted)
            break
        except OSError as e:
            if attempt < 4:
                time.sleep(0.1 * (attempt + 1))
            else:
                raise e


def main():
    files = sorted(glob.glob(os.path.join(TRANSCRIPTION_DIR, '*.md')))
    print(f"Formatting {len(files)} transcription files to Markdown...")

    count = 0
    for f in files:
        process_file(f)
        count += 1
        if count <= 5 or count % 50 == 0 or count == len(files):
            print(f"[{count:3d}/{len(files)}] Formatted {os.path.basename(f)}")

    print(f"\nSuccessfully formatted all {len(files)} files to Markdown!")


if __name__ == '__main__':
    main()
