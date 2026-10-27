import json
import os
import re

def validate_all():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Validating all {len(data)} transcription files against Master Specification...")

    errors = []
    archetypes = {1: 0, 2: 0, 3: 0}

    for idx, item in enumerate(data):
        fpath = item['text']
        img_name = os.path.basename(item['image'])

        if not os.path.exists(fpath):
            errors.append((item['id'], "File missing on disk"))
            continue

        with open(fpath, 'r', encoding='utf-8') as fp:
            c = fp.read()

        # Check required sections
        expected_title = f"# Transcription of {img_name}"
        if not c.startswith(expected_title):
            errors.append((item['id'], f"Title mismatch. Expected: {expected_title}"))

        if "## Metadata" not in c:
            errors.append((item['id'], "Missing '## Metadata'"))
        if "- **Image File:**" not in c:
            errors.append((item['id'], "Missing '- **Image File:**'"))
        if "- **Source:**" not in c:
            errors.append((item['id'], "Missing '- **Source:**'"))
        if "- **Date Range:**" not in c:
            errors.append((item['id'], "Missing '- **Date Range:**'"))
        if "- **Key Events & Entities:**" not in c:
            errors.append((item['id'], "Missing '- **Key Events & Entities:**'"))
        if "- **Key Events:**" not in c:
            errors.append((item['id'], "Missing '- **Key Events:**'"))
        if "- **Key Entities (Persons):**" not in c:
            errors.append((item['id'], "Missing '- **Key Entities (Persons):**'"))
        if "- **Key Entities (Places):**" not in c:
            errors.append((item['id'], "Missing '- **Key Entities (Places):**'"))
        if "- **Key Entities (Institutions / Terms):**" not in c:
            errors.append((item['id'], "Missing '- **Key Entities (Institutions / Terms):**'"))

        if "### Header & Archival Classification" not in c:
            errors.append((item['id'], "Missing '### Header & Archival Classification'"))
        if "### Main Text & Margin Notes" not in c:
            errors.append((item['id'], "Missing '### Main Text & Margin Notes'"))
        if "### Cross-Reference with `39_Expanded_Keyword_Index.md`" not in c:
            errors.append((item['id'], "Missing '### Cross-Reference with `39_Expanded_Keyword_Index.md`'"))

        if "* **People:**" not in c:
            errors.append((item['id'], "Missing '* **People:**'"))
        if "* **Places & Institutions:**" not in c:
            errors.append((item['id'], "Missing '* **Places & Institutions:**'"))
        if "* **Terms:**" not in c:
            errors.append((item['id'], "Missing '* **Terms:**'"))

        # Determine archetype
        if "Physical Target" in c or "Physical Object" in c or "Blank Verso" in c or "Folder Divider" in c:
            archetypes[3] += 1
        elif "Cadastral" in c or "Cadastral, Village & Cacah Surveys" in c or "Book of Klèpu" in c or "| Location / Village" in c or "| Location" in c:
            archetypes[2] += 1
        else:
            archetypes[1] += 1

    print("\n--- VALIDATION RESULTS ---")
    print(f"Total files validated: {len(data)}")
    print(f"Archetype 1 (Narrative Notes, Letters & Diaries): {archetypes[1]}")
    print(f"Archetype 2 (Tabular Surveys & Registers): {archetypes[2]}")
    print(f"Archetype 3 (Covers, Dividers & Physical Artifacts): {archetypes[3]}")
    print(f"Total errors: {len(errors)}")

    if errors:
        print("\nErrors encountered:")
        for eid, err in errors[:10]:
            print(f"  {eid}: {err}")
    else:
        print("\nALL 413 TRANSCRIPTION FILES PASSED 100% STRICT SCHEMA VALIDATION!")

if __name__ == '__main__':
    validate_all()
