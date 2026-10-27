import re
import html

with open('39_Expanded_Keyword_Index.md', 'r', encoding='utf-8') as f:
    lines = f.readlines()

entries = []
current_section = 'General'

for line in lines:
    l = line.strip()
    if l.startswith('## ') or l.startswith('### '):
        sec = l.replace('#', '').strip()
        # Clean section names
        sec = re.sub(r'^\d+\.\s*', '', sec)
        sec = re.sub(r'\s*\(Appendix.*?\)', '', sec)
        current_section = sec
        continue
    
    # Bullet item like: *   **Term**: Description
    m = re.match(r'^\*\s+\*\*([^*]+?)\*\*:\s*(.+)$', l)
    if m:
        term, desc = m.group(1).strip(), m.group(2).strip()
        entries.append((current_section, term, desc))
        continue
        
    # Sub-item like:     *   *Term* (Description)
    m2 = re.match(r'^\*\s+\*([^*]+?)\*(?:\s*[-:]|\s*\((.+)\)|\s*(.+))?$', l)
    if m2:
        term = m2.group(1).strip()
        desc = (m2.group(2) or m2.group(3) or '').strip()
        if not desc and len(term) > 3:
            desc = current_section
        entries.append((current_section, term, desc))
        continue

# Build HTML
categories = sorted(list(set(e[0] for e in entries)))

html_out = """<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <meta http-equiv="Cache-Control" content="no-cache, no-store, must-revalidate">
    <meta http-equiv="Pragma" content="no-cache">
    <meta http-equiv="Expires" content="0">
    <title>Keyword & Terminology Dictionary — 1792-1809 Yogyakarta Residency Letters</title>
    <style>
        :root {
            --bg: #1a1a1a;
            --panel: #222222;
            --panel-alt: #2d2d2d;
            --fg: #e0e0e0;
            --muted: #9a9a9a;
            --line: #333333;
            --accent: #4a9eff;
        }
        * { box-sizing: border-box; }
        body {
            background-color: var(--bg);
            color: var(--fg);
            font-family: Arial, sans-serif;
            max-width: 1200px;
            margin: 0 auto;
            padding: 20px;
            line-height: 1.6;
        }
        .topbar {
            display: flex;
            gap: 10px;
            border-bottom: 1px solid var(--line);
            padding-bottom: 15px;
            margin-bottom: 25px;
            flex-wrap: wrap;
            align-items: center;
        }
        .btn {
            background: var(--panel-alt);
            color: var(--fg);
            border: 1px solid var(--line);
            border-radius: 5px;
            padding: 8px 14px;
            text-decoration: none;
            font-size: 0.9rem;
            transition: all 0.2s ease;
        }
        .btn:hover { background: var(--accent); color: #ffffff; }
        h1 { color: #ffffff; margin-top: 0; }
        .controls {
            display: flex;
            gap: 12px;
            margin-bottom: 20px;
            flex-wrap: wrap;
        }
        .search-box {
            flex: 2;
            min-width: 250px;
            background: var(--panel);
            color: var(--fg);
            border: 1px solid #444;
            border-radius: 5px;
            padding: 10px 14px;
            font-size: 0.95rem;
        }
        .search-box:focus {
            outline: none;
            border-color: var(--accent);
        }
        .category-select {
            flex: 1;
            min-width: 200px;
            background: var(--panel);
            color: var(--fg);
            border: 1px solid #444;
            border-radius: 5px;
            padding: 10px 14px;
            font-size: 0.95rem;
            cursor: pointer;
        }
        .stats-bar {
            font-size: 0.88rem;
            color: var(--muted);
            margin-bottom: 15px;
        }
        table {
            width: 100%;
            border-collapse: collapse;
            background: var(--panel);
            border-radius: 6px;
            overflow: hidden;
            border: 1px solid var(--line);
        }
        th, td {
            border: 1px solid var(--line);
            padding: 12px 14px;
            text-align: left;
            vertical-align: top;
        }
        th {
            background-color: var(--panel-alt);
            color: #ffffff;
            font-weight: 600;
        }
        tr:nth-child(even) {
            background-color: rgba(255, 255, 255, 0.02);
        }
        tr:hover {
            background-color: rgba(74, 158, 255, 0.07);
        }
        .tag {
            display: inline-block;
            background: #2a3b4c;
            color: #8bc34a;
            border-radius: 4px;
            padding: 2px 8px;
            font-size: 0.78rem;
            white-space: nowrap;
        }
        .term-title {
            color: #ffffff;
            font-weight: bold;
        }
    </style>
</head>
<body>

    <div class="topbar">
        <a class="btn" href="index.html">← Main Portal</a>
        <a class="btn" href="transcriptions.html">Individual Transcriptions</a>
        <a class="btn" href="full.html">Full Documentation</a>
    </div>

    <h1>Keyword & Terminology Dictionary</h1>
    <p style="color: var(--muted); margin-bottom: 25px;">
        Comprehensive historical glossary of rulers, princely houses, Javanese officials, colonial officers, geographical sites, administrative concepts, and currency units compiled from the Peter Carey Archive.
    </p>

    <div class="controls">
        <input type="text" id="searchInput" class="search-box" placeholder="🔍 Search by term, name, title, place, or concept..." autofocus>
        <select id="categorySelect" class="category-select">
            <option value="">All Categories (488 entries)</option>
"""

for c in categories:
    html_out += f'            <option value="{html.escape(c)}">{html.escape(c)}</option>\n'

html_out += """        </select>
    </div>

    <div class="stats-bar" id="statsBar">
        Showing all entries.
    </div>

    <table>
        <thead>
            <tr>
                <th style="width: 22%;">Category</th>
                <th style="width: 28%;">Standard / Historical Term</th>
                <th style="width: 50%;">Description / Context</th>
            </tr>
        </thead>
        <tbody id="dictionaryBody">
"""

for cat, term, desc in entries:
    html_out += f"""            <tr data-cat="{html.escape(cat)}">
                <td><span class="tag">{html.escape(cat)}</span></td>
                <td class="term-title">{html.escape(term)}</td>
                <td>{html.escape(desc)}</td>
            </tr>\n"""

html_out += """        </tbody>
    </table>

    <script>
        const searchInput = document.getElementById('searchInput');
        const categorySelect = document.getElementById('categorySelect');
        const rows = Array.from(document.querySelectorAll('#dictionaryBody tr'));
        const statsBar = document.getElementById('statsBar');

        function filterTable() {
            const query = searchInput.value.toLowerCase().trim();
            const selectedCat = categorySelect.value;
            let visibleCount = 0;

            rows.forEach(row => {
                const text = row.textContent.toLowerCase();
                const rowCat = row.getAttribute('data-cat');
                
                const matchesQuery = !query || text.includes(query);
                const matchesCat = !selectedCat || rowCat === selectedCat;

                if (matchesQuery && matchesCat) {
                    row.style.display = '';
                    visibleCount++;
                } else {
                    row.style.display = 'none';
                }
            });

            statsBar.textContent = `Showing ${visibleCount} of ${rows.length} entries.`;
        }

        searchInput.addEventListener('input', filterTable);
        categorySelect.addEventListener('change', filterTable);
        filterTable();
    </script>

</body>
</html>
"""

with open('dictionary.html', 'w', encoding='utf-8') as f:
    f.write(html_out)

print("Generated dictionary.html with 488 searchable entries!")
