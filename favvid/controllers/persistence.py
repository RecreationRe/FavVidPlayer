"""Persistence controller for managing state and data persistence"""
from pathlib import Path
from PyQt5 import QtCore
from ..models import Video, Playlist, VideoMetadata
from ..services import MetadataService, PlaybackService, SettingsService


class PersistenceController(QtCore.QObject):
    """Coordinates persistence operations between services"""
    
    # Signals
    metadata_saved = QtCore.pyqtSignal(object)  # Video
    position_updated = QtCore.pyqtSignal(object, float)  # Video, position
    favorites_updated = QtCore.pyqtSignal(object, str)  # Video, status
    
    def __init__(self):
        super().__init__()
        self.metadata_service: MetadataService = None
        self.settings_service: SettingsService = SettingsService()
    
    def set_metadata_service(self, metadata_service: MetadataService) -> None:
        """Set the metadata service"""
        self.metadata_service = metadata_service
    
    def save_playback_state(self, video: Video, playback_service: PlaybackService) -> None:
        """Save current playback state for a video"""
        if not self.metadata_service:
            return
        
        metadata = video.metadata
        
        # Update playback position if persist flag is set
        if self.settings_service.app_settings.persist_position:
            metadata.position = playback_service.get_position()
        
        # Save metadata
        self.metadata_service.set(video, metadata)
        self.metadata_saved.emit(video)
    
    def update_video_position(self, video: Video, position: float) -> None:
        """Update and persist video playback position"""
        if not self.metadata_service:
            return
        
        if self.settings_service.app_settings.persist_position:
            video.metadata.position = position
            self.metadata_service.set(video, video.metadata)
            self.position_updated.emit(video, position)
    
    def set_video_rating(self, video: Video, status: str) -> None:
        """Set video rating and manage favorites folder"""
        if not self.metadata_service:
            return
        
        metadata = video.metadata
        
        # Toggle off if already has same status
        if metadata.status == status:
            metadata.status = "normal"
        else:
            metadata.status = status
        
        # Save metadata
        self.metadata_service.set(video, metadata)
        
        # Update favorites folder
        if status == "liked":
            self.metadata_service.create_favorite(video)
        else:
            self.metadata_service.remove_favorite(video)
        
        self.favorites_updated.emit(video, metadata.status)
    
    def set_video_speed(self, video: Video, speed: float) -> None:
        """Set and persist video playback speed"""
        if not self.metadata_service:
            return
        
        metadata = video.metadata
        metadata.speed = speed
        self.metadata_service.set(video, metadata)
    
    def set_video_repeat(self, video: Video, repeat: bool) -> None:
        """Set and persist repeat flag for video"""
        if not self.metadata_service:
            return
        
        metadata = video.metadata
        metadata.repeat = repeat
        self.metadata_service.set(video, metadata)
    
    def restore_playback_state(self, video: Video, playback_service: PlaybackService) -> None:
        """Restore previously saved playback state for a video"""
        metadata = video.metadata
        
        # Restore speed
        if metadata.speed != 1.0:
            playback_service.set_speed(metadata.speed)
        
        # Restore position (with delay for VLC to initialize)
        if self.settings_service.app_settings.persist_position and metadata.position > 0:
            QtCore.QTimer.singleShot(500, lambda: playback_service.set_position(metadata.position))
    
    def save_app_settings(self) -> None:
        """Save application settings"""
        self.settings_service.save()
    
    def load_app_settings(self) -> None:
        """Load application settings"""
        self.settings_service.load()
    
    def get_last_folder(self) -> Path:
        """Get last loaded folder from settings"""
        return self.settings_service.get("last_folder")
    
    def set_last_folder(self, folder: Path) -> None:
        """Save last loaded folder to settings"""
        self.settings_service.set("last_folder", str(folder))
        self.save_app_settings()
    
    def get_volume(self) -> int:
        """Get persisted volume level"""
        return self.settings_service.app_settings.volume
    
    def set_volume(self, volume: int) -> None:
        """Set and persist volume level"""
        if self.settings_service.app_settings.persist_volume:
            self.settings_service.app_settings.volume = volume
            self.save_app_settings()
    
    def get_seek_intervals(self) -> tuple:
        """Get small and large seek intervals in seconds"""
        settings = self.settings_service.app_settings
        return (settings.seek_small_seconds, settings.seek_large_seconds)
    
    def set_seek_intervals(self, small_seconds: float, large_seconds: float) -> None:
        """Set and persist seek intervals"""
        settings = self.settings_service.app_settings
        settings.seek_small_seconds = small_seconds
        settings.seek_large_seconds = large_seconds
        self.save_app_settings()
    
    def get_persist_flags(self) -> tuple:
        """Get persistence flags (persist_position, persist_volume)"""
        settings = self.settings_service.app_settings
        return (settings.persist_position, settings.persist_volume)
    
    def set_persist_flags(self, persist_position: bool, persist_volume: bool) -> None:
        """Set persistence flags"""
        settings = self.settings_service.app_settings
        settings.persist_position = persist_position
        settings.persist_volume = persist_volume
        self.save_app_settings()
