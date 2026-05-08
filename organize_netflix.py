"""
organize_netflix.py — CLI alternative to index.html
Reads NetflixViewingHistory.csv and writes a dark-themed HTML report.
No dependencies beyond the Python standard library.
"""

import csv
import html as _html
import os
import re
from collections import defaultdict
from datetime import datetime

INPUT_FILE  = 'NetflixViewingHistory.csv'
OUTPUT_FILE = 'Netflix_History_Organized.html'

SERIES_KEYWORDS = ['season', 'chapter', 'volume', 'part', 'limited series']


# ── Helpers ──────────────────────────────────────────────────────────────────

def parse_date(s):
    try:
        return datetime.strptime(s, '%m/%d/%y')
    except ValueError:
        return datetime.min


def latest_ts(dates):
    return max((int(parse_date(d).timestamp()) for d in dates), default=0)


def best_date(dates):
    if not dates:
        return '—'
    winner = max(dates, key=parse_date)
    dt = parse_date(winner)
    return dt.strftime('%b %d, %Y') if dt != datetime.min else winner


def extract_season(show, full_title):
    rem = full_title[len(show):].lstrip(': -') if full_title.startswith(show) else full_title
    m = re.match(r'((Season|Part|Volume|Series|Chapter)\s+\d+)', rem, re.IGNORECASE)
    if m:
        return m.group(1).title()
    if 'limited series' in rem.lower():
        return 'Limited Series'
    return 'Other'


def season_sort_key(name):
    nums = re.findall(r'\d+', name)
    return int(nums[0]) if nums else 999


def e(s):
    return _html.escape(str(s))


