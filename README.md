# organise_files.py

A Python script to automatically organize anime episodes and movies into neatly named subfolders, and update each folder's modified time to the latest file inside it.

---

## 🧩 Features

- Moves episodes like:

    [SubsPlease] Series Name - 03v2 (720p) [ABC12345].mkv

  into:

    ./Series Name/[SubsPlease] Series Name - 03v2 (720p) [ABC12345].mkv

- Moves movies like:

    I Want to Eat Your Pancreas (2018) 1080p AV1 Opus [UnAV1Chain].mkv

  into:

    ./I Want to Eat Your Pancreas/[...].mkv

- Automatically creates folders as needed
- Sets each folder’s "last modified" time to the newest file inside it (recursively)
- Works on **Windows**, **Linux (Ubuntu)**, and **macOS**

---

## ✅ Requirements

- Python 3.8+
- No external libraries required (only standard library used)

---

## 🚀 Usage

Run in the current directory:

    python organise_files.py

Or specify a folder path:

    python organise_files.py "/path/to/your/folder"

Examples:

    python organise_files.py "D:\Downloads\Anime"
    python3 organise_files.py ~/Downloads/anime

---

## 🔧 Adding Custom Regex Patterns

You can add more filename formats in the `PATTERNS` list inside the script:

    PATTERNS = [
        re.compile(r"your_regex_here", re.VERBOSE),
    ]

Each pattern should:
- Match the full filename
- Extract the folder name with `(?P<title>...)`

### Example: Match `[Group] Movie_Title_[2023].mp4`

    re.compile(r"""
        ^\s*
        \[[^\]]+\]         # [Group]
        \s*
        (?P<title>.+?)     # Movie_Title
        _\[\d{4}\]         # [2023]
        \.[A-Za-z0-9]+$    # file extension
    """, re.VERBOSE)

Tip: Test your regex at https://regex101.com

---

## 📁 Folder Rules

- Invalid filename characters (like \ / : * ? " < > |) are replaced with `_`
- Leading/trailing spaces in folder names are removed
- Files already present in destination folders are skipped (not overwritten)

---

## 💡 Tips

- You can schedule this to run periodically (e.g., cron job, Task Scheduler)
- Or bind it to a desktop shortcut or context menu for one-click sorting

---

## 🆘 Need Help?

If you have a unique filename structure that isn’t getting matched, just tweak the regex or ask for help!
