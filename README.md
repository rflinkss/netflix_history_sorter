# Netflix History Sorter

A lightweight Python tool that converts your raw Netflix viewing history into a clean, interactive, and searchable HTML dashboard.

## 📖 About
Downloading your viewing history from Netflix gives you a messy, unorganized CSV file with thousands of rows. This script parses that data and organizes it into a beautiful local webpage where you can sort by movies, series, and even track re-watches.

### How it Works
The code distinguishes between a single entry (one specific time you sat down to watch) and the show as a whole:
* **Episodes:** Individual entries that record every single time you hit play.
* **Series:** The "parent" category that groups all those episodes together.

## ✨ Features
* **Zero Dependencies:** Uses only Python's standard library. No `pip install` required!
* **Smart Sorting:** Sort Movies by title or "Last Watched" date. Sort Series by name or the date you last watched them.
* **Rewatch Tracking:** If you have watched a movie or episode multiple times, it lists **every date** you watched it.
* **Interactive UI:** The generated HTML file includes search bars, clickable headers, and expandable season lists.

## 🚀 How to Use

### 1. Get Your Data
First, you need to request your viewing history from Netflix.
* **[Click here to download your Netflix History](https://help.netflix.com/en/node/101917)**
* Netflix will email you a file named `NetflixViewingHistory.csv`.

### 2. Run the Script
1.  Ensure you have **Python** installed.
2.  Place `NetflixViewingHistory.csv` in the same folder as `organize_netflix.py`.
3.  Open your terminal or command prompt and run:
    ```bash
    python organize_netflix.py
    ```

### 3. View Results
A new file named **`Netflix_History_Organized.html`** will appear in the folder. Open it in any web browser to explore your history!

## ⚠️ Note
Most of this code was written with Gemini. I refined some of it, but I just wanted to push my idea out using this form.

## 📞 Contact
Join my server and message me for any contact reasons:
[**Join Discord Server**](https://discord.gg/ACrhedSKKC)
