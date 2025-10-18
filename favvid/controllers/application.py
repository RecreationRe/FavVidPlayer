"""Application controller - Main orchestrator of app logic and services"""
from pathlib import Path
from PyQt5 import QtCore
from ..models import Video, Playlist
from ..services import VideoScanner, MetadataService, PlaybackService, SettingsService


class ApplicationController(QtCore.QObject):
    """Main application controller - MVC controller orchestrating services and models"""
    
    # Signals for UI updates
    videos_loaded = QtCore.pyqtSignal(list)
    video_started = QtCore.pyqtSignal(object)  # Video object
    playback_state_changed = QtCore.pyqtSignal(bool)  # is_playing
    position_changed = QtCore.pyqtSignal(float)  # position 0.0-1.0
    time_updated = QtCore.pyqtSignal(int, int)  # current_ms, total_ms
    rating_changed = QtCore.pyqtSignal(object, str)  # video, status
    
    def __init__(self):
        super().__init__()
        self.settings_service = SettingsService()
        self.playback_service = None
        self.metadata_service = None
        self.playlist = Playlist()
        self.current_folder = None
        self.is_muted = False
        self.pre_mute_volume = 50
    
    def set_playback_service(self, video_widget) -> None:
        """Initialize playback service"""
        self.playback_service = PlaybackService(video_widget)
    
    def load_folder(self, folder_path: Path) -> None:
        """Load videos from a folder"""
        self.current_folder = Path(folder_path)
        self.metadata_service = MetadataService(self.current_folder)
        
        # Scan videos
        videos = VideoScanner.scan_directory(self.current_folder)
        
        # Load metadata
        for video in videos:
            video.metadata = self.metadata_service.get(video)
        
        # Update playlist
        self.playlist.clear()
        for video in videos:
            self.playlist.add_video(video)
        
        self.settings_service.set('last_folder', str(self.current_folder))
        self.videos_loaded.emit(videos)
    
    def play_video(self, video: Video) -> bool:
        """Play a video"""
        if not self.playback_service:
            return False
        
        success = self.playback_service.play(video)
        if success:
            video.mark_played()
            if self.metadata_service:
                self.metadata_service.set(video, video.metadata)
            
            # Restore playback state (speed, position)
            if video.metadata.speed != 1.0:
                self.playback_service.set_speed(video.metadata.speed)
            if self.settings_service.app_settings.persist_position and video.metadata.position > 0:
                QtCore.QTimer.singleShot(500, lambda: self.playback_service.set_position(video.metadata.position))
            
            self.video_started.emit(video)
        
        return success
    
    def stop_playback(self) -> None:
        """Stop playback"""
        if self.playback_service:
            # Save current position before stopping
            if self.playback_service.current_video and self.metadata_service:
                video = self.playback_service.current_video
                video.metadata.position = self.playback_service.get_position()
                self.metadata_service.set(video, video.metadata)
            self.playback_service.stop()
            self.playback_state_changed.emit(False)
    
    def toggle_play_pause(self) -> None:
        """Toggle play/pause"""
        if self.playback_service:
            self.playback_service.toggle_pause()
            self.playback_state_changed.emit(self.playback_service.is_playing())
    
    def play_next(self) -> None:
        """Play next video"""
        if not self.playback_service or not self.playback_service.current_video:
            return
        
        next_video = self.playlist.get_next(self.playback_service.current_video)
        if next_video:
            self.play_video(next_video)
    
    def play_previous(self) -> None:
        """Play previous video"""
        if not self.playback_service or not self.playback_service.current_video:
            return
        
        prev_video = self.playlist.get_previous(self.playback_service.current_video)
        if prev_video:
            self.play_video(prev_video)
    
    def set_video_position(self, position: float) -> None:
        """Set video position and save"""
        if self.playback_service:
            self.playback_service.set_position(position)
            # Save position if persistence is enabled
            if self.playback_service.current_video and self.metadata_service:
                if self.settings_service.app_settings.persist_position:
                    video = self.playback_service.current_video
                    video.metadata.position = position
                    self.metadata_service.set(video, video.metadata)
            self.position_changed.emit(position)
    
    def seek_forward(self, seconds: float) -> None:
        """Seek forward"""
        if self.playback_service:
            self.playback_service.seek_forward(seconds)
    
    def seek_backward(self, seconds: float) -> None:
        """Seek backward"""
        if self.playback_service:
            self.playback_service.seek_backward(seconds)
    
    def seek_forward_small(self) -> None:
        """Seek forward by small interval"""
        seconds = self.settings_service.app_settings.seek_small_seconds
        self.seek_forward(seconds)
    
    def seek_forward_large(self) -> None:
        """Seek forward by large interval"""
        seconds = self.settings_service.app_settings.seek_large_seconds
        self.seek_forward(seconds)
    
    def seek_backward_small(self) -> None:
        """Seek backward by small interval"""
        seconds = self.settings_service.app_settings.seek_small_seconds
        self.seek_backward(seconds)
    
    def seek_backward_large(self) -> None:
        """Seek backward by large interval"""
        seconds = self.settings_service.app_settings.seek_large_seconds
        self.seek_backward(seconds)
    
    def set_volume(self, volume: int) -> None:
        """Set volume"""
        if self.playback_service:
            self.playback_service.set_volume(volume)
            self.settings_service.app_settings.volume = volume
            if self.settings_service.app_settings.persist_volume:
                self.settings_service.save()
    
    def set_video_speed(self, speed: float) -> None:
        """Set video playback speed"""
        if self.playback_service:
            self.playback_service.set_speed(speed)
            if self.playback_service.current_video and self.metadata_service:
                video = self.playback_service.current_video
                video.metadata.speed = speed
                self.metadata_service.set(video, video.metadata)
    
    def toggle_mute(self) -> None:
        """Toggle mute"""
        if self.is_muted:
            self.set_volume(self.pre_mute_volume)
            self.is_muted = False
        else:
            self.pre_mute_volume = self.settings_service.app_settings.volume
            self.set_volume(0)
            self.is_muted = True
    
    def volume_up(self) -> None:
        """Increase volume"""
        current = self.settings_service.app_settings.volume
        self.set_volume(min(100, current + 5))
    
    def volume_down(self) -> None:
        """Decrease volume"""
        current = self.settings_service.app_settings.volume
        self.set_volume(max(0, current - 5))
    
    def set_video_rating(self, video: Video, status: str) -> None:
        """Set video rating (toggle on/off)"""
        if not self.metadata_service:
            return
        
        current_status = video.metadata.status
        if current_status == status:
            # Toggle off
            video.metadata.status = "normal"
        else:
            # Set new status
            video.metadata.status = status
        
        self.metadata_service.set(video, video.metadata)
        
        # Manage favorites
        if video.metadata.status == "liked":
            self.metadata_service.create_favorite(video)
        else:
            self.metadata_service.remove_favorite(video)
        
        self.rating_changed.emit(video, video.metadata.status)
    
    def toggle_shuffle(self) -> None:
        """Toggle shuffle mode"""
        self.playlist.toggle_shuffle()
        self.settings_service.app_settings.shuffle_enabled = self.playlist.is_shuffled()
        self.settings_service.save()
    
    def enable_shuffle(self) -> None:
        """Enable shuffle mode"""
        if not self.playlist.is_shuffled():
            self.playlist.toggle_shuffle()
            self.settings_service.app_settings.shuffle_enabled = True
            self.settings_service.save()
    
    def disable_shuffle(self) -> None:
        """Disable shuffle mode"""
        if self.playlist.is_shuffled():
            self.playlist.toggle_shuffle()
            self.settings_service.app_settings.shuffle_enabled = False
            self.settings_service.save()
    
    def search_playlist(self, query: str) -> list:
        """Search playlist"""
        return self.playlist.search(query)
    
    def toggle_repeat(self) -> None:
        """Toggle repeat mode"""
        # This would cycle through: off -> one -> all -> off
        current = self.settings_service.app_settings.repeat_mode or 'off'
        modes = {'off': 'one', 'one': 'all', 'all': 'off'}
        new_mode = modes.get(current, 'off')
        self.settings_service.app_settings.repeat_mode = new_mode
        self.settings_service.save()
    
    def get_is_playing(self) -> bool:
        """Get playback state"""
        return self.playback_service.is_playing() if self.playback_service else False
    
    def get_current_time(self) -> int:
        """Get current time in milliseconds"""
        return self.playback_service.get_time() if self.playback_service else 0
    
    def get_total_time(self) -> int:
        """Get total time in milliseconds"""
        return self.playback_service.get_length() if self.playback_service else 0
    
    def get_current_position(self) -> float:
        """Get current position (0.0-1.0)"""
        return self.playback_service.get_position() if self.playback_service else 0.0