# ── Main ─────────────────────────────────────────────────────────────────────

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: '{INPUT_FILE}' not found in the current directory.")
        return

    rows = []
    with open(INPUT_FILE, encoding='utf-8-sig') as f:
        for row in csv.DictReader(f):
            row = {k.strip(): v for k, v in row.items()}
            if 'Title' in row:
                rows.append(row)

    if not rows:
        print('No data found in CSV.')
        return

    # Identify series roots
    root_sets = defaultdict(set)
    for row in rows:
        root = row['Title'].split(':')[0].strip()
        root_sets[root].add(row['Title'])

    series_roots = set()
    for root, titles in root_sets.items():
        if len(titles) > 1 or any(k in list(titles)[0].lower() for k in SERIES_KEYWORDS):
            series_roots.add(root)

    # Categorise rows
    movies = defaultdict(list)
    series = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for row in rows:
        title     = row['Title']
        date      = row.get('Date', '')
        root      = title.split(':')[0].strip()
        is_series = root in series_roots or any(k in title.lower() for k in SERIES_KEYWORDS)

        if is_series:
            series[root][extract_season(root, title)][title].append(date)
        else:
            movies[title].append(date)

    print(f'Found {len(movies)} movies and {len(series)} series.')
    print('Generating HTML…')

    out = []
    w = out.append

    # ── Head ─────────────────────────────────────────────────────────────────
    w(f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>Netflix Viewing History</title>
<style>
  :root{{--bg:#141414;--s:#1f1f1f;--s2:#2a2a2a;--b:#333;--r:#e50914;--t:#e5e5e5;--td:#888}}
  *{{box-sizing:border-box;margin:0;padding:0}}
  body{{font-family:'Segoe UI',system-ui,sans-serif;background:var(--bg);color:var(--t);padding-bottom:60px}}
  a{{color:var(--r)}}
  header{{background:#0a0a0a;border-bottom:1px solid var(--b);padding:13px 28px;
          display:flex;align-items:center;gap:14px;position:sticky;top:0;z-index:10}}
  .logo{{font-size:1.8rem;font-weight:900;color:var(--r);letter-spacing:-2px}}
  header h1{{font-size:1.05rem;font-weight:600;color:var(--t)}}
  .wrap{{max-width:1040px;margin:0 auto;padding:24px 20px}}
  #q{{width:100%;background:var(--s);border:1px solid var(--b);border-radius:6px;
      padding:11px 16px;color:var(--t);font-size:.95rem;margin-bottom:24px}}
  #q:focus{{outline:none;border-color:var(--r)}}
  .sec{{margin-bottom:40px}}
  h2{{font-size:1.05rem;font-weight:700;margin-bottom:12px}}
  .cnt{{color:var(--td);font-size:.8em;font-weight:400}}
  .srow{{display:flex;gap:6px;margin-bottom:12px;flex-wrap:wrap;align-items:center}}
  .srow span{{color:var(--td);font-size:.82rem}}
  .sb{{background:var(--s);border:1px solid var(--b);color:var(--td);
       padding:5px 12px;border-radius:4px;font-size:.8rem;cursor:pointer}}
  .sb.on{{border-color:var(--r);color:var(--t);background:var(--s2)}}
  table.tbl{{width:100%;border-collapse:collapse;background:var(--s);
             border:1px solid var(--b);border-radius:8px;overflow:hidden}}
  .tbl th{{background:var(--s2);padding:10px 16px;text-align:left;font-size:.78rem;
           color:var(--td);text-transform:uppercase;letter-spacing:.06em;cursor:pointer;user-select:none}}
  .tbl th:hover{{color:var(--t)}}
  .tbl td{{padding:10px 16px;border-top:1px solid var(--b);font-size:.9rem}}
  .tbl tr:hover td{{background:rgba(255,255,255,.025)}}
  details.show{{background:var(--s);border:1px solid var(--b);border-radius:8px;margin-bottom:6px}}
  details.show>summary{{padding:13px 16px;cursor:pointer;list-style:none;
                        font-weight:600;font-size:.95rem;display:flex;align-items:center;gap:10px}}
  details.show>summary::-webkit-details-marker{{display:none}}
  details.show>summary:hover{{background:rgba(255,255,255,.02)}}
  .show-body{{padding:4px 16px 16px}}
  details.ssn{{border-left:2px solid var(--r);border-radius:0 4px 4px 0;margin-bottom:6px}}
  details.ssn>summary{{padding:8px 12px;cursor:pointer;list-style:none;
                       font-size:.86rem;font-weight:600;color:var(--td);display:flex;gap:8px}}
  details.ssn>summary::-webkit-details-marker{{display:none}}
  details.ssn>summary:hover{{color:var(--t)}}
  table.eps{{width:100%;border-collapse:collapse;font-size:.84rem;margin-top:4px}}
  .eps td{{padding:5px 12px;border-top:1px solid rgba(255,255,255,.05);color:var(--td)}}
  .eps td:first-child{{color:var(--t);font-weight:500}}
  .eps tr:hover td{{background:rgba(255,255,255,.02)}}
  .dt{{text-align:right;white-space:nowrap;font-size:.8rem}}
  .rw{{color:var(--r);font-size:.74rem;font-weight:700;margin-left:4px}}
  .hidden{{display:none!important}}
</style>
</head>
<body>
<header>
  <div class="logo">N</div>
  <h1>Netflix Viewing History</h1>
</header>
<div class="wrap">
<input type="search" id="q" placeholder="🔍  Search titles…" oninput="doSearch()">
""")

    # ── Movies ───────────────────────────────────────────────────────────────
    w(f'<div class="sec"><h2>🎬 Movies <span class="cnt">({len(movies)})</span></h2>')
    w('<div class="srow"><span>Sort:</span>')
    w('<button class="sb on" onclick="sortTbl(\'mt\',0,\'s\',this)">Title</button>')
    w('<button class="sb" onclick="sortTbl(\'mt\',1,\'n\',this)">Last Watched</button>')
    w('<button class="sb" onclick="sortTbl(\'mt\',2,\'n\',this)">Times Watched</button>')
    w('</div>')
    w('<table class="tbl"><thead><tr>'
      '<th>Title</th><th>Last Watched</th><th>Times Watched</th>'
      '</tr></thead><tbody id="mt">')

    for title in sorted(movies):
        dates = movies[title]
        w(f'<tr class="mrow">'
          f'<td data-s="{e(title).lower()}">{e(title)}</td>'
          f'<td data-s="{latest_ts(dates)}">{best_date(dates)}</td>'
          f'<td data-s="{len(dates)}">{len(dates)}×</td>'
          f'</tr>')

    w('</tbody></table></div>')

    # ── Series ───────────────────────────────────────────────────────────────
    w(f'<div class="sec"><h2>📺 Series <span class="cnt">({len(series)})</span></h2>')
    w('<div class="srow"><span>Sort:</span>')
    w('<button class="sb on" onclick="sortShows(\'name\',this)">Name</button>')
    w('<button class="sb" onclick="sortShows(\'ts\',this)">Last Watched</button>')
    w('</div><div id="sc">')

    for show in sorted(series):
        seasons   = series[show]
        total_eps = sum(len(ep_map) for ep_map in seasons.values())
        all_dates = [d for s in seasons.values() for ep in s.values() for d in ep]
        ts        = latest_ts(all_dates)

        w(f'<details class="show srow" data-name="{e(show).lower()}" data-ts="{ts}">')
        w(f'<summary>{e(show)} <span class="cnt">({total_eps} eps)</span></summary>')
        w('<div class="show-body">')

        for season_name in sorted(seasons, key=season_sort_key):
            ep_map = seasons[season_name]
            w(f'<details class="ssn"><summary>{e(season_name)} '
              f'<span class="cnt">({len(ep_map)} ep)</span></summary>'
              f'<table class="eps"><tbody>')

            for full_title, dates in ep_map.items():
                label = full_title
                if label.startswith(show):
                    label = label[len(show):].lstrip(': -')
                if season_name.lower() in label.lower():
                    label = re.sub(re.escape(season_name), '', label, flags=re.IGNORECASE).lstrip(': -')
                if len(label) < 2:
                    label = full_title
                rewatch = f' <span class="rw">{len(dates)}×</span>' if len(dates) > 1 else ''
                w(f'<tr><td>{e(label)}{rewatch}</td><td class="dt">{best_date(dates)}</td></tr>')

            w('</tbody></table></details>')

        w('</div></details>')

    # ── Script ───────────────────────────────────────────────────────────────
    w("""</div></div>
</div><!-- /wrap -->
<script>
'use strict';
const _d = {};
function sortTbl(id, col, type, btn) {
  const tbody = document.getElementById(id);
  const rows  = [...tbody.querySelectorAll('tr.mrow')];
  const key   = id + col;
  _d[key]     = _d[key] === 1 ? -1 : 1;
  rows.sort((a, b) => {
    const va = a.children[col].dataset.s;
    const vb = b.children[col].dataset.s;
    return type === 'n' ? _d[key] * (va - vb) : _d[key] * va.localeCompare(vb);
  });
  rows.forEach(r => tbody.appendChild(r));
  if (btn) { document.querySelectorAll('#mt ~ .srow .sb, .srow .sb').forEach(b => b.classList.remove('on')); btn.classList.add('on'); }
}

const _sd = {};
function sortShows(by, btn) {
  const c     = document.getElementById('sc');
  const items = [...c.querySelectorAll('details.show')];
  const key   = by;
  _sd[key]    = _sd[key] === 1 ? -1 : 1;
  items.sort((a, b) =>
    by === 'ts' ? _sd[key] * (b.dataset.ts - a.dataset.ts)
                : _sd[key] * a.dataset.name.localeCompare(b.dataset.name)
  );
  items.forEach(i => c.appendChild(i));
  if (btn) { btn.closest('.srow').querySelectorAll('.sb').forEach(b => b.classList.remove('on')); btn.classList.add('on'); }
}

function doSearch() {
  const q = document.getElementById('q').value.toLowerCase().trim();
  document.querySelectorAll('tr.mrow').forEach(el => {
    el.classList.toggle('hidden', !!q && !el.children[0].dataset.s.includes(q));
  });
  document.querySelectorAll('details.show').forEach(el => {
    el.classList.toggle('hidden', !!q && !el.dataset.name.includes(q));
  });
}
</script>
</body>
</html>""")

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write('\n'.join(out))

    print(f"Done! Open '{OUTPUT_FILE}' in your browser.")


if __name__ == '__main__':
    main()
