import re
import json

def build_index():
    with open('39_Expanded_Keyword_Index.md', 'r', encoding='utf-8') as f:
        lines = f.readlines()

    entries = []
    current_top = 'General'
    current_sub = 'General'

    for idx, line in enumerate(lines):
        line_num = idx + 1
        l = line.strip()
        if l.startswith('## '):
            current_top = re.sub(r'^\d+\.\s*', '', l.replace('##', '').strip())
            current_sub = current_top
            continue
        if l.startswith('### '):
            current_sub = re.sub(r'\s*\(Appendix.*?\)', '', l.replace('###', '').strip())
            continue
        
        # Bullet item: * **Term**: Description
        m = re.match(r'^\*\s+\*\*([^*]+?)\*\*:\s*(.+)$', l)
        if m:
            term_raw = m.group(1).strip()
            desc = m.group(2).strip()
            entries.append({
                'line': line_num,
                'top_category': current_top,
                'sub_category': current_sub,
                'term': term_raw,
                'desc': desc
            })
            continue
            
        # Sub-item: * *Term* (Description)
        m2 = re.match(r'^\*\s+\*([^*]+?)\*(?:\s*[-:]|\s*\((.+)\)|\s*(.+))?$', l)
        if m2:
            t = m2.group(1).strip()
            d = (m2.group(2) or m2.group(3) or '').strip() or current_sub
            entries.append({
                'line': line_num,
                'top_category': current_top,
                'sub_category': current_sub,
                'term': t,
                'desc': d
            })
            continue

        # Plain bullet: * Name (Years/Details)
        m3 = re.match(r'^\*\s+([A-Za-z\u00C0-\u017F\s\.\,\-\'\(\)]+?)(?:\s*\((.*?)\))?$', l)
        if m3 and not l.startswith('*   *') and not l.startswith('*   **') and len(l) > 6:
            t = m3.group(1).strip()
            d = m3.group(2) or current_sub
            if len(t) > 3 and not t.startswith('Appendix') and not t.startswith('Book'):
                entries.append({
                    'line': line_num,
                    'top_category': current_top,
                    'sub_category': current_sub,
                    'term': t,
                    'desc': d
                })

    # Save to json
    with open('scripts/entity_database.json', 'w', encoding='utf-8') as f:
        json.dump(entries, f, indent=2, ensure_ascii=False)

    print(f"Extracted {len(entries)} entities from 39_Expanded_Keyword_Index.md to scripts/entity_database.json")

if __name__ == '__main__':
    build_index()
