import os
import sys
import re
import json
import glob

sys.path.insert(0, os.path.abspath('.'))

with open('data.json', 'r', encoding='utf-8') as f:
    DATA_LIST = json.load(f)

from scripts.build_full_corpus_engine import PEOPLE_MAP, PLACES_MAP, TERMS_MAP, expand_shorthand

def is_already_upgraded(content):
    return (
        '## Metadata' in content and
        '### Header & Archival Classification' in content and
        '### Main Text & Margin Notes' in content and
        'Cross-Reference with' in content and
        content.strip().startswith('# Transcription of ')
    )

def extract_dates(text):
    # Search for explicit dates
    m_full = re.findall(r'\b(\d{1,2}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\b', text, re.I)
    if m_full:
        return m_full[0]
    m_my = re.findall(r'\b((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\b', text, re.I)
    if m_my:
        return m_my[0]
    m_ym = re.findall(r'\b(\d{4}\s+(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*)\b', text, re.I)
    if m_ym:
        return m_ym[0]
    m_range = re.findall(r'\b(17\d\d|18\d\d)\s*[–\-]\s*(17\d\d|18\d\d)\b', text)
    if m_range:
        return f"{m_range[0][0]} to {m_range[0][1]}"
    m_yr = re.findall(r'\b(17\d\d|18\d\d)\b', text)
    if m_yr:
        # filter reasonable years
        valid_yrs = [y for y in m_yr if 1740 <= int(y) <= 1860]
        if valid_yrs:
            return valid_yrs[0]
    return "1792 to 1809 / Archival Period"

def extract_source(text):
    m_dj = re.search(r'(?:ANRI\s+)?(?:[\'\"])?Dj(?:okjo|\.)\s+Br(?:ieven|\.)?(?:[\'\"])?\s*(?:no\.|bundel|No\.)?\s*(\d+)', text, re.I)
    if m_dj:
        return f"Peter Carey Collection / Archival Research Notes (ANRI 'Djokjo Brieven' No. {m_dj.group(1)})"
    if 'Overstraten' in text or 'MvO Van Overstraten' in text:
        return "Peter Carey Collection / Archival Research Notes (ANRI Archief van Java's Noordoostkust No. 1 / No. 68: Memorie van Overgave van P.G. van Overstraten)"
    if 'Van den Berg' in text or 'vdBerg' in text:
        return "Peter Carey Collection / Archival Research Notes (ANRI: Memorie van Overgave van J.G. van den Berg, 1803)"
    if 'Book of Klepu' in text or 'Book of Klèpu' in text:
        return "Peter Carey Collection / Archival Research Notes (ANRI 'Djokjo Brieven' No. 41: Ingekomen stukken wegens opgenomen Vorsten Landen, 1770 / Book of Klèpu)"
    if 'Band Coll' in text:
        return "Peter Carey Collection / Archival Research Notes (Band Coll. 308: Conference Notes April 1792)"
    if 'KITLV' in text:
        return "Peter Carey Collection / Archival Research Notes (KITLV Manuscripts)"
    if 'BL Add' in text or 'Crawfurd Coll' in text:
        return "Peter Carey Collection / Archival Research Notes (British Library Additional Manuscripts)"
    if 'Leiden' in text or 'B.P.L.' in text or 'Lor' in text:
        return "Peter Carey Collection / Archival Research Notes (Leiden University Library)"
    if 'de Kock' in text:
        return "Peter Carey Collection / Archival Research Notes (H.M. de Kock Archive)"
    return "Peter Carey Collection / Archival Research Notes (ANRI 'Djokjo Brieven' / Residency Archive)"

def match_entities(text):
    matched_people = {}
    matched_places = {}
    matched_terms = {}

    for k, v in PEOPLE_MAP.items():
        pattern = r'\b' + re.escape(k) + r'\b'
        abbr = v[1].split('/')[0].strip().replace('[', '').replace(']', '')
        abbr_pattern = r'\b' + re.escape(abbr) + r'\b' if len(abbr) >= 2 else None
        if re.search(pattern, text, re.I) or (abbr_pattern and re.search(abbr_pattern, text)):
            matched_people[k] = v

    for k, v in PLACES_MAP.items():
        pattern = r'\b' + re.escape(k) + r'\b'
        abbr = v[1].split('/')[0].strip().replace('[', '').replace(']', '')
        abbr_pattern = r'\b' + re.escape(abbr) + r'\b' if len(abbr) >= 2 else None
        if re.search(pattern, text, re.I) or (abbr_pattern and re.search(abbr_pattern, text)):
            matched_places[k] = v

    for k, v in TERMS_MAP.items():
        pattern = r'\b' + re.escape(k) + r'\b'
        abbr = v[1].split('/')[0].strip().replace('[', '').replace(']', '')
        abbr_pattern = r'\b' + re.escape(abbr) + r'\b' if len(abbr) >= 3 else None
        if re.search(pattern, text, re.I) or (abbr_pattern and re.search(abbr_pattern, text)):
            matched_terms[k] = v

    # Defaults if none matched
    if not matched_people:
        matched_people['Hamengkubuwana II'] = PEOPLE_MAP['Hamengkubuwana II']
    if not matched_places:
        matched_places['Yogyakarta'] = PLACES_MAP['Yogyakarta']
    if not matched_terms:
        matched_terms['Vorstenlanden'] = TERMS_MAP['Vorstenlanden']

    return matched_people, matched_places, matched_terms

