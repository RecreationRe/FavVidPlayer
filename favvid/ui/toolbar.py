"""Toolbar setup and controls for PlayerWindow"""
from PyQt5 import QtWidgets, QtCore


class ToolbarManager:
    """Manages playback toolbar setup and controls"""
    
    BUTTON_STYLE_NORMAL = 'background-color: lightblue; border: none; padding: 5px; border-radius: 3px;'
    BUTTON_STYLE_LIKED = 'background-color: lightgreen; border: none; padding: 5px; border-radius: 3px;'
    BUTTON_STYLE_DISLIKED = 'background-color: lightcoral; border: none; padding: 5px; border-radius: 3px;'
    
    def __init__(self, parent):
        """Initialize toolbar manager"""
        self.parent = parent
        self.toolbar = None
        self.position_slider = None
        self.volume_slider = None
        self.time_label = None
        self.play_action = None
        self.shuffle_btn = None
        self.repeat_btn = None
    
    def setup(self):
        """Setup playback toolbar with proper styling"""
        self.toolbar = self.parent.addToolBar('Playback')
        self.parent.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolbar)
        
        # Playback controls
        self.toolbar.addAction('⏮', self.parent.previous_video)
        self.play_action = self.toolbar.addAction('▶', self.parent.toggle_play_pause)
        self.toolbar.addAction('⏹', self.parent.stop_playback)
        self.toolbar.addAction('⏭', self.parent.next_video)
        
        self.toolbar.addSeparator()
        
        # Time display and position slider
        self.time_label = QtWidgets.QLabel('00:00 / 00:00')
        self.time_label.setMinimumWidth(100)
        self.toolbar.addWidget(self.time_label)
        
        self.position_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.position_slider.setMaximum(1000)
        self.position_slider.sliderMoved.connect(self.parent.seek_video)
        self.toolbar.addWidget(self.position_slider)
        
        self.toolbar.addSeparator()
        
        # Volume control
        self.toolbar.addWidget(QtWidgets.QLabel('🔊'))
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.parent.set_volume)
        self.toolbar.addWidget(self.volume_slider)
        
        self.toolbar.addSeparator()
        
        # Fullscreen
        self.toolbar.addAction('⛶', self.parent.toggle_fullscreen)
        
        self.toolbar.addSeparator()
        
        # Shuffle and repeat
        self.shuffle_btn = QtWidgets.QPushButton('🔀 Shuffle')
        self.shuffle_btn.setCheckable(True)
        self.shuffle_btn.setToolTip('Toggle shuffle (S)')
        self.shuffle_btn.toggled.connect(self.parent._on_shuffle_toggled)
        self.toolbar.addWidget(self.shuffle_btn)
        
        self.repeat_btn = QtWidgets.QPushButton('🔁 Off')
        self.repeat_btn.setToolTip('Cycle repeat: off → once → all (R)')
        self.repeat_btn.clicked.connect(self.parent._toggle_repeat)
        self.toolbar.addWidget(self.repeat_btn)
        
        # Ratings buttons
        self._setup_rating_buttons()
    
    def _setup_rating_buttons(self):
        """Setup rating buttons with colors"""
        self.toolbar.addSeparator()
        
        normal_btn = QtWidgets.QPushButton('😐')
        normal_btn.setStyleSheet(self.BUTTON_STYLE_NORMAL)
        normal_btn.setToolTip('Mark as normal (1)')
        normal_btn.clicked.connect(lambda: self.parent.set_rating('normal'))
        self.toolbar.addWidget(normal_btn)
        
        liked_btn = QtWidgets.QPushButton('👍')
        liked_btn.setStyleSheet(self.BUTTON_STYLE_LIKED)
        liked_btn.setToolTip('Mark as liked (2)')
        liked_btn.clicked.connect(lambda: self.parent.set_rating('liked'))
        self.toolbar.addWidget(liked_btn)
        
        disliked_btn = QtWidgets.QPushButton('👎')
        disliked_btn.setStyleSheet(self.BUTTON_STYLE_DISLIKED)
        disliked_btn.setToolTip('Mark as disliked (3)')
        disliked_btn.clicked.connect(lambda: self.parent.set_rating('disliked'))
        self.toolbar.addWidget(disliked_btn)
    
    def update_play_icon(self, is_playing: bool):
        """Update play button icon based on playback state"""
        if self.play_action:
            self.play_action.setText('⏸' if is_playing else '▶')
