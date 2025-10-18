"""Playlist view management"""
from PyQt5 import QtWidgets, QtCore, QtGui


class PlaylistManager:
    """Manages playlist view and search"""
    
    def __init__(self, parent):
        """Initialize playlist manager"""
        self.parent = parent
        self.playlist_dock = None
        self.playlist_view = None
        self.search_box = None
        self.auto_hide_timer = None
        self.playlist_was_visible = True
    
    def setup(self):
        """Setup playlist dock widget"""
        self.playlist_dock = QtWidgets.QDockWidget('Playlist', self.parent)
        
        playlist_container = QtWidgets.QWidget()
        playlist_layout = QtWidgets.QVBoxLayout()
        
        # Search box
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText('Search videos... (Ctrl+F)')
        self.search_box.textChanged.connect(self.parent.search_playlist)
        playlist_layout.addWidget(self.search_box)
        
        # Playlist view
        self.playlist_view = QtWidgets.QListWidget()
        self.playlist_view.itemSelectionChanged.connect(self.parent._on_playlist_item_selected)
        playlist_layout.addWidget(self.playlist_view)
        
        playlist_container.setLayout(playlist_layout)
        self.playlist_dock.setWidget(playlist_container)
        
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.playlist_dock)
        
        # Setup auto-hide timer
        self.auto_hide_timer = QtCore.QTimer()
        self.auto_hide_timer.timeout.connect(self.parent._on_auto_hide_timeout)
        
        # Enable mouse tracking for auto-hide
        self.playlist_dock.enterEvent = lambda e: self._on_enter(e)
        self.playlist_dock.leaveEvent = lambda e: self._on_leave(e)
    
    def _on_enter(self, event):
        """Handle mouse enter playlist"""
        self.auto_hide_timer.stop()
        self.playlist_was_visible = True
    
    def _on_leave(self, event):
        """Handle mouse leave playlist"""
        if self.parent.auto_hide_action.isChecked():
            timeout = self.parent.controller.settings_service.get('autohide_timeout', 3)
            self.auto_hide_timer.start(int(timeout * 1000))
    
    def update_view(self, videos):
        """Update playlist view with proper colors"""
        self.playlist_view.clear()
        for video in videos:
            item = QtWidgets.QListWidgetItem(video.name)
            
            # Color based on status
            status = video.metadata.status
            if status == 'liked':
                item.setBackground(QtGui.QColor('lightgreen'))
            elif status == 'disliked':
                item.setBackground(QtGui.QColor('lightcoral'))
            else:
                item.setBackground(QtGui.QColor('lightblue'))
            
            self.playlist_view.addItem(item)
    
    def update_colors(self, videos):
        """Update all playlist item colors"""
        for i in range(self.playlist_view.count()):
            item = self.playlist_view.item(i)
            video_name = item.text()
            video = next((v for v in videos if v.name == video_name), None)
            
            if video:
                status = video.metadata.status
                if status == 'liked':
                    item.setBackground(QtGui.QColor('lightgreen'))
                elif status == 'disliked':
                    item.setBackground(QtGui.QColor('lightcoral'))
                else:
                    item.setBackground(QtGui.QColor('lightblue'))
    
    def focus_search(self):
        """Focus search box and select all"""
        self.search_box.setFocus()
        self.search_box.selectAll()
