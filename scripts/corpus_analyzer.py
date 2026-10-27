import json
import re
import os
import glob

def analyze_corpus():
    with open('data.json', 'r', encoding='utf-8') as f:
        data = json.load(f)

    print(f"Total entries in data.json: {len(data)}")
    
    types = {
        'cover': 0,
        'divider': 0,
        'register_table': 0,
        'treaty_conference': 0,
        'mvo': 0,
        'residency_letter': 0,
        'chevallier_diary': 0,
        'already_upgraded': 0
    }

    for item in data:
        tpath = item['text']
        if not os.path.exists(tpath):
            continue
        with open(tpath, 'r', encoding='utf-8') as fp:
            content = fp.read()
        
        # Check if already upgraded
        if 'Cross-Reference with' in content and '## Metadata' in content and '### Header & Archival Classification' in content:
            types['already_upgraded'] += 1
            continue

        fid = item['id']
        if fid.startswith('Cover_'):
            types['cover'] += 1
        elif 'divider' in content.lower() or 'LIST OF MSS' in content or 'LIST G MSS' in content:
            types['divider'] += 1
        elif 'Chevallier' in content or 'REGISTER CONCERNING DP' in content or ('1825' in content and 'Tegalrejo' in content):
            types['chevallier_diary'] += 1
        elif 'Memorie van Overgave' in content or 'MvO' in content or 'Overstraten' in content or 'Van den Berg' in content:
            types['mvo'] += 1
        elif 'Book of Klepu' in content or 'Book of Klèpu' in content or 'Lands / Cacahs' in content or ('| :---' in content and 'Cacahs' in content):
            types['register_table'] += 1
        elif 'Band Coll' in content or 'Conference' in content or 'Troupes' in content or 'conferentiën' in content:
            types['treaty_conference'] += 1
        else:
            types['residency_letter'] += 1

    print("Corpus classification counts:")
    for k, v in types.items():
        print(f"  {k:20s}: {v}")

if __name__ == '__main__':
    analyze_corpus()
