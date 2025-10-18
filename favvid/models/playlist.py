"""Playlist model"""
from dataclasses import dataclass, field
from pathlib import Path
from typing import List, Optional
import random
from .video import Video


@dataclass
class Playlist:
    """Domain model for a playlist"""
    videos: List[Video] = field(default_factory=list)
    _original_order: List[Video] = field(default_factory=list)
    _is_shuffled: bool = False
    
    def add_video(self, video: Video) -> None:
        """Add a video to playlist"""
        if video not in self.videos:
            self.videos.append(video)
    
    def remove_video(self, video: Video) -> None:
        """Remove a video from playlist"""
        if video in self.videos:
            self.videos.remove(video)
        if video in self._original_order:
            self._original_order.remove(video)
    
    def clear(self) -> None:
        """Clear all videos"""
        self.videos.clear()
        self._original_order.clear()
        self._is_shuffled = False
    
    def shuffle(self) -> None:
        """Shuffle the playlist"""
        if not self._is_shuffled:
            self._original_order = self.videos.copy()
            self._is_shuffled = True
            random.shuffle(self.videos)
    
    def unshuffle(self) -> None:
        """Restore original order"""
        if self._is_shuffled and self._original_order:
            self.videos = self._original_order.copy()
            self._is_shuffled = False
    
    def toggle_shuffle(self) -> None:
        """Toggle shuffle mode"""
        if self._is_shuffled:
            self.unshuffle()
        else:
            self.shuffle()
    
    def is_shuffled(self) -> bool:
        """Check if playlist is shuffled"""
        return self._is_shuffled
    
    def filter_by_status(self, status: str) -> List[Video]:
        """Filter videos by rating status"""
        return [v for v in self.videos if v.metadata.status == status]
    
    def search(self, query: str) -> List[Video]:
        """Search videos by name"""
        query_lower = query.lower()
        return [v for v in self.videos if query_lower in v.name.lower()]
    
    def get_next(self, current: Video) -> Optional[Video]:
        """Get next video"""
        try:
            idx = self.videos.index(current)
            if idx < len(self.videos) - 1:
                return self.videos[idx + 1]
        except ValueError:
            pass
        return None
    
    def get_previous(self, current: Video) -> Optional[Video]:
        """Get previous video"""
        try:
            idx = self.videos.index(current)
            if idx > 0:
                return self.videos[idx - 1]
        except ValueError:
            pass
        return None
    
    def __len__(self) -> int:
        return len(self.videos)
    
    def __iter__(self):
        return iter(self.videos)
