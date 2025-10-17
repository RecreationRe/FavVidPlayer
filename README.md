FavVidPlayer

A lightweight desktop video organizer/player built with PyQt5 and python-vlc.

Features
- Select a folder and recursively scan for video files (mp4, mkv, avi, webm, gif, etc.)
- Playlist panel on the right that auto-hides and reveals when the mouse is near the right edge
- Single-click a playlist entry to play
- Like (green), Dislike (red), and Normal (blue) buttons to tag videos
- A Favorites folder (Favorites_FavVidPlayer) is created inside the selected root. Liked videos are hardlinked into that folder; if hardlinking fails (cross-device), the file is copied.
- Metadata persisted in `.favmeta.json` at the selected root mapping relative paths to status, last_played, speed, repeat

Quick start
1. Create a virtualenv and install dependencies:

```powershell
python -m venv .venv; .\.venv\Scripts\Activate.ps1; pip install -r requirements.txt
```

2. Run:

```powershell
python main.py
```

Notes
- Requires VLC installed on the system. Ensure the libvlc DLLs are in PATH or install VLC.
- This is an initial prototype. Improvements: file-watching, better error handling, UI polish, tests.
