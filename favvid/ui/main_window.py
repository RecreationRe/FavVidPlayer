"""Main application window"""
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui
from ..controller import ApplicationController


class PlayerWindow(QtWidgets.QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FavVidPlayer')
        self.resize(1200, 800)
        
        # Initialize controller
        self.controller = ApplicationController()
        
        # Setup UI
        self._setup_menu_bar()
        self._setup_central_widget()
        self._setup_toolbar()
        self._setup_dock_widgets()
        self._setup_shortcuts()
        self._setup_connections()
        
        # Load saved settings
        self._load_settings()
    
    def _setup_menu_bar(self):
        """Setup menu bar"""
        menu_bar = self.menuBar()
        
        # File menu
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction('Open Folder', self.open_folder)
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        
        # View menu
        view_menu = menu_bar.addMenu('View')
        self.explorer_action = view_menu.addAction('File Explorer Mode')
        self.explorer_action.setCheckable(True)
        
        # Help menu
        help_menu = menu_bar.addMenu('Help')
        help_menu.addAction('Settings', self.show_settings)
        help_menu.addAction('Hotkeys', self.show_hotkeys)
    
    def _setup_central_widget(self):
        """Setup central video widget"""
        self.video_frame = QtWidgets.QFrame()
        self.setCentralWidget(self.video_frame)
        
        # Initialize playback service
        self.controller.set_playback_service(self.video_frame)
    
    def _setup_toolbar(self):
        """Setup playback toolbar"""
        self.toolbar = self.addToolBar('Playback')
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolbar)
        
        # Playback controls
        self.toolbar.addAction('⏮', self.previous_video)
        self.play_action = self.toolbar.addAction('▶', self.toggle_play_pause)
        self.toolbar.addAction('⏹', self.stop_playback)
        self.toolbar.addAction('⏭', self.next_video)
        
        self.toolbar.addSeparator()
        
        # Time display
        self.time_label = QtWidgets.QLabel('00:00 / 00:00')
        self.time_label.setMinimumWidth(100)
        self.toolbar.addWidget(self.time_label)
        
        # Position slider
        self.position_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.position_slider.setMaximum(1000)
        self.position_slider.sliderMoved.connect(self.seek_video)
        self.toolbar.addWidget(self.position_slider)
        
        self.toolbar.addSeparator()
        
        # Volume
        self.toolbar.addWidget(QtWidgets.QLabel('🔊'))
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.toolbar.addWidget(self.volume_slider)
        
        self.toolbar.addSeparator()
        
        # Other controls
        self.toolbar.addAction('⛶', self.toggle_fullscreen)
        
        self.toolbar.addSeparator()
        
        # Shuffle and repeat
        self.shuffle_btn = QtWidgets.QPushButton('🔀')
        self.shuffle_btn.setCheckable(True)
        self.toolbar.addWidget(self.shuffle_btn)
        
        self.repeat_btn = QtWidgets.QPushButton('🔁')
        self.repeat_btn.setCheckable(True)
        self.toolbar.addWidget(self.repeat_btn)
        
        # Ratings
        self.toolbar.addSeparator()
        self.toolbar.addAction('😐', lambda: self.set_rating('normal'))
        self.toolbar.addAction('👍', lambda: self.set_rating('liked'))
        self.toolbar.addAction('👎', lambda: self.set_rating('disliked'))
    
    def _setup_dock_widgets(self):
        """Setup dock widgets"""
        # Playlist dock
        self.playlist_dock = QtWidgets.QDockWidget('Playlist', self)
        
        playlist_container = QtWidgets.QWidget()
        playlist_layout = QtWidgets.QVBoxLayout()
        
        # Search box
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText('Search videos...')
        self.search_box.textChanged.connect(self.search_playlist)
        playlist_layout.addWidget(self.search_box)
        
        # Playlist view
        self.playlist_view = QtWidgets.QListWidget()
        playlist_layout.addWidget(self.playlist_view)
        
        playlist_container.setLayout(playlist_layout)
        self.playlist_dock.setWidget(playlist_container)
        
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.playlist_dock)
    
    def _setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        QtWidgets.QShortcut(QtGui.QKeySequence('Space'), self, self.toggle_play_pause)
        QtWidgets.QShortcut(QtGui.QKeySequence('Left'), self, self.previous_video)
        QtWidgets.QShortcut(QtGui.QKeySequence('Right'), self, self.next_video)
        QtWidgets.QShortcut(QtGui.QKeySequence('F11'), self, self.toggle_fullscreen)
        QtWidgets.QShortcut(QtGui.QKeySequence('Up'), self, self.volume_up)
        QtWidgets.QShortcut(QtGui.QKeySequence('Down'), self, self.volume_down)
        QtWidgets.QShortcut(QtGui.QKeySequence('S'), self, self.controller.toggle_shuffle)
    
    def _setup_connections(self):
        """Setup signal connections"""
        self.controller.videos_loaded.connect(self._on_videos_loaded)
        self.controller.video_started.connect(self._on_video_started)
    
    def _load_settings(self):
        """Load saved settings"""
        settings = self.controller.settings_service
        self.volume_slider.setValue(settings.get('volume', 50))
        
        last_folder = settings.get('last_folder')
        if last_folder and Path(last_folder).exists():
            self.controller.load_folder(last_folder)
    
    # Slot methods
    def open_folder(self):
        """Open folder dialog"""
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select folder')
        if folder:
            self.controller.load_folder(Path(folder))
    
    def toggle_play_pause(self):
        """Toggle play/pause"""
        self.controller.toggle_play_pause()
        self.play_action.setText('⏸' if self.controller.get_is_playing() else '▶')
    
    def stop_playback(self):
        """Stop playback"""
        if self.controller.playback_service:
            self.controller.playback_service.stop()
        self.play_action.setText('▶')
    
    def previous_video(self):
        """Play previous video"""
        self.controller.play_previous()
    
    def next_video(self):
        """Play next video"""
        self.controller.play_next()
    
    def seek_video(self, value):
        """Seek to position"""
        self.controller.set_video_position(value / 1000.0)
    
    def set_volume(self, value):
        """Set volume"""
        self.controller.set_volume(value)
    
    def volume_up(self):
        """Increase volume"""
        new_vol = min(100, self.volume_slider.value() + 5)
        self.volume_slider.setValue(new_vol)
    
    def volume_down(self):
        """Decrease volume"""
        new_vol = max(0, self.volume_slider.value() - 5)
        self.volume_slider.setValue(new_vol)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen"""
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def set_rating(self, status):
        """Set video rating"""
        if self.controller.playback_service and self.controller.playback_service.current_video:
            self.controller.set_video_rating(
                self.controller.playback_service.current_video,
                status
            )
    
    def search_playlist(self, query):
        """Search playlist"""
        results = self.controller.search_playlist(query)
        self._update_playlist_view(results if query else self.controller.playlist.videos)
    
    def show_settings(self):
        """Show settings dialog"""
        # TODO: Implement settings dialog
        pass
    
    def show_hotkeys(self):
        """Show hotkeys dialog"""
        # TODO: Implement hotkeys dialog
        pass
    
    def _on_videos_loaded(self, videos):
        """Handle videos loaded signal"""
        self._update_playlist_view(videos)
    
    def _on_video_started(self, video):
        """Handle video started signal"""
        self.setWindowTitle(f'FavVidPlayer - {video.name}')
    
    def _update_playlist_view(self, videos):
        """Update playlist view"""
        self.playlist_view.clear()
        for video in videos:
            self.playlist_view.addItem(video.name)
    
    def keyPressEvent(self, event):
        """Handle key press - especially Space key"""
        if event.key() == QtCore.Qt.Key_Space and not event.isAutoRepeat():
            self.toggle_play_pause()
            return
        super().keyPressEvent(event)
