import json
import shutil
import os
from pathlib import Path

META_FILENAME = '.favmeta.json'
FAV_FOLDER_NAME = 'Favorites_FavVidPlayer'


class MetaStore:
    def __init__(self, root: Path):
        self.root = root
        self.meta_path = root / META_FILENAME
        self.fav_dir = root / FAV_FOLDER_NAME
        self.fav_dir.mkdir(exist_ok=True)
        self._data = {}
        self.load()

    def load(self):
        if self.meta_path.exists():
            try:
                with open(self.meta_path, 'r', encoding='utf-8') as f:
                    self._data = json.load(f)
            except Exception:
                self._data = {}
        else:
            self._data = {}

    def save(self):
        try:
            with open(self.meta_path, 'w', encoding='utf-8') as f:
                json.dump(self._data, f, indent=2, ensure_ascii=False)
        except Exception as e:
            raise

    def get(self, rel_path: str):
        return self._data.get(rel_path, {})

    def set(self, rel_path: str, data: dict):
        self._data[rel_path] = data
        self.save()

    def set_status(self, rel_path: str, status: str, src_path: Path):
        m = self._data.setdefault(rel_path, {})
        m['status'] = status
        self.save()
        fav_path = self.fav_dir / src_path.name
        try:
            if status == 'liked':
                if fav_path.exists():
                    fav_path.unlink()
                os.link(str(src_path), str(fav_path))
            else:
                if fav_path.exists():
                    fav_path.unlink()
        except Exception:
            # fallback to copy when hardlinking not possible
            if status == 'liked':
                shutil.copy2(str(src_path), str(fav_path))
            else:
                if fav_path.exists():
                    fav_path.unlink()
