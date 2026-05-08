# Netflix History Viewer

Turn your raw Netflix viewing history CSV into a clean, searchable, dark-themed dashboard — directly in your browser. No installs, no servers, no accounts.

![Netflix History Viewer](https://img.shields.io/badge/works%20in-any%20browser-e50914?style=flat-square&logo=google-chrome&logoColor=white)
![No dependencies](https://img.shields.io/badge/dependencies-none-brightgreen?style=flat-square)
![Python](https://img.shields.io/badge/CLI%20alternative-Python%203-3776AB?style=flat-square&logo=python&logoColor=white)

---

## What it does

Netflix gives you a messy CSV with thousands of raw entries. This tool organizes it into:

- **Movies** — searchable, sortable table with watch dates and rewatch counts
- **Series** — collapsible list grouped by show → season → episode
- **IMDB Ratings** — fetched live via the free OMDb API and cached in your browser
- **Stats** — total movies, series, episodes, and views at a glance

Everything runs locally in your browser. Your data never leaves your machine.

---

## Quick Start

### Step 1 — Export your Netflix history

1. Go to **[netflix.com](https://netflix.com)** and sign in
2. Click your profile icon → **Account**
3. Under *Profile & Parental Controls*, click your profile
4. Click **Viewing activity**
5. Scroll to the bottom → **Download all**
6. Netflix emails you (or downloads directly) a file called `NetflixViewingHistory.csv`

### Step 2 — Open the viewer

**Option A — Web app (recommended)**

1. Download or clone this repo
2. Open `index.html` in any modern browser
3. Drag and drop your `NetflixViewingHistory.csv` onto the page

That's it. No Python, no terminal, no setup.

**Option B — Python CLI**

If you prefer generating a static HTML file from the command line:

```bash
# Place NetflixViewingHistory.csv in the same folder, then run:
python organize_netflix.py
# Output: Netflix_History_Organized.html
```

Requires Python 3.6+ and zero external packages.

---

## IMDB Ratings (optional)

To show IMDB ratings next to each title:

1. Get a **free API key** from [omdbapi.com/apikey.aspx](https://www.omdbapi.com/apikey.aspx) (takes ~30 seconds, 1,000 requests/day free)
2. Paste it into the *IMDB Ratings* field on the import screen and click **Save Key**
3. After importing your CSV, click **⭐ Load Ratings** in the top bar

Ratings are cached in your browser's `localStorage` so they don't need to be re-fetched on every visit.

> **Note:** OMDb matches by title, so some Netflix-exclusive or internationally titled shows (e.g. *Money Heist* vs *La casa de papel*) may return N/A.

---

## Features

| Feature | Web App | Python CLI |
|---|---|---|
| Drag-and-drop CSV import | ✅ | — |
| Dark Netflix-themed UI | ✅ | ✅ |
| Movies & Series separated | ✅ | ✅ |
| Search / filter | ✅ | ✅ |
| Sort by name, date, views, rating | ✅ | ✅ |
| Rewatch tracking | ✅ | ✅ |
| IMDB ratings (OMDb) | ✅ | — |
| Season / episode breakdown | ✅ | ✅ |
| Works fully offline | ✅ (after first load) | ✅ |
| Zero dependencies | ✅ | ✅ (stdlib only) |

---

## How it works

The CSV from Netflix has one row per play event, formatted like:

```
Title,Date
"BoJack Horseman: Season 4: Ruthie","4/13/26"
"Hubie Halloween","4/24/26"
```

The tool parses each entry and uses the following logic to separate movies from series:

- If a title's root (everything before the first `:`) appears more than once, it's a series
- If a title contains keywords like *Season*, *Part*, *Chapter*, *Volume*, or *Limited Series*, it's a series
- Everything else is a movie

Episodes are then grouped by show → season → episode title, and the dates are tracked individually so rewatches are visible.

---

## Files

| File | Description |
|---|---|
| `index.html` | Self-contained web app — open this in a browser |
| `organize_netflix.py` | Python CLI alternative — generates a static HTML file |
| `NetflixViewingHistory.csv` | Your exported Netflix data (not included — add your own) |

---

## Contact

Questions or suggestions? Join my Discord:
[**discord.gg/ACrhedSKKC**](https://discord.gg/ACrhedSKKC)