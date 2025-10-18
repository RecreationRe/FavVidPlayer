"""Dialog windows for settings and hotkeys"""
from PyQt5 import QtWidgets, QtCore


class SettingsDialog(QtWidgets.QDialog):
    """Settings dialog with persistent options"""
    
    def __init__(self, parent, controller):
        """Initialize settings dialog"""
        super().__init__(parent)
        self.setWindowTitle('Settings')
        self.resize(450, 350)
        self.controller = controller
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QtWidgets.QVBoxLayout()
        
        # Master volume
        layout.addWidget(QtWidgets.QLabel('Master Volume:'))
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMaximum(100)
        vol_value = self.controller.settings_service.get('volume', 50)
        self.volume_slider.setValue(vol_value)
        layout.addWidget(self.volume_slider)
        
        # Small seek interval
        layout.addWidget(QtWidgets.QLabel('Small Seek Interval (seconds):'))
        self.small_seek_spin = QtWidgets.QSpinBox()
        self.small_seek_spin.setMinimum(1)
        self.small_seek_spin.setMaximum(60)
        small_seek = self.controller.settings_service.get('small_seek_interval', 5)
        self.small_seek_spin.setValue(int(small_seek))
        layout.addWidget(self.small_seek_spin)
        
        # Large seek interval
        layout.addWidget(QtWidgets.QLabel('Large Seek Interval (seconds):'))
        self.large_seek_spin = QtWidgets.QSpinBox()
        self.large_seek_spin.setMinimum(1)
        self.large_seek_spin.setMaximum(300)
        large_seek = self.controller.settings_service.get('large_seek_interval', 30)
        self.large_seek_spin.setValue(int(large_seek))
        layout.addWidget(self.large_seek_spin)
        
        # Auto-hide timeout
        layout.addWidget(QtWidgets.QLabel('Auto-hide Timeout (seconds):'))
        self.autohide_spin = QtWidgets.QSpinBox()
        self.autohide_spin.setMinimum(1)
        self.autohide_spin.setMaximum(30)
        autohide = self.controller.settings_service.get('autohide_timeout', 3)
        self.autohide_spin.setValue(int(autohide))
        layout.addWidget(self.autohide_spin)
        
        layout.addStretch()
        
        # Buttons
        button_layout = QtWidgets.QHBoxLayout()
        ok_btn = QtWidgets.QPushButton('OK')
        ok_btn.clicked.connect(self._save_settings)
        cancel_btn = QtWidgets.QPushButton('Cancel')
        cancel_btn.clicked.connect(self.reject)
        button_layout.addStretch()
        button_layout.addWidget(ok_btn)
        button_layout.addWidget(cancel_btn)
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def _save_settings(self):
        """Save settings and close"""
        self.controller.settings_service.set('volume', self.volume_slider.value())
        self.controller.settings_service.set('small_seek_interval', self.small_seek_spin.value())
        self.controller.settings_service.set('large_seek_interval', self.large_seek_spin.value())
        self.controller.settings_service.set('autohide_timeout', self.autohide_spin.value())
        self.accept()


class HotkeysDialog(QtWidgets.QDialog):
    """Hotkeys reference dialog"""
    
    def __init__(self, parent):
        """Initialize hotkeys dialog"""
        super().__init__(parent)
        self.setWindowTitle('Hotkeys')
        self.resize(500, 450)
        
        self._setup_ui()
    
    def _setup_ui(self):
        """Setup dialog UI"""
        layout = QtWidgets.QVBoxLayout()
        
        hotkeys_text = """
        PLAYBACK:
        Space - Play/Pause
        Z - Seek Backward (small)
        X - Seek Forward (small)
        Ctrl+Z - Seek Backward (large)
        Ctrl+X - Seek Forward (large)
        ⏮/⏭ - Previous/Next Video
        
        RATINGS:
        1 - Mark as Normal
        2 - Mark as Liked
        3 - Mark as Disliked
        
        CONTROLS:
        S - Toggle Shuffle
        R - Toggle Repeat (cycles: off → once → all)
        A - Toggle Auto-hide
        M - Toggle View Mode (flat/tree)
        V - Toggle Mute
        
        VOLUME:
        Up Arrow - Volume Up (+5)
        Down Arrow - Volume Down (-5)
        
        UI:
        F11 - Toggle Fullscreen
        Ctrl+F - Focus Search
        Ctrl+O - Open Folder
        Ctrl+S - Save Settings
        
        VIDEO:
        Click - Play/Pause
        Double Click - Fullscreen
        Mouse Wheel - Volume Up/Down
        """
        
        text_edit = QtWidgets.QTextEdit()
        text_edit.setText(hotkeys_text.strip())
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        close_btn = QtWidgets.QPushButton('Close')
        close_btn.clicked.connect(self.accept)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
