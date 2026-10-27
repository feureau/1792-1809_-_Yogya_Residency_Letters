import glob
import re

files = glob.glob('transcription/*.md')
fixed_files = 0

for f in files:
    with open(f, 'r', encoding='utf-8') as fp:
        lines = fp.readlines()
        
    modified = False
    new_lines = []
    in_2col_table = False
    
    for l_num, line in enumerate(lines):
        l_str = line.strip()
        if l_str == '| :--- | :--- |':
            in_2col_table = True
            new_lines.append(line)
            continue
            
        if in_2col_table:
            if not l_str.startswith('|'):
                in_2col_table = False
                new_lines.append(line)
                continue
                
            # It's a table row in a 2-column table
            # It should have format: | Margin | Main Text |
            # If it has more pipes inside Main Text, escape them!
            parts = line.split('|')
            # parts[0] is before first pipe (empty or whitespace)
            # parts[1] is Margin Notes
            # parts[2:-1] is Main Text (if split by unescaped pipes)
            # parts[-1] is after last pipe (\n)
            if len(parts) > 4:
                margin = parts[1]
                # join parts[2:-1] with escaped pipe \|
                main_text = '\\|'.join(parts[2:-1])
                trailing = parts[-1]
                new_line = f"|{margin}|{main_text}|{trailing}"
                new_lines.append(new_line)
                modified = True
                continue
                
        new_lines.append(line)
        
    if modified:
        with open(f, 'w', encoding='utf-8') as fp:
            fp.writelines(new_lines)
        fixed_files += 1
        print(f"Fixed unescaped pipes in {f}")

print(f"Total files fixed: {fixed_files}")
