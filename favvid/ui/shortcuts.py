"""Keyboard shortcuts setup"""
from PyQt5 import QtWidgets, QtGui


class ShortcutsManager:
    """Manages all keyboard shortcuts"""
    
    def __init__(self, parent):
        """Initialize shortcuts manager"""
        self.parent = parent
    
    def setup_all(self):
        """Setup all keyboard shortcuts"""
        self._setup_playback_shortcuts()
        self._setup_navigation_shortcuts()
        self._setup_rating_shortcuts()
        self._setup_control_shortcuts()
        self._setup_volume_shortcuts()
        self._setup_ui_shortcuts()
    
    def _setup_playback_shortcuts(self):
        """Setup playback control shortcuts"""
        QtWidgets.QShortcut(QtGui.QKeySequence('Space'), self.parent, self.parent.toggle_play_pause)
        QtWidgets.QShortcut(QtGui.QKeySequence('Z'), self.parent, self.parent.seek_backward)
        QtWidgets.QShortcut(QtGui.QKeySequence('X'), self.parent, self.parent.seek_forward)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Z'), self.parent, self.parent.seek_backward_large)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+X'), self.parent, self.parent.seek_forward_large)
    
    def _setup_navigation_shortcuts(self):
        """Setup video navigation shortcuts"""
        QtWidgets.QShortcut(QtGui.QKeySequence('Left'), self.parent, self.parent.previous_video)
        QtWidgets.QShortcut(QtGui.QKeySequence('Right'), self.parent, self.parent.next_video)
    
    def _setup_rating_shortcuts(self):
        """Setup rating shortcuts (1-3 keys)"""
        QtWidgets.QShortcut(QtGui.QKeySequence('1'), self.parent, lambda: self.parent.set_rating('normal'))
        QtWidgets.QShortcut(QtGui.QKeySequence('2'), self.parent, lambda: self.parent.set_rating('liked'))
        QtWidgets.QShortcut(QtGui.QKeySequence('3'), self.parent, lambda: self.parent.set_rating('disliked'))
    
    def _setup_control_shortcuts(self):
        """Setup general control shortcuts (S, R, A, M, V)"""
        QtWidgets.QShortcut(QtGui.QKeySequence('S'), self.parent, self.parent._toggle_shuffle)
        QtWidgets.QShortcut(QtGui.QKeySequence('R'), self.parent, self.parent._toggle_repeat)
        QtWidgets.QShortcut(QtGui.QKeySequence('A'), self.parent, self.parent._toggle_auto_hide)
        QtWidgets.QShortcut(QtGui.QKeySequence('M'), self.parent, self.parent._toggle_view_mode)
        QtWidgets.QShortcut(QtGui.QKeySequence('V'), self.parent, self.parent.toggle_mute)
    
    def _setup_volume_shortcuts(self):
        """Setup volume control shortcuts"""
        QtWidgets.QShortcut(QtGui.QKeySequence('Up'), self.parent, self.parent.volume_up)
        QtWidgets.QShortcut(QtGui.QKeySequence('Down'), self.parent, self.parent.volume_down)
    
    def _setup_ui_shortcuts(self):
        """Setup UI control shortcuts"""
        QtWidgets.QShortcut(QtGui.QKeySequence('F11'), self.parent, self.parent.toggle_fullscreen)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+F'), self.parent, self.parent._focus_search)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+O'), self.parent, self.parent.open_folder)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+S'), self.parent, self.parent._save_settings)
