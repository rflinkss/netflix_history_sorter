import csv
import html
import os
import re
from collections import defaultdict
from datetime import datetime

# --- CONFIGURATION ---
INPUT_FILE = 'NetflixViewingHistory.csv'
OUTPUT_FILE = 'Netflix_History_Organized.html'

def extract_season(show_name, full_title):
    if full_title.startswith(show_name):
        remainder = full_title[len(show_name):].strip(': -')
    else:
        remainder = full_title

    match = re.match(r'((Season|Part|Volume|Series|Chapter)\s+\d+)', remainder, re.IGNORECASE)
    if match:
        return match.group(1).title()
    if "Limited Series" in remainder:
        return "Limited Series"
    return "Other"

def parse_date(date_str):
    """
    Parses 'M/D/YY' into a datetime object for sorting.
    Returns datetime.min if invalid.
    """
    try:
        return datetime.strptime(date_str, "%m/%d/%y")
    except ValueError:
        return datetime.min

def get_latest_date_timestamp(dates_list):
    """
    Given a list of date strings, returns the timestamp of the most recent one.
    Used for sorting HTML elements.
    """
    best_ts = 0
    for d_str in dates_list:
        dt = parse_date(d_str)
        ts = dt.timestamp()
        if ts > best_ts:
            best_ts = ts
    return int(best_ts)

