"""Domain model for Video"""
from dataclasses import dataclass, field, asdict
from pathlib import Path
from typing import Optional
from datetime import datetime


@dataclass
class VideoMetadata:
    """Metadata for a video"""
    path: Path
    status: str = "normal"  # normal, liked, disliked
    position: float = 0.0  # 0.0 to 1.0
    speed: float = 1.0
    last_played: Optional[str] = None
    repeat: bool = False
    custom_data: dict = field(default_factory=dict)
    
    def to_dict(self) -> dict:
        """Convert to dictionary for serialization"""
        data = asdict(self)
        data['path'] = str(data['path'])
        return data
    
    @classmethod
    def from_dict(cls, data: dict, path: Optional[Path] = None) -> 'VideoMetadata':
        """Create from dictionary"""
        data = data.copy()
        if 'path' in data and isinstance(data['path'], str):
            data['path'] = Path(data['path'])
        elif path:
            data['path'] = path
        elif 'path' not in data:
            data['path'] = Path("")
        return cls(**data)
    
    def is_liked(self) -> bool:
        return self.status == "liked"
    
    def is_disliked(self) -> bool:
        return self.status == "disliked"
    
    def is_normal(self) -> bool:
        return self.status == "normal"


@dataclass
class Video:
    """Domain model for a video file"""
    path: Path
    metadata: VideoMetadata = field(default_factory=lambda: VideoMetadata(Path("")))
    
    def __post_init__(self):
        if not self.metadata.path:
            self.metadata.path = self.path
    
    @property
    def name(self) -> str:
        """Get video name without extension"""
        return self.path.stem
    
    @property
    def exists(self) -> bool:
        """Check if video file exists"""
        return self.path.exists()
    
    def set_status(self, status: str) -> None:
        """Set rating status"""
        if status not in ("normal", "liked", "disliked"):
            raise ValueError(f"Invalid status: {status}")
        self.metadata.status = status
    
    def update_position(self, position: float) -> None:
        """Update playback position (0.0 to 1.0)"""
        self.metadata.position = max(0.0, min(1.0, position))
    
    def mark_played(self) -> None:
        """Mark video as played"""
        self.metadata.last_played = datetime.now().isoformat()