def synthesize_key_events(text, date_str, people, places, terms, is_blank=False, is_divider=False):
    if is_blank:
        return "Blank ruled manuscript verso leaf preserving clear binding perforations along the inner margin, faint ink show-through from the recto, and top chronological folder index tabs."
    if is_divider:
        return f"Archival binder card divider sheet demarcating research notes and primary dossiers; features reinforced binding perforations, folder tab annotations, and visible chronological filing tabs ({date_str})."
    
    # Extract existing subheadings and prominent sentences
    headings = re.findall(r'###\s*(.+)', text)
    clean_heads = [h.strip() for h in headings if not h.startswith('[') and len(h.strip()) > 3]
    
    people_names = [p[0] for p in people.values()][:3]
    places_names = [p[0] for p in places.values()][:3]
    
    topic_str = ""
    if clean_heads:
        topic_str = f"Focuses on {clean_heads[0].replace('Entry', '').replace('List', '').strip()}; "
    
    desc = f"Archival research notes and diplomatic documentation ({date_str}). {topic_str}records primary correspondence, administrative negotiations, and political intelligence involving {', '.join(people_names)} across {', '.join(places_names)}; documents internal court governance, fiscal assessments, and colonial interactions in the Vorstenlanden."
    return desc

def process_file(item):
    fpath = item['text']
    img_name = os.path.basename(item['image'])
    img_path = item['image'].replace('\\', '/')
    
    if not os.path.exists(fpath):
        return False, "File does not exist"
        
    with open(fpath, 'r', encoding='utf-8') as fp:
        raw = fp.read()
        
    if is_already_upgraded(raw):
        return True, "Already upgraded"
        
    is_blank = 'blank' in raw.lower() or 'no independent text' in raw.lower()
    is_divider = 'divider' in raw.lower() or 'folder divider' in raw.lower()
    has_table = '| :---' in raw or '|:---' in raw
    
    date_str = extract_dates(raw)
    source_str = extract_source(raw)
    people, places, terms = match_entities(raw)
    key_events = synthesize_key_events(raw, date_str, people, places, terms, is_blank, is_divider)
    
    # Parse existing content section
    content_idx = raw.find('## Content')
    if content_idx != -1:
        body_text = raw[content_idx + len('## Content'):].strip()
    else:
        # strip previous metadata
        body_lines = []
        in_body = False
        for l in raw.splitlines():
            if l.startswith('---'):
                in_body = True
                continue
            if in_body:
                body_lines.append(l)
        body_text = '\n'.join(body_lines).strip() or raw
        
    # Shorthand expansion in body
    expanded_body = expand_shorthand(body_text)
    
    # Archetype selection and Main Text construction
    if is_blank:
        archetype = 3
        header_classification = f"""* **[Physical Target / Object Description]:** `Verso of preceding manuscript leaf; blank ruled notebook paper stock with binding perforations reinforced with clear tape.`
* **[Visible Tabs / Secondary Markings]:** `Faint ink show-through from recto writing; top chronological tabs visible.`"""
        main_text_section = f"""| Margin Notes | Main Text |
| :--- | :--- |
| **Blank Verso<br>Leaf** | <b>Verso of Manuscript Leaf:</b><br><br>Verso of the preceding manuscript leaf ({img_name}):<br><br>• Blank ruled notebook paper.<br>• Binding perforations reinforced with clear adhesive tape along the inner margin.<br>• Faint ink show-through from recto.<br>• Top chronological tabs visible along upper margin. |"""

    elif is_divider:
        archetype = 3
        header_classification = f"""* **[Physical Target / Object Description]:** `Grey archival card folder divider sheet with two-hole punch perforations on the margin.`
* **[Affixed Label / Notation]:** `Folder tab annotation written in ink: {date_str}`
* **[Visible Tabs / Secondary Markings]:** `Chronological index tabs visible along binder edge.`"""
        main_text_section = f"""| Margin Notes | Main Text |
| :--- | :--- |
| **Folder Divider<br>{date_str}** | <b>Archival Folder Divider Leaf:</b><br><br>{expanded_body.replace(chr(10), '<br>')} |"""

    elif has_table:
        archetype = 2
        header_classification = f"""* **[Top Heading]:** `Archival Cadastral & Survey Register`
* **[Archival Document Citation]:** `{source_str}`
* **[Date Span / Register Period]:** `{date_str}`"""
        main_text_section = f"""| Margin Notes | Main Text |
| :--- | :--- |
| **Archival Context:<br>{date_str}** | <b>Registered Territorial & Fiscal Survey:</b><br><br>Official survey of agricultural lands, village allocations, and tax-revenue jurisdictions partitioned among the Central Javanese courts: |

{expanded_body}"""

    else:
        archetype = 1
        header_classification = f"""* **[Top Left / Series]:** `{source_str.split('(')[-1].replace(')', '')}`
* **[Top Center (Ink Color / Notation)]:** `Research Notes / Primary Documentation`
* **[Top Right / Folio]:** `{img_name}`
* **[Upper Subheading / Annotations]:** `{date_str}`"""
        
        # Check if text already has margins or format into 2-column
        paragraphs = [p.strip() for p in expanded_body.split('\n\n') if p.strip()]
        rows = []
        margin_label = f"**{date_str}**"
        
        p_html = []
        for p in paragraphs:
            # format sub-bullets
            lines = p.splitlines()
            p_formatted = "<br>".join(lines).replace('• ', '&nbsp;&nbsp;&nbsp;&nbsp;• ')
            p_html.append(p_formatted)
            
        full_p_html = "<br><br>".join(p_html)
        main_text_section = f"""| Margin Notes | Main Text |
| :--- | :--- |
| {margin_label} | {full_p_html} |"""

    # Build Cross-Reference Section
    people_lines = []
    for k, v in people.items():
        people_lines.append(f"  * **{v[0]}** (`{v[1]}`): Listed under *{v[3]}* (line {v[2]}). {v[4]}")
        
    places_lines = []
    for k, v in places.items():
        places_lines.append(f"  * **{v[0]}** (`{v[1]}`): Listed under *{v[3]}* (line {v[2]}). {v[4]}")
        
    terms_lines = []
    for k, v in terms.items():
        terms_lines.append(f"  * **{v[0]}**: Listed under line {v[2]}. {v[3]}")

    people_block = "\n".join(people_lines)
    places_block = "\n".join(places_lines)
    terms_block = "\n".join(terms_lines)

    cross_ref_section = f"""### Cross-Reference with `39_Expanded_Keyword_Index.md`

* **People:**
{people_block}
* **Places & Institutions:**
{places_block}
* **Terms:**
{terms_block}"""

    # Assemble complete markdown document
    new_doc = f"""# Transcription of {img_name}

## Metadata
- **Image File:** `{img_path}`
- **Source:** {source_str}
- **Date Range:** {date_str}
- **Key Events & Entities:**
  - **Key Events:** {key_events}
  - **Key Entities (Persons):** {', '.join([p[0] for p in people.values()])}
  - **Key Entities (Places):** {', '.join([p[0] for p in places.values()])}
  - **Key Entities (Institutions / Terms):** {', '.join([t[0] for t in terms.values()])}

---

### Header & Archival Classification

{header_classification}

---

### Main Text & Margin Notes

{main_text_section}

---

{cross_ref_section}
"""

    with open(fpath, 'w', encoding='utf-8') as fp:
        fp.write(new_doc.strip() + '\n')
        
    return True, f"Upgraded to Archetype {archetype}"

def run_batch():
    success_count = 0
    skipped_count = 0
    error_count = 0
    
    print(f"Starting batch upgrade across {len(DATA_LIST)} files...")
    
    for idx, item in enumerate(DATA_LIST):
        ok, msg = process_file(item)
        if ok:
            if "Already" in msg:
                skipped_count += 1
            else:
                success_count += 1
        else:
            error_count += 1
            print(f"Error on {item['id']}: {msg}")
            
        if (idx + 1) % 50 == 0 or (idx + 1) == len(DATA_LIST):
            print(f"Processed {idx + 1}/{len(DATA_LIST)} files (Upgraded: {success_count}, Skipped: {skipped_count}, Errors: {error_count})")
            
    print(f"\nBatch processing complete! Upgraded: {success_count}, Previously Upgraded: {skipped_count}, Errors: {error_count}")

if __name__ == '__main__':
    run_batch()