def main():
    if not os.path.exists(INPUT_FILE):
        print(f"Error: Could not find '{INPUT_FILE}'.")
        input("Press Enter to exit...")
        return

    print("Reading Netflix History...")
    rows = []
    try:
        with open(INPUT_FILE, 'r', encoding='utf-8-sig') as f:
            reader = csv.DictReader(f)
            for row in reader:
                clean_row = {k.strip(): v for k, v in row.items()}
                if 'Title' in clean_row:
                    rows.append(clean_row)
    except Exception as e:
        print(f"Error reading file: {e}")
        return

    # --- IDENTIFY SERIES ---
    titles_by_root = defaultdict(set)
    for row in rows:
        t = row['Title']
        root = t.split(':')[0] if ':' in t else t
        titles_by_root[root].add(t)
    
    series_roots = set()
    keywords = ['Season', 'Chapter', 'Volume', 'Part', 'Limited Series', 'Series']
    for root, titles in titles_by_root.items():
        if len(titles) > 1:
            series_roots.add(root)
        else:
            if any(k in list(titles)[0] for k in keywords):
                series_roots.add(root)

    # --- ORGANIZE DATA ---
    movies_map = defaultdict(list)
    series_map = defaultdict(lambda: defaultdict(lambda: defaultdict(list)))

    for row in rows:
        title = row['Title']
        date = row.get('Date', '')
        root = title.split(':')[0] if ':' in title else title
        is_series = False
        show_name = root

        if root in series_roots:
            is_series = True
        elif any(k in title for k in keywords):
            is_series = True
            if ':' in title: show_name = title.split(':')[0]

        if is_series:
            season = extract_season(show_name, title)
            series_map[show_name][season][title].append(date)
        else:
            movies_map[title].append(date)

    print(f"Found {len(movies_map)} movies and {len(series_map)} series.")
    print("Generating HTML...")

    # --- GENERATE HTML ---
    html_content = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Netflix Viewing History</title>
    <style>
        body { font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif; padding: 20px; max-width: 1000px; margin: 0 auto; background-color: #fcfcfc; color: #333; }
        h1 { color: #e50914; border-bottom: 2px solid #eee; padding-bottom: 10px; }
        input.search { width: 100%; padding: 12px; font-size: 16px; margin-bottom: 20px; border: 1px solid #ddd; border-radius: 4px; box-sizing: border-box; }
        
        /* Sort Controls */
        .sort-controls { margin-bottom: 15px; }
        .sort-btn { background: #eee; border: none; padding: 8px 12px; border-radius: 4px; cursor: pointer; font-size: 0.9em; margin-right: 5px; }
        .sort-btn:hover { background: #ddd; }
        .sort-btn.active { background: #e50914; color: white; }

        /* Tables */
        table { width: 100%; border-collapse: collapse; background: white; margin-bottom: 10px; font-size: 0.95em; border: 1px solid #eee; }
        th { background: #f4f4f4; text-align: left; padding: 10px; border-bottom: 2px solid #ddd; cursor: pointer; user-select: none; }
        th:hover { background: #e0e0e0; }
        td { border-bottom: 1px solid #eee; padding: 10px; vertical-align: top; }
        tr:hover { background: #fafafa; }
        
        th.sort-asc::after { content: " ▲"; font-size: 0.8em; }
        th.sort-desc::after { content: " ▼"; font-size: 0.8em; }

        /* Series List */
        details { background: white; border: 1px solid #e0e0e0; border-radius: 4px; margin-bottom: 5px; }
        summary { padding: 12px; cursor: pointer; font-weight: 600; list-style: none; position: relative; }
        summary:hover { background: #f8f8f8; }
        summary::-webkit-details-marker { display: none; }
        summary:after { content: "+"; position: absolute; right: 15px; color: #999; font-weight: bold; }
        details[open] > summary:after { content: "-"; }
        
        .season-details { margin: 10px 10px 10px 20px; border-left: 3px solid #e50914; }
        .season-summary { font-size: 0.95em; color: #555; }
        .count { color: #888; font-size: 0.8em; font-weight: normal; margin-left: 5px; }
    </style>
    <script>
    function filterList() {
        var input = document.getElementById("search");
        var filter = input.value.toUpperCase();
        var items = document.querySelectorAll(".item-row");
        items.forEach(item => {
            var txt = item.textContent || item.innerText;
            item.style.display = txt.toUpperCase().indexOf(filter) > -1 ? "" : "none";
        });
    }

    function sortTable(tableId, colIndex, type) {
        var table = document.getElementById(tableId);
        var tbody = table.querySelector("tbody");
        var rows = Array.from(tbody.querySelectorAll("tr"));
        var th = table.querySelectorAll("th")[colIndex];
        
        // Determine order
        var order = th.classList.contains("sort-asc") ? "desc" : "asc";
        
        // Reset Headers
        table.querySelectorAll("th").forEach(h => h.classList.remove("sort-asc", "sort-desc"));
        th.classList.add(order === "asc" ? "sort-asc" : "sort-desc");

        rows.sort((a, b) => {
            var valA = a.children[colIndex].getAttribute("data-sort");
            var valB = b.children[colIndex].getAttribute("data-sort");
            
            if (type === 'num') {
                return order === "asc" ? valA - valB : valB - valA;
            } else {
                return order === "asc" ? valA.localeCompare(valB) : valB.localeCompare(valA);
            }
        });
        
        rows.forEach(row => tbody.appendChild(row));
    }

    function sortSeries(criteria) {
        var container = document.getElementById("series-container");
        var items = Array.from(container.children);
        
        // Toggle active button style
        document.querySelectorAll(".series-sort-btn").forEach(btn => btn.classList.remove("active"));
        event.target.classList.add("active");

        items.sort((a, b) => {
            var valA = a.getAttribute(criteria);
            var valB = b.getAttribute(criteria);
            
            if (criteria === 'data-date') {
                // Default date sort is Newest First (Desc)
                return valB - valA;
            } else {
                // Default name sort is A-Z (Asc)
                return valA.localeCompare(valB);
            }
        });
        
        items.forEach(item => container.appendChild(item));
    }
    </script>
    </head>
    <body>
    <h1>Netflix Viewing History</h1>
    <input type="text" id="search" class="search" onkeyup="filterList()" placeholder="Search titles...">
    
    <h2>Movies <span class="count">(""" + str(len(movies_map)) + """)</span></h2>
    <p style="font-size:0.9em; color:#666;">Click headers to sort.</p>
    <table id="movieTable">
        <thead>
            <tr>
                <th onclick="sortTable('movieTable', 0, 'str')">Title</th>
                <th onclick="sortTable('movieTable', 1, 'num')">Last Watched</th>
            </tr>
        </thead>
        <tbody>
    """
    
    # Sort Movies by Name initially
    sorted_movies = sorted(movies_map.keys())
    for title in sorted_movies:
        dates = movies_map[title]
        dates_str = ", ".join(dates)
        
        # Calculate timestamps for sorting
        latest_ts = get_latest_date_timestamp(dates)
        
        html_content += f"""
        <tr class="item-row">
            <td data-sort="{html.escape(title).lower()}">{html.escape(title)}</td>
            <td data-sort="{latest_ts}">{dates_str}</td>
        </tr>
        """
        
    html_content += f"""
        </tbody>
    </table>
    
    <h2>Series <span class="count">(""" + str(len(series_map)) + """)</span></h2>
    <div class="sort-controls">
        <button class="sort-btn series-sort-btn active" onclick="sortSeries('data-name')">Name (A-Z)</button>
        <button class="sort-btn series-sort-btn" onclick="sortSeries('data-date')">Last Watched (Newest)</button>
    </div>
    
    <div id="series-container">
    """
    
    sorted_series = sorted(series_map.keys())
    for show in sorted_series:
        seasons = series_map[show]
        total_unique_eps = sum(len(ep_map) for ep_map in seasons.values())
        
        # Calculate latest watch date for the entire show
        all_show_dates = []
        for s in seasons.values():
            for d_list in s.values():
                all_show_dates.extend(d_list)
        latest_show_ts = get_latest_date_timestamp(all_show_dates)
        
        html_content += f"""
        <details class="item-row" data-name="{html.escape(show).lower()}" data-date="{latest_show_ts}">
            <summary>
                {html.escape(show)} 
                <span class="count">({total_unique_eps} unique eps)</span>
            </summary>
            <div style="padding: 5px;">
        """
        
        # Sort Seasons
        def season_sort_key(s_name):
            nums = re.findall(r'\d+', s_name)
            if nums: return int(nums[0])
            return 999 
            
        sorted_seasons = sorted(seasons.keys(), key=season_sort_key)
        
        for season_name in sorted_seasons:
            episodes_map = seasons[season_name]
            html_content += f"""
            <details class="season-details">
                <summary class="season-summary">{season_name} <span class="count">({len(episodes_map)})</span></summary>
                <table>
                    <thead><tr><th>Episode</th><th>Dates Watched</th></tr></thead>
                    <tbody>
            """
            
            for full_title, dates in episodes_map.items():
                dates_str = ", ".join(dates)
                
                disp = full_title
                if disp.startswith(show): disp = disp[len(show):].strip(': -')
                if season_name in disp: disp = disp.replace(season_name, '').strip(': -')
                if len(disp) < 2: disp = full_title
                
                html_content += f"<tr><td>{html.escape(disp)}</td><td>{dates_str}</td></tr>"
            
            html_content += "</tbody></table></details>"
            
        html_content += "</div></details>"

    html_content += "</div></body></html>"
    
    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        f.write(html_content)
        
    print(f"Success! Open '{OUTPUT_FILE}' to see your list.")

if __name__ == "__main__":
    main()