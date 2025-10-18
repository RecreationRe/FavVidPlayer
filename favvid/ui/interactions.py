"""Video frame interactions (clicks, double-clicks, mouse wheel)"""
from PyQt5 import QtWidgets, QtCore
from .video_overlay import VideoOverlay


class VideoInteractionsManager:
    """Manages video frame mouse and keyboard interactions"""
    
    def __init__(self, parent):
        """Initialize interactions manager"""
        self.parent = parent
        self.overlay = None
    
    def setup(self):
        """Setup video frame event handlers with overlay"""
        # Create overlay on top of video frame
        self.overlay = VideoOverlay(self.parent.video_frame)
        self.overlay.setGeometry(self.parent.video_frame.rect())
        
        # Connect overlay signals
        self.overlay.single_clicked.connect(self.parent.toggle_play_pause)
        self.overlay.double_clicked.connect(self.parent.toggle_fullscreen)
        self.overlay.wheel_scrolled.connect(self._on_wheel_scrolled)
    
    def _on_wheel_scrolled(self, delta):
        """Handle mouse wheel - adjust volume"""
        if delta > 0:
            self.parent.volume_up()
        else:
            self.parent.volume_down()

