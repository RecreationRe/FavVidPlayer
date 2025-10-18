"""Signal handlers for PlayerWindow events"""


class SignalHandlers:
    """Manages all signal handler connections"""
    
    def __init__(self, parent):
        """Initialize signal handlers"""
        self.parent = parent
    
    def setup(self):
        """Setup all signal connections"""
        self.parent.controller.videos_loaded.connect(self._on_videos_loaded)
        self.parent.controller.video_started.connect(self._on_video_started)
    
    def _on_videos_loaded(self, videos):
        """Handle videos loaded signal"""
        self.parent.playlist_mgr.update_view(videos)
        self.parent.status_label.setText(f'Loaded {len(videos)} videos')
    
    def _on_video_started(self, video):
        """Handle video started signal"""
        self.parent.setWindowTitle(f'FavVidPlayer - {video.name}')
        self.parent.status_label.setText(f'Playing: {video.name}')
