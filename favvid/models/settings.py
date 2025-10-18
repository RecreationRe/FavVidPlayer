"""Application settings model"""
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Optional


@dataclass
class AppSettings:
    """Application settings"""
    # Playback
    volume: int = 50
    persist_volume: bool = True
    persist_position: bool = True
    
    # Seek intervals
    small_seek_seconds: float = 5.0
    large_seek_seconds: float = 30.0
    
    # UI
    pin_playlist: bool = False
    file_explorer_mode: bool = False
    last_folder: Optional[str] = None
    
    # Features
    auto_next_enabled: bool = True
    repeat_enabled: bool = False
    shuffle_enabled: bool = False
    
    def to_dict(self) -> dict:
        """Convert to dictionary"""
        return {k: v for k, v in self.__dict__.items()}
    
    @classmethod
    def from_dict(cls, data: dict) -> 'AppSettings':
        """Create from dictionary"""
        return cls(**{k: v for k, v in data.items() if k in cls.__dataclass_fields__})
