"""Video scanning service"""
from pathlib import Path
from typing import List
from ..models import Video


class VideoScanner:
    """Service for scanning video files"""
    
    # Supported video extensions
    VIDEO_EXTENSIONS = {
        '.mp4', '.mkv', '.avi', '.mov', '.flv', '.wmv',
        '.webm', '.m4v', '.mpg', '.mpeg', '.3gp', '.3g2',
        '.mxf', '.ogv', '.ts', '.m2ts', '.mts', '.vob'
    }
    
    @staticmethod
    def scan_directory(root: Path) -> List[Video]:
        """Recursively scan directory for video files"""
        videos = []
        
        if not root.is_dir():
            return videos
        
        try:
            for item in root.rglob('*'):
                if item.is_file() and item.suffix.lower() in VideoScanner.VIDEO_EXTENSIONS:
                    videos.append(Video(path=item))
        except (PermissionError, OSError):
            pass
        
        # Sort by name for consistency
        return sorted(videos, key=lambda v: v.path.name)
    
    @staticmethod
    def get_video_hierarchy(root: Path) -> dict:
        """Get hierarchical structure of videos by folder"""
        hierarchy = {}
        
        if not root.is_dir():
            return hierarchy
        
        try:
            for item in root.rglob('*'):
                if item.is_file() and item.suffix.lower() in VideoScanner.VIDEO_EXTENSIONS:
                    try:
                        rel_path = item.relative_to(root)
                        parent_dir = rel_path.parent
                        
                        if parent_dir not in hierarchy:
                            hierarchy[parent_dir] = []
                        
                        hierarchy[parent_dir].append(Video(path=item))
                    except ValueError:
                        pass
        except (PermissionError, OSError):
            pass
        
        return hierarchy
