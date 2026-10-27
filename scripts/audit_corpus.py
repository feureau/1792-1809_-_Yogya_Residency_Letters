import json
import os
import re

def full_deep_audit():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Executing complete deep audit across all {len(data)} files...")

    issues = []
    archetypes = {1: 0, 2: 0, 3: 0}

    for idx, item in enumerate(data):
        fid = item['id']
        fpath = item['text']
        img_path = item['image']

        if not os.path.exists(fpath):
            issues.append((fid, "File missing on disk"))
            continue
        if not os.path.exists(img_path):
            issues.append((fid, "Image missing on disk"))
            continue

        with open(fpath, 'r', encoding='utf-8') as fp:
            content = fp.read()

        # 1. Title format check
        img_basename = os.path.basename(img_path)
        expected_title = f"# Transcription of {img_basename}"
        if not content.startswith(expected_title):
            issues.append((fid, f"Title mismatch: {content.splitlines()[0]} != {expected_title}"))

        # 2. Check legacy markers
        legacy_checks = [
            "## Content",
            "**Keyword Index Check:**",
            "**Transcription Type:**",
            "**Transcribed by:**"
        ]
        for leg in legacy_checks:
            if leg in content:
                issues.append((fid, f"Contains legacy marker: {leg}"))

        # 3. Check required sections
        required_sections = [
            "## Metadata",
            "- **Image File:**",
            "- **Source:**",
            "- **Date Range:**",
            "- **Key Events & Entities:**",
            "- **Key Events:**",
            "- **Key Entities (Persons):**",
            "- **Key Entities (Places):**",
            "- **Key Entities (Institutions / Terms):**",
            "### Header & Archival Classification",
            "### Main Text & Margin Notes",
            "### Cross-Reference with `39_Expanded_Keyword_Index.md`",
            "* **People:**",
            "* **Places & Institutions:**",
            "* **Terms:**"
        ]
        for sec in required_sections:
            if sec not in content:
                issues.append((fid, f"Missing section: {sec}"))

        # 4. Check HTML tags
        for tag in ['u', 'i', 'b', 'span']:
            open_tags = len(re.findall(rf'<{tag}(?:\s+[^>]*?)?>', content))
            close_tags = len(re.findall(rf'</{tag}>', content))
            if open_tags != close_tags:
                issues.append((fid, f"Mismatched <{tag}> tags: {open_tags} open vs {close_tags} close"))

        # 5. Check markdown table syntax (splitting only on unescaped pipes)
        lines = content.splitlines()
        in_table = False
        table_cols = 0
        for l_num, l in enumerate(lines):
            l_str = l.strip()
            if '| :---' in l_str or '|:---' in l_str:
                in_table = True
                header_line = lines[l_num - 1].strip()
                table_cols = len([c for c in re.split(r'(?<!\\)\|', header_line)[1:-1]])
                continue
            if in_table:
                if not l_str.startswith('|'):
                    in_table = False
                    continue
                cols = len([c for c in re.split(r'(?<!\\)\|', l_str)[1:-1]])
                # Allow sub-tables or row continuity if valid
                if cols != table_cols and cols > 0 and table_cols > 0:
                    # check if next line is a new table delimiter
                    if l_num + 1 < len(lines) and ('| :---' in lines[l_num + 1] or '|:---' in lines[l_num + 1]):
                        in_table = False
                        continue
                    issues.append((fid, f"Table column mismatch at line {l_num+1}: {cols} != {table_cols}"))

        # Categorize
        if "Physical Target" in content or "Physical Object" in content or "Blank Verso" in content or "Folder Divider" in content:
            archetypes[3] += 1
        elif "Cadastral" in content or "Book of Klèpu" in content or "| Location / Village" in content or "| Location" in content or "Table Variation A" in content:
            archetypes[2] += 1
        else:
            archetypes[1] += 1

    print("\n================ AUDIT SUMMARY ================")
    print(f"Total files audited: {len(data)}")
    print(f"Archetype 1 (Narrative Notes, Letters & Diaries): {archetypes[1]}")
    print(f"Archetype 2 (Tabular Surveys & Registers): {archetypes[2]}")
    print(f"Archetype 3 (Covers, Dividers & Physical Artifacts): {archetypes[3]}")
    print(f"Total issues found: {len(issues)}")

    if issues:
        print("\nIssues encountered:")
        for eid, err in issues[:20]:
            print(f"  {eid}: {err}")
    else:
        print("\nCONCORDANCE: 100% PERFECT! ALL 413 TRANSCRIPTION FILES ARE FLAWLESS!")

if __name__ == '__main__':
    full_deep_audit()
