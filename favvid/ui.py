from PyQt5 import QtWidgets, QtGui, QtCore
from pathlib import Path
import random
from .scanner import scan_videos
from .meta import MetaStore, FAV_FOLDER_NAME
from .player import VLCPlayer


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowTitle('Settings')
        layout = QtWidgets.QVBoxLayout()
        
        # Persistence settings
        self.persist_volume = QtWidgets.QCheckBox('Persist Volume')
        self.persist_position = QtWidgets.QCheckBox('Persist Last Position')
        settings = QtCore.QSettings()
        self.persist_volume.setChecked(settings.value("persist_volume", True, type=bool))
        self.persist_position.setChecked(settings.value("persist_position", True, type=bool))
        layout.addWidget(self.persist_volume)
        layout.addWidget(self.persist_position)
        
        # Seek intervals
        layout.addWidget(QtWidgets.QLabel("Seek Intervals:"))
        seek_layout = QtWidgets.QHBoxLayout()
        seek_layout.addWidget(QtWidgets.QLabel("Small (Z/X):"))
        self.small_seek = QtWidgets.QDoubleSpinBox()
        self.small_seek.setRange(0.1, 60.0)
        self.small_seek.setSingleStep(0.5)
        self.small_seek.setSuffix(" sec")
        self.small_seek.setValue(settings.value("small_seek_seconds", 5.0, type=float))
        seek_layout.addWidget(self.small_seek)
        
        seek_layout.addWidget(QtWidgets.QLabel("Large (Ctrl+Z/X):"))
        self.large_seek = QtWidgets.QDoubleSpinBox()
        self.large_seek.setRange(1.0, 300.0)
        self.large_seek.setSingleStep(5.0)
        self.large_seek.setSuffix(" sec")
        self.large_seek.setValue(settings.value("large_seek_seconds", 30.0, type=float))
        seek_layout.addWidget(self.large_seek)
        layout.addLayout(seek_layout)
        
        buttons = QtWidgets.QDialogButtonBox(QtWidgets.QDialogButtonBox.Ok | QtWidgets.QDialogButtonBox.Cancel)
        buttons.accepted.connect(self.accept)
        buttons.rejected.connect(self.reject)
        layout.addWidget(buttons)
        self.setLayout(layout)

    def accept(self):
        settings = QtCore.QSettings()
        settings.setValue("persist_volume", self.persist_volume.isChecked())
        settings.setValue("persist_position", self.persist_position.isChecked())
        settings.setValue("small_seek_seconds", self.small_seek.value())
        settings.setValue("large_seek_seconds", self.large_seek.value())
        super().accept()


class VideoOverlay(QtWidgets.QWidget):
    """Transparent overlay for handling video interactions"""
    single_clicked = QtCore.pyqtSignal()
    double_clicked = QtCore.pyqtSignal()
    wheel_scrolled = QtCore.pyqtSignal(int)
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        self.setStyleSheet("background-color: transparent;")
        self.click_timer = None
        self.setMouseTracking(True)
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
    
    def mousePressEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            self.click_timer = QtCore.QTimer()
            self.click_timer.setSingleShot(True)
            self.click_timer.timeout.connect(self.on_single_click)
            self.click_timer.start(250)
            event.accept()
        else:
            event.ignore()
    
    def mouseDoubleClickEvent(self, event):
        if event.button() == QtCore.Qt.LeftButton:
            if self.click_timer:
                self.click_timer.stop()
            self.double_clicked.emit()
            event.accept()
        else:
            event.ignore()
    
    def wheelEvent(self, event):
        delta = event.angleDelta().y()
        self.wheel_scrolled.emit(delta)
        event.accept()
    
    def on_single_click(self):
        self.single_clicked.emit()


class VideoWidget(QtWidgets.QFrame):
    """Custom widget for video with event handling"""
    single_clicked = QtCore.pyqtSignal()
    double_clicked = QtCore.pyqtSignal()
    wheel_scrolled = QtCore.pyqtSignal(int)  # delta
    
    def __init__(self):
        super().__init__()
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        self.setAttribute(QtCore.Qt.WA_Hover, True)
        self.setMouseTracking(True)
        
        # Create layout for this frame
        layout = QtWidgets.QVBoxLayout()
        layout.setContentsMargins(0, 0, 0, 0)
        
        # Create overlay
        self.overlay = VideoOverlay(self)
        self.overlay.single_clicked.connect(lambda: self.single_clicked.emit())
        self.overlay.double_clicked.connect(lambda: self.double_clicked.emit())
        self.overlay.wheel_scrolled.connect(lambda delta: self.wheel_scrolled.emit(delta))
        
        self.setLayout(layout)
    
    def resizeEvent(self, event):
        """Resize overlay to match frame"""
        super().resizeEvent(event)
        if hasattr(self, 'overlay'):
            self.overlay.resize(self.size())
            self.overlay.raise_()  # Bring to front


class PlayerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FavVidPlayer')
        self.resize(1200, 800)
        
        # Store click timer for single/double click detection
        self.video_click_timer = None
        self.last_click_time = 0
        self.double_click_threshold = 250  # ms

        # menu bar
        self.menu_bar = self.menuBar()
        file_menu = self.menu_bar.addMenu('File')
        file_menu.addAction('Select Folder', self.open_folder)
        view_menu = self.menu_bar.addMenu('View')
        self.explorer_action = view_menu.addAction('File Explorer Mode')
        self.explorer_action.setCheckable(True)
        self.explorer_action.setChecked(False)
        self.explorer_action.triggered.connect(self.on_explorer_changed)
        help_menu = self.menu_bar.addMenu('Help')
        help_menu.addAction('Settings', self.show_settings)
        help_menu.addAction('Hotkeys', self.show_hotkeys)

        # status bar for hotkeys
        self.status_bar = self.statusBar()
        self.status_bar.showMessage('Hotkeys: Space=Play/Pause | Z/X=Seek | F11=Fullscreen | ↑↓=Volume | ←→=Prev/Next | 1/2/3=Ratings | S=Shuffle | Ctrl+F=Search | Wheel=Volume')

        # central widget for video
        self.video_frame = VideoWidget()
        self.video_frame.single_clicked.connect(self.video_single_click)
        self.video_frame.double_clicked.connect(self.video_double_click)
        self.video_frame.wheel_scrolled.connect(self.on_video_wheel)
        self.video_frame.setFocusPolicy(QtCore.Qt.NoFocus)  # Don't steal focus from main window
        self.setCentralWidget(self.video_frame)
        
        # Make sure main window handles key events
        self.setFocusPolicy(QtCore.Qt.StrongFocus)
        
        # Install event filter on application to catch all events
        QtWidgets.QApplication.instance().installEventFilter(self)

        # right playlist dock with search
        self.playlist_dock = QtWidgets.QDockWidget('Playlist', self)
        playlist_container = QtWidgets.QWidget()
        playlist_layout = QtWidgets.QVBoxLayout()
        
        # search box
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText('Search videos... (Ctrl+F)')
        self.search_box.textChanged.connect(self.filter_playlist)
        playlist_layout.addWidget(self.search_box)
        
        # playlist views
        self.playlist_stack = QtWidgets.QStackedWidget()
        self.flat_list = QtWidgets.QListWidget()
        self.tree_list = QtWidgets.QTreeWidget()
        self.tree_list.setHeaderLabel("Playlist")
        self.playlist_stack.addWidget(self.flat_list)
        self.playlist_stack.addWidget(self.tree_list)
        playlist_layout.addWidget(self.playlist_stack)
        
        playlist_container.setLayout(playlist_layout)
        self.playlist_dock.setWidget(playlist_container)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.playlist_dock)

        # custom title bar for pin button
        self.title_widget = QtWidgets.QWidget()
        h_title = QtWidgets.QHBoxLayout()
        h_title.addWidget(QtWidgets.QLabel('Playlist'))
        h_title.addStretch()
        self.pin_btn = QtWidgets.QPushButton('Pin')
        self.pin_btn.setCheckable(True)
        self.pin_btn.clicked.connect(self.on_pin_changed)
        h_title.addWidget(self.pin_btn)
        self.title_widget.setLayout(h_title)
        self.playlist_dock.setTitleBarWidget(self.title_widget)

        # default to flat
        self.playlist_widget = self.flat_list
        self.playlist_stack.setCurrentWidget(self.flat_list)

        # connect signals
        self.flat_list.itemClicked.connect(self.on_item_clicked)
        self.tree_list.itemClicked.connect(self.on_item_clicked)

        # playback toolbar
        self.toolbar = QtWidgets.QToolBar('Playback')
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self.toolbar)
        
        # shuffle button
        self.shuffle_action = self.toolbar.addAction('🔀', self.toggle_shuffle)
        self.shuffle_action.setCheckable(True)
        self.shuffle_action.setToolTip('Shuffle (S)')
        
        self.toolbar.addAction('⏮', self.previous_video).setToolTip('Previous (Left Arrow)')
        self.play_action = self.toolbar.addAction('▶', self.toggle_play_pause)
        self.play_action.setToolTip('Play/Pause (Space)')
        self.toolbar.addAction('⏹', self.stop_playback).setToolTip('Stop (Ctrl+S)')
        self.toolbar.addAction('⏭', self.next_video).setToolTip('Next (Right Arrow)')
        self.toolbar.addSeparator()
        
        # time display and position
        self.time_label = QtWidgets.QLabel('00:00 / 00:00')
        self.time_label.setMinimumWidth(100)
        self.toolbar.addWidget(self.time_label)
        
        self.position_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.position_slider.setMaximum(1000)
        self.position_slider.sliderMoved.connect(self.set_position)
        self.position_slider.mousePressEvent = self.position_click_seek
        self.toolbar.addWidget(self.position_slider)
        self.toolbar.addSeparator()
        
        # volume with icon
        self.volume_icon = QtWidgets.QLabel('🔊')
        self.toolbar.addWidget(self.volume_icon)
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        self.volume_slider.wheelEvent = self.volume_wheel_event
        self.toolbar.addWidget(self.volume_slider)
        
        self.toolbar.addSeparator()
        self.fullscreen_action = self.toolbar.addAction('⛶', self.toggle_fullscreen)
        self.fullscreen_action.setToolTip('Fullscreen (F11)')
        
        self.toolbar.addSeparator()
        self.speed_label = QtWidgets.QLabel('Speed:')
        self.toolbar.addWidget(self.speed_label)
        self.speed_spin = QtWidgets.QDoubleSpinBox()
        self.speed_spin.setRange(0.25, 4.0)
        self.speed_spin.setSingleStep(0.25)
        self.speed_spin.setValue(1.0)
        self.speed_spin.valueChanged.connect(self.on_speed_changed)
        self.toolbar.addWidget(self.speed_spin)
        
        self.repeat_checkbox = QtWidgets.QCheckBox('🔁')
        self.repeat_checkbox.stateChanged.connect(self.on_repeat_changed)
        self.repeat_checkbox.setToolTip('Repeat (R)')
        self.toolbar.addWidget(self.repeat_checkbox)
        
        self.auto_next_checkbox = QtWidgets.QCheckBox('⏭️')
        self.auto_next_checkbox.setChecked(True)
        self.auto_next_checkbox.setToolTip('Auto Next (A)')
        self.toolbar.addWidget(self.auto_next_checkbox)
        self.toolbar.addSeparator()
        
        # ratings with icons
        self.normal_btn = QtWidgets.QPushButton('😐')
        self.normal_btn.setStyleSheet('background-color: lightblue')
        self.normal_btn.clicked.connect(lambda: self.toggle_status('normal'))
        self.normal_btn.setToolTip('Normal (1)')
        self.toolbar.addWidget(self.normal_btn)
        self.like_btn = QtWidgets.QPushButton('👍')
        self.like_btn.setStyleSheet('background-color: lightgreen')
        self.like_btn.clicked.connect(lambda: self.toggle_status('liked'))
        self.like_btn.setToolTip('Like (2)')
        self.toolbar.addWidget(self.like_btn)
        self.dislike_btn = QtWidgets.QPushButton('👎')
        self.dislike_btn.setStyleSheet('background-color: lightcoral')
        self.dislike_btn.clicked.connect(lambda: self.toggle_status('disliked'))
        self.dislike_btn.setToolTip('Dislike (3)')
        self.toolbar.addWidget(self.dislike_btn)

        # settings
        self.settings = QtCore.QSettings()

        # state
        self.current_root = None
        self.playlist = []  # list of Path
        self.original_playlist = []  # for shuffle
        self.meta = None
        self.current_playing_path = None
        self.shuffle_mode = False
        self.original_title = 'FavVidPlayer'
        self.global_repeat_enabled = False  # Track repeat state across videos
        self.is_repeating_current = False  # Flag for current repeat
        
        # seek intervals (configurable)
        self.small_seek_seconds = self.settings.value("small_seek_seconds", 5.0, type=float)
        self.large_seek_seconds = self.settings.value("large_seek_seconds", 30.0, type=float)

        # load settings
        pin = self.settings.value("pin_playlist", False, type=bool)
        explorer = self.settings.value("file_explorer_mode", False, type=bool)

        self.pin_btn.blockSignals(True)
        self.pin_btn.setChecked(pin)
        self.pin_btn.blockSignals(False)

        self.explorer_action.blockSignals(True)
        self.explorer_action.setChecked(explorer)
        self.explorer_action.blockSignals(False)

        if explorer:
            self.toggle_playlist_mode(QtCore.Qt.Checked)

        # timers
        self.edge_timer = QtCore.QTimer()
        self.edge_timer.timeout.connect(self.check_mouse_edge)
        self.edge_timer.start(200)

        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)

        # player wrapper
        self.vlc = VLCPlayer(self.video_frame)

        # load last folder
        last_folder = self.settings.value("last_folder")
        if last_folder and Path(last_folder).exists():
            self.open_folder(last_folder)

        # load volume
        vol = self.settings.value("volume", 50, type=int)
        self.volume_slider.blockSignals(True)
        self.volume_slider.setValue(vol)
        self.volume_slider.blockSignals(False)
        self.set_volume(vol)
        
        # setup keyboard shortcuts
        self.setup_shortcuts()

    def on_video_wheel(self, delta):
        """Handle mouse wheel on video"""
        current_vol = self.volume_slider.value()
        if delta > 0:
            new_vol = min(100, current_vol + 5)
        else:
            new_vol = max(0, current_vol - 5)
        self.volume_slider.setValue(new_vol)

    def keyPressEvent(self, event):
        """Override to ensure hotkeys work even when VLC has focus"""
        # Handle Space key explicitly since VLC might consume it
        if event.key() == QtCore.Qt.Key_Space and not event.isAutoRepeat():
            self.toggle_play_pause()
            return
        
        # For other keys, let Qt shortcuts handle them
        super().keyPressEvent(event)

    def mousePressEvent(self, event):
        """Handle mouse clicks on video"""
        # Check if click is on video area
        video_rect = self.video_frame.geometry()
        if video_rect.contains(self.mapFromGlobal(QtGui.QCursor.pos())):
            if event.button() == QtCore.Qt.LeftButton:
                current_time = QtCore.QTime.currentTime().msecsSinceStartOfDay()
                
                # Check if this is a double click
                if current_time - self.last_click_time < self.double_click_threshold:
                    if self.video_click_timer:
                        self.video_click_timer.stop()
                    self.video_double_click()
                    self.last_click_time = 0
                else:
                    self.last_click_time = current_time
                    # Single click - start timer
                    self.video_click_timer = QtCore.QTimer()
                    self.video_click_timer.setSingleShot(True)
                    self.video_click_timer.timeout.connect(self.video_single_click)
                    self.video_click_timer.start(self.double_click_threshold)
        
        super().mousePressEvent(event)

    def wheelEvent(self, event):
        """Handle mouse wheel anywhere"""
        video_rect = self.video_frame.geometry()
        if video_rect.contains(self.mapFromGlobal(QtGui.QCursor.pos())):
            delta = event.angleDelta().y()
            current_vol = self.volume_slider.value()
            if delta > 0:
                new_vol = min(100, current_vol + 5)
            else:
                new_vol = max(0, current_vol - 5)
            self.volume_slider.setValue(new_vol)
            event.accept()
            return
        
        super().wheelEvent(event)

    def _wrap_widget_as_toolbar(self, widget):
        tb = QtWidgets.QToolBar()
        tb.addWidget(widget)
        return tb

    def open_folder(self, folder=None):
        if not folder:
            folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select folder to scan')
        if not folder:
            return
        root = Path(folder)
        self.current_root = root
        self.meta = MetaStore(root)
        self.playlist = scan_videos(root)
        self.refresh_playlist()
        self.settings.setValue("last_folder", str(root))

    def refresh_playlist(self):
        if isinstance(self.playlist_widget, QtWidgets.QListWidget):
            self.playlist_widget.clear()
            for p in self.playlist:
                item = QtWidgets.QListWidgetItem(str(p.relative_to(self.current_root)))
                status = self.meta.get(str(p.relative_to(self.current_root))).get('status')
                if status == 'liked':
                    item.setBackground(QtGui.QColor('lightgreen'))
                elif status == 'disliked':
                    item.setBackground(QtGui.QColor('lightcoral'))
                elif status == 'normal':
                    item.setBackground(QtGui.QColor('lightblue'))
                self.playlist_widget.addItem(item)
        elif isinstance(self.playlist_widget, QtWidgets.QTreeWidget):
            expanded = self.get_expanded_paths()
            self.build_tree(self.playlist)
            self.restore_expanded_paths(expanded)

    def build_tree(self, paths):
        self.playlist_widget.clear()
        tree = {}

        for p in sorted(paths):
            rel = p.relative_to(self.current_root)
            parts = rel.parts
            current = tree
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            # add file
            if '__files__' not in current:
                current['__files__'] = []
            current['__files__'].append((parts[-1], str(rel)))

        def add_items(parent_item, node):
            for key, value in node.items():
                if key == '__files__':
                    for name, rel in value:
                        file_item = QtWidgets.QTreeWidgetItem([name])
                        file_item.setData(0, QtCore.Qt.UserRole, rel)
                        parent_item.addChild(file_item)
                        status = self.meta.get(rel).get('status')
                        if status == 'liked':
                            file_item.setBackground(0, QtGui.QColor('lightgreen'))
                        elif status == 'disliked':
                            file_item.setBackground(0, QtGui.QColor('lightcoral'))
                        elif status == 'normal':
                            file_item.setBackground(0, QtGui.QColor('lightblue'))
                else:
                    folder_item = QtWidgets.QTreeWidgetItem([key])
                    parent_item.addChild(folder_item)
                    add_items(folder_item, value)

        root_item = self.playlist_widget.invisibleRootItem()
        add_items(root_item, tree)

    def on_item_clicked(self, item):
        if isinstance(item, QtWidgets.QListWidgetItem):
            rel = item.text()
        elif isinstance(item, QtWidgets.QTreeWidgetItem):
            rel = item.data(0, QtCore.Qt.UserRole)
            if not rel:  # folder
                item.setExpanded(not item.isExpanded())
                return
        p = self.current_root / rel
        self.play_file(p)

    def on_pin_changed(self, state):
        self.settings.setValue("pin_playlist", bool(state))

    def on_explorer_changed(self, state):
        self.settings.setValue("file_explorer_mode", bool(state))
        self.toggle_playlist_mode(state)

    def show_settings(self):
        dialog = SettingsDialog(self)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            # Update seek intervals when settings are saved
            self.small_seek_seconds = self.settings.value("small_seek_seconds", 5.0, type=float)
            self.large_seek_seconds = self.settings.value("large_seek_seconds", 30.0, type=float)

    def show_hotkeys(self):
        """Show hotkeys dialog"""
        msg = QtWidgets.QMessageBox(self)
        msg.setWindowTitle('Hotkeys')
        msg.setText('''
<b>Playback Controls:</b><br>
Space - Play/Pause<br>
Left Arrow - Previous Video<br>
Right Arrow - Next Video<br>
Ctrl+S - Stop<br>
F11 - Toggle Fullscreen<br><br>

<b>Seeking:</b><br>
Z - Seek Backward (Small)<br>
X - Seek Forward (Small)<br>
Ctrl+Z - Seek Backward (Large)<br>
Ctrl+X - Seek Forward (Large)<br>
<i>Seek intervals configurable in Settings</i><br><br>

<b>Volume:</b><br>
Up Arrow - Volume Up<br>
Down Arrow - Volume Down<br>
M - Toggle Mute<br>
Mouse Wheel on Video - Adjust Volume<br><br>

<b>Ratings:</b><br>
1 - Normal Rating<br>
2 - Like<br>
3 - Dislike<br><br>

<b>Playlist:</b><br>
S - Toggle Shuffle<br>
R - Toggle Repeat<br>
Ctrl+F - Focus Search Box<br>
Ctrl+O - Open Folder<br><br>

<b>Video Interaction:</b><br>
Single Click on Video - Play/Pause<br>
Double Click on Video - Fullscreen<br>
Click on Position Bar - Seek to Position<br>
Mouse Wheel on Video - Volume Control
        ''')
        msg.exec_()

    def play_file(self, path: Path):
        if not path.exists():
            QtWidgets.QMessageBox.warning(self, 'Missing', f'File not found: {path}')
            return
        self.current_playing_path = path
        self.vlc.play(path)
        self.play_action.setText('⏸')
        meta = self.meta.get(str(path.relative_to(self.current_root)))
        speed = meta.get('speed', 1.0)
        QtCore.QTimer.singleShot(300, lambda: self.vlc.set_rate(speed))
        
        # Preserve global repeat state
        self.repeat_checkbox.blockSignals(True)
        self.repeat_checkbox.setChecked(self.global_repeat_enabled)
        self.repeat_checkbox.blockSignals(False)
        
        meta['last_played'] = QtCore.QDateTime.currentDateTime().toString()
        self.meta.set(str(path.relative_to(self.current_root)), meta)
        # restore position if persist
        persist = self.settings.value("persist_position", True, type=bool)
        if persist and 'position' in meta:
            QtCore.QTimer.singleShot(500, lambda: self.vlc.set_position(meta['position']))

    def toggle_play_pause(self):
        if self.vlc.is_playing():
            self.vlc.pause()
            self.play_action.setText('▶')
        else:
            # resume
            self.vlc.player.play()
            self.play_action.setText('⏸')

    def stop_playback(self):
        self.vlc.stop()
        self.play_action.setText('▶')

    def previous_video(self):
        if self.playlist and self.current_playing_path:
            current_index = self.playlist.index(self.current_playing_path)
            if current_index > 0:
                self.play_file(self.playlist[current_index - 1])

    def next_video(self):
        if self.playlist and self.current_playing_path:
            current_index = self.playlist.index(self.current_playing_path)
            if current_index < len(self.playlist) - 1:
                self.play_file(self.playlist[current_index + 1])

    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()

    def set_position(self, position):
        self.vlc.set_position(position / 1000.0)

    def set_volume(self, volume):
        self.vlc.set_volume(volume)
        persist = self.settings.value("persist_volume", True, type=bool)
        if persist:
            self.settings.setValue("volume", volume)

    def update_ui(self):
        if self.vlc.is_playing():
            pos = self.vlc.get_position()
            self.position_slider.setValue(int(pos * 1000))
            
            # Update time display
            current_time = self.vlc.get_time()
            total_time = self.vlc.get_length()
            if total_time > 0:
                current_str = self.format_time(current_time)
                total_str = self.format_time(total_time)
                self.time_label.setText(f"{current_str} / {total_str}")
            
            # Update window title
            self.update_window_title()
            
            persist = self.settings.value("persist_position", True, type=bool)
            if persist:
                cur = self.current_playing_rel()
                if cur:
                    m = self.meta.get(cur)
                    m['position'] = pos
                    self.meta.set(cur, m)
        else:
            # Video finished - handle repeat and auto-next
            if self.current_playing_path:
                if self.global_repeat_enabled and not self.is_repeating_current:
                    # Repeat current video
                    self.is_repeating_current = True
                    self.play_file(self.current_playing_path)
                elif self.auto_next_checkbox.isChecked() and self.playlist:
                    # Auto play next
                    if self.current_playing_path in self.playlist:
                        current_index = self.playlist.index(self.current_playing_path)
                        if current_index < len(self.playlist) - 1:
                            self.is_repeating_current = False
                            self.play_file(self.playlist[current_index + 1])
                    else:
                        self.is_repeating_current = False

    def current_playing_rel(self):
        if not self.current_playing_path or not self.current_root:
            return None
        try:
            return str(self.current_playing_path.relative_to(self.current_root))
        except Exception:
            return None

    def set_status(self, status: str):
        cur = self.current_playing_rel()
        if not cur:
            QtWidgets.QMessageBox.information(self, 'No file', 'No file currently playing')
            return
        self.meta.set_status(cur, status, self.current_playing_path)
        self.refresh_playlist()

    def toggle_status(self, status: str):
        cur = self.current_playing_rel()
        if not cur:
            QtWidgets.QMessageBox.information(self, 'No file', 'No file currently playing')
            return
        current = self.meta.get(cur).get('status')
        if current == status:
            # remove rating
            m = self.meta.get(cur)
            m.pop('status', None)
            self.meta.set(cur, m)
        else:
            self.meta.set_status(cur, status, self.current_playing_path)
        self.refresh_playlist()

    def on_speed_changed(self, val):
        self.vlc.set_rate(val)
        cur = self.current_playing_rel()
        if cur:
            m = self.meta.get(cur)
            m['speed'] = val
            self.meta.set(cur, m)

    def on_repeat_changed(self, state):
        """Store global repeat state"""
        self.global_repeat_enabled = bool(state)

    def toggle_playlist_mode(self, state):
        if state == QtCore.Qt.Checked:
            self.playlist_stack.setCurrentWidget(self.tree_list)
            self.playlist_widget = self.tree_list
        else:
            self.playlist_stack.setCurrentWidget(self.flat_list)
            self.playlist_widget = self.flat_list
        self.refresh_playlist()

    def check_mouse_edge(self):
        pos = QtGui.QCursor.pos()
        local_pos = self.mapFromGlobal(pos)
        w = self.width()
        if self.pin_btn.isChecked():
            # pinned: always show
            if not self.playlist_dock.isVisible():
                self.playlist_dock.show()
        else:
            # unpinned: auto-hide
            if local_pos.x() >= w - 40:
                if self.playlist_dock.isHidden():
                    self.playlist_dock.show()
            else:
                if not self.playlist_dock.isHidden() and local_pos.x() < w - 200:
                    self.playlist_dock.hide()

    def get_expanded_paths(self):
        expanded = []
        def collect(item, path):
            if item.isExpanded():
                expanded.append(path)
            for i in range(item.childCount()):
                child = item.child(i)
                collect(child, path + [child.text(0)])
        root = self.playlist_widget.invisibleRootItem()
        collect(root, [])
        return expanded

    def restore_expanded_paths(self, expanded):
        def expand_item(item, path):
            if not path:
                return
            for i in range(item.childCount()):
                child = item.child(i)
                if child.text(0) == path[0]:
                    child.setExpanded(True)
                    expand_item(child, path[1:])
                    break
        for path in expanded:
            expand_item(self.playlist_widget.invisibleRootItem(), path)

    def setup_shortcuts(self):
        """Setup keyboard shortcuts"""
        # Playback shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence('Space'), self, self.toggle_play_pause)
        QtWidgets.QShortcut(QtGui.QKeySequence('Left'), self, self.previous_video)
        QtWidgets.QShortcut(QtGui.QKeySequence('Right'), self, self.next_video)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+S'), self, self.stop_playback)
        QtWidgets.QShortcut(QtGui.QKeySequence('F11'), self, self.toggle_fullscreen)
        
        # Volume shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence('Up'), self, self.volume_up)
        QtWidgets.QShortcut(QtGui.QKeySequence('Down'), self, self.volume_down)
        QtWidgets.QShortcut(QtGui.QKeySequence('M'), self, self.toggle_mute)
        
        # Rating shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence('1'), self, lambda: self.toggle_status('normal'))
        QtWidgets.QShortcut(QtGui.QKeySequence('2'), self, lambda: self.toggle_status('liked'))
        QtWidgets.QShortcut(QtGui.QKeySequence('3'), self, lambda: self.toggle_status('disliked'))
        
        # Seek shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence('Z'), self, self.seek_backward_small)
        QtWidgets.QShortcut(QtGui.QKeySequence('X'), self, self.seek_forward_small)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+Z'), self, self.seek_backward_large)
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+X'), self, self.seek_forward_large)
        
        # Other shortcuts
        QtWidgets.QShortcut(QtGui.QKeySequence('S'), self, self.toggle_shuffle)
        QtWidgets.QShortcut(QtGui.QKeySequence('R'), self, lambda: self.repeat_checkbox.setChecked(not self.repeat_checkbox.isChecked()))
        QtWidgets.QShortcut(QtGui.QKeySequence('A'), self, lambda: self.auto_next_checkbox.setChecked(not self.auto_next_checkbox.isChecked()))
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+F'), self, lambda: self.search_box.setFocus())
        QtWidgets.QShortcut(QtGui.QKeySequence('Ctrl+O'), self, self.open_folder)

    def video_single_click(self):
        """Handle single click on video - pause/unpause"""
        self.toggle_play_pause()

    def video_double_click(self):
        """Handle double click on video - fullscreen"""
        self.toggle_fullscreen()

    def video_click(self, event):
        """Legacy method - replaced by eventFilter"""
        pass

    def position_click_seek(self, event):
        """Seek to position on click instead of drag"""
        if event.button() == QtCore.Qt.LeftButton:
            slider_width = self.position_slider.width()
            click_pos = event.x()
            value = int((click_pos / slider_width) * 1000)
            self.position_slider.setValue(value)
            self.set_position(value)

    def volume_wheel_event(self, event):
        """Handle mouse wheel for volume control"""
        delta = event.angleDelta().y()
        current_vol = self.volume_slider.value()
        if delta > 0:
            new_vol = min(100, current_vol + 5)
        else:
            new_vol = max(0, current_vol - 5)
        self.volume_slider.setValue(new_vol)

    def volume_up(self):
        """Increase volume by 5"""
        current_vol = self.volume_slider.value()
        self.volume_slider.setValue(min(100, current_vol + 5))

    def volume_down(self):
        """Decrease volume by 5"""
        current_vol = self.volume_slider.value()
        self.volume_slider.setValue(max(0, current_vol - 5))

    def toggle_mute(self):
        """Toggle mute"""
        if self.volume_slider.value() > 0:
            self.last_volume = self.volume_slider.value()
            self.volume_slider.setValue(0)
        else:
            vol = getattr(self, 'last_volume', 50)
            self.volume_slider.setValue(vol)

    def toggle_shuffle(self):
        """Toggle shuffle mode"""
        self.shuffle_mode = not self.shuffle_mode
        self.shuffle_action.setChecked(self.shuffle_mode)
        
        if self.shuffle_mode:
            # Store original and shuffle
            self.original_playlist = self.playlist.copy()
            random.shuffle(self.playlist)
        else:
            # Restore original order
            if self.original_playlist:
                self.playlist = self.original_playlist.copy()
        
        self.refresh_playlist()

    def filter_playlist(self):
        """Filter playlist based on search text"""
        search_text = self.search_box.text().lower()
        
        if isinstance(self.playlist_widget, QtWidgets.QListWidget):
            for i in range(self.playlist_widget.count()):
                item = self.playlist_widget.item(i)
                if search_text in item.text().lower():
                    item.setHidden(False)
                else:
                    item.setHidden(True)
        else:  # Tree widget
            def filter_tree_item(item):
                text = item.text(0).lower()
                has_visible_children = False
                is_folder = item.data(0, QtCore.Qt.UserRole) is None
                
                # Check children first
                for i in range(item.childCount()):
                    child = item.child(i)
                    if filter_tree_item(child):
                        has_visible_children = True
                
                # Show if matches search or has visible children or no search text
                matches = search_text in text
                should_show = matches or has_visible_children or not search_text
                
                # If it's a folder that matches, expand it to show contents
                if is_folder and matches and search_text:
                    item.setExpanded(True)
                
                item.setHidden(not should_show)
                return should_show
            
            root = self.playlist_widget.invisibleRootItem()
            for i in range(root.childCount()):
                filter_tree_item(root.child(i))

    def update_window_title(self):
        """Update window title with current playing video"""
        if self.current_playing_path:
            video_name = self.current_playing_path.stem
            self.setWindowTitle(f"{self.original_title} - {video_name}")
        else:
            self.setWindowTitle(self.original_title)

    def format_time(self, milliseconds):
        """Format time in mm:ss format"""
        seconds = int(milliseconds / 1000)
        mins = seconds // 60
        secs = seconds % 60
        return f"{mins:02d}:{secs:02d}"

    def seek_backward_small(self):
        """Seek backward by small amount (Z key)"""
        if self.vlc.is_playing():
            current_time = self.vlc.get_time() / 1000.0  # Convert to seconds
            new_time = max(0, current_time - self.small_seek_seconds)
            total_time = self.vlc.get_length() / 1000.0
            if total_time > 0:
                new_position = new_time / total_time
                self.vlc.set_position(new_position)

    def seek_forward_small(self):
        """Seek forward by small amount (X key)"""
        if self.vlc.is_playing():
            current_time = self.vlc.get_time() / 1000.0
            total_time = self.vlc.get_length() / 1000.0
            if total_time > 0:
                new_time = min(total_time, current_time + self.small_seek_seconds)
                new_position = new_time / total_time
                self.vlc.set_position(new_position)

    def seek_backward_large(self):
        """Seek backward by large amount (Ctrl+Z)"""
        if self.vlc.is_playing():
            current_time = self.vlc.get_time() / 1000.0
            new_time = max(0, current_time - self.large_seek_seconds)
            total_time = self.vlc.get_length() / 1000.0
            if total_time > 0:
                new_position = new_time / total_time
                self.vlc.set_position(new_position)

    def seek_forward_large(self):
        """Seek forward by large amount (Ctrl+X)"""
        if self.vlc.is_playing():
            current_time = self.vlc.get_time() / 1000.0
            total_time = self.vlc.get_length() / 1000.0
            if total_time > 0:
                new_time = min(total_time, current_time + self.large_seek_seconds)
                new_position = new_time / total_time
                self.vlc.set_position(new_position)
