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
        # Store root path in playlist manager
        if videos and hasattr(videos[0].path, 'parent'):
            # Find common root from all videos
            paths = [v.path for v in videos]
            common_root = paths[0].parent
            for p in paths[1:]:
                while not str(p).startswith(str(common_root)):
                    common_root = common_root.parent
            self.parent.playlist_mgr.root_path = common_root
        
        self.parent.playlist_mgr.update_view(videos)
        self.parent.status_label.setText(f'Loaded {len(videos)} videos')
    
    def _on_video_started(self, video):
        """Handle video started signal"""
        self.parent.setWindowTitle(f'FavVidPlayer - {video.name}')
        self.parent.status_label.setText(f'Playing: {video.name}')
