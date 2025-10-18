"""Metadata persistence service"""
import json
import shutil
from pathlib import Path
from typing import Dict, Optional
from ..models import Video, VideoMetadata


class MetadataService:
    """Service for persisting and loading video metadata"""
    
    METADATA_FILENAME = '.favmeta.json'
    FAV_FOLDER_NAME = 'Favorites_FavVidPlayer'
    
    def __init__(self, root_folder: Path):
        self.root_folder = Path(root_folder)
        self.metadata_file = self.root_folder / self.METADATA_FILENAME
        self.fav_folder = self.root_folder / self.FAV_FOLDER_NAME
        self._cache: Dict[str, dict] = {}
        self._load_metadata()
    
    def _load_metadata(self) -> None:
        """Load metadata from file"""
        self._cache.clear()
        
        if self.metadata_file.exists():
            try:
                with open(self.metadata_file, 'r', encoding='utf-8') as f:
                    self._cache = json.load(f)
            except (json.JSONDecodeError, IOError):
                pass
    
    def _save_metadata(self) -> None:
        """Save metadata to file"""
        try:
            self.metadata_file.parent.mkdir(parents=True, exist_ok=True)
            with open(self.metadata_file, 'w', encoding='utf-8') as f:
                json.dump(self._cache, f, indent=2, ensure_ascii=False)
        except IOError:
            pass
    
    def get(self, video: Video) -> VideoMetadata:
        """Get metadata for a video"""
        try:
            rel_path = str(video.path.relative_to(self.root_folder))
        except ValueError:
            rel_path = str(video.path)
        
        if rel_path in self._cache:
            return VideoMetadata.from_dict(self._cache[rel_path], path=video.path)
        
        return VideoMetadata(path=video.path)
    
    def set(self, video: Video, metadata: VideoMetadata) -> None:
        """Set metadata for a video"""
        try:
            rel_path = str(video.path.relative_to(self.root_folder))
        except ValueError:
            rel_path = str(video.path)
        
        self._cache[rel_path] = metadata.to_dict()
        self._save_metadata()
    
    def set_status(self, video: Video, status: str) -> None:
        """Set rating status for a video"""
        metadata = self.get(video)
        metadata.set_status(status)
        self.set(video, metadata)
    
    def create_favorite(self, video: Video) -> bool:
        """Add video to favorites folder using hardlink or copy"""
        try:
            self.fav_folder.mkdir(exist_ok=True)
            fav_path = self.fav_folder / video.path.name
            
            # Remove if exists
            if fav_path.exists():
                fav_path.unlink()
            
            # Try hardlink first
            try:
                fav_path.hardlink_to(video.path)
                return True
            except (OSError, NotImplementedError):
                # Fallback to copy
                shutil.copy2(video.path, fav_path)
                return True
        except Exception:
            return False
    
    def remove_favorite(self, video: Video) -> bool:
        """Remove video from favorites folder"""
        try:
            fav_path = self.fav_folder / video.path.name
            if fav_path.exists():
                fav_path.unlink()
            return True
        except Exception:
            return False

