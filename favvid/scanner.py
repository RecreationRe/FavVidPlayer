from pathlib import Path

VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.webm', '.mov', '.flv', '.wmv', '.mpg', '.mpeg', '.gif'}


def scan_videos(root: Path):
    """Recursively scan a root Path for video files and return a sorted list of Path objects."""
    files = []
    for p in root.rglob('*'):
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS:
            files.append(p)
    files.sort()
    return files
