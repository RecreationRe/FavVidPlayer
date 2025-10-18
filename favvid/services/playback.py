"""Playback service"""
from pathlib import Path
from typing import Optional
from ..models import Video
from ..player import VLCPlayer


class PlaybackService:
    """Service for managing video playback"""
    
    def __init__(self, video_widget):
        self.player = VLCPlayer(video_widget)
        self.current_video: Optional[Video] = None
    
    def play(self, video: Video) -> bool:
        """Play a video"""
        if not video.exists:
            return False
        
        self.player.play(video.path)
        self.current_video = video
        return True
    
    def pause(self) -> None:
        """Pause playback"""
        self.player.pause()
    
    def resume(self) -> None:
        """Resume playback"""
        if self.player.player:
            self.player.player.play()
    
    def toggle_pause(self) -> None:
        """Toggle pause/play"""
        if self.is_playing():
            self.pause()
        else:
            self.resume()
    
    def stop(self) -> None:
        """Stop playback"""
        self.player.stop()
        self.current_video = None
    
    def is_playing(self) -> bool:
        """Check if currently playing"""
        return self.player.is_playing()
    
    def set_position(self, position: float) -> None:
        """Set playback position (0.0 to 1.0)"""
        self.player.set_position(position)
    
    def get_position(self) -> float:
        """Get current position (0.0 to 1.0)"""
        return self.player.get_position()
    
    def set_volume(self, volume: int) -> None:
        """Set volume (0-100)"""
        self.player.set_volume(volume)
    
    def set_speed(self, speed: float) -> None:
        """Set playback speed"""
        self.player.set_rate(speed)
    
    def get_time(self) -> int:
        """Get current time in milliseconds"""
        return self.player.get_time()
    
    def get_length(self) -> int:
        """Get total length in milliseconds"""
        return self.player.get_length()
    
    def seek_forward(self, seconds: float) -> None:
        """Seek forward by specified seconds"""
        current_time = self.get_time() / 1000.0  # Convert to seconds
        total_time = self.get_length() / 1000.0
        if total_time > 0:
            new_time = min(total_time, current_time + seconds)
            new_position = new_time / total_time
            self.set_position(new_position)
    
    def seek_backward(self, seconds: float) -> None:
        """Seek backward by specified seconds"""
        current_time = self.get_time() / 1000.0  # Convert to seconds
        total_time = self.get_length() / 1000.0
        if total_time > 0:
            new_time = max(0, current_time - seconds)
            new_position = new_time / total_time
            self.set_position(new_position)
    
    def toggle_fullscreen(self) -> None:
        """Toggle fullscreen"""
        # This is handled by the UI layer
        pass

