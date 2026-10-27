import glob
import re

files = glob.glob('transcription/*.md')
count = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        c = fp.read()
    
    if '**Keyword Index Check:**' in c:
        # Strip '**Keyword Index Check:** Verified against ... <br>' or with trailing whitespace
        # Match from '**Keyword Index Check:**' up to either '<br>', '<br><br>', or end of line/phrase
        new_c = re.sub(r'\*\*Keyword Index Check:\*\*[^\n<]+(?:<br>\s*|<br><br>\s*|\n)?', '', c)
        if new_c != c:
            with open(f, 'w', encoding='utf-8') as fp:
                fp.write(new_c)
            count += 1
            print(f"Cleaned legacy check in {f}")

print(f"Total files cleaned: {count}")
