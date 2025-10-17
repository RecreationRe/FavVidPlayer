from PyQt5 import QtWidgets, QtGui, QtCore
from pathlib import Path
from .scanner import scan_videos
from .meta import MetaStore, FAV_FOLDER_NAME
from .player import VLCPlayer


class PlayerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FavVidPlayer')
        self.resize(1200, 800)

        # central widget for video
        self.video_frame = QtWidgets.QFrame()
        self.setCentralWidget(self.video_frame)

        # right playlist dock
        self.playlist_dock = QtWidgets.QDockWidget('Playlist', self)
        self.playlist_widget = QtWidgets.QTreeWidget()
        self.playlist_widget.setHeaderLabel("Playlist")
        self.playlist_widget.itemClicked.connect(self.on_item_clicked)
        self.playlist_dock.setWidget(self.playlist_widget)
        self.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.playlist_dock)

        # control bar
        control = QtWidgets.QWidget()
        h = QtWidgets.QHBoxLayout()

        self.open_btn = QtWidgets.QPushButton('Open Folder')
        self.open_btn.clicked.connect(self.open_folder)
        h.addWidget(self.open_btn)

        # playback controls
        self.play_btn = QtWidgets.QPushButton('Play')
        self.play_btn.clicked.connect(self.toggle_play_pause)
        h.addWidget(self.play_btn)

        self.stop_btn = QtWidgets.QPushButton('Stop')
        self.stop_btn.clicked.connect(self.stop_playback)
        h.addWidget(self.stop_btn)

        # seek slider
        self.position_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.position_slider.setMaximum(1000)
        self.position_slider.sliderMoved.connect(self.set_position)
        h.addWidget(self.position_slider)

        # volume slider
        self.volume_label = QtWidgets.QLabel('Vol:')
        h.addWidget(self.volume_label)
        self.volume_slider = QtWidgets.QSlider(QtCore.Qt.Horizontal)
        self.volume_slider.setMaximum(100)
        self.volume_slider.setValue(50)
        self.volume_slider.setMaximumWidth(100)
        self.volume_slider.valueChanged.connect(self.set_volume)
        h.addWidget(self.volume_slider)

        self.speed_label = QtWidgets.QLabel('Speed:')
        h.addWidget(self.speed_label)
        self.speed_spin = QtWidgets.QDoubleSpinBox()
        self.speed_spin.setRange(0.25, 4.0)
        self.speed_spin.setSingleStep(0.25)
        self.speed_spin.setValue(1.0)
        self.speed_spin.valueChanged.connect(self.on_speed_changed)
        h.addWidget(self.speed_spin)

        self.repeat_checkbox = QtWidgets.QCheckBox('Repeat')
        self.repeat_checkbox.stateChanged.connect(self.on_repeat_changed)
        h.addWidget(self.repeat_checkbox)

        h.addStretch()

        # like/dislike/normal buttons
        self.normal_btn = QtWidgets.QPushButton('Normal')
        self.normal_btn.setStyleSheet('background-color: lightblue')
        self.normal_btn.clicked.connect(lambda: self.set_status('normal'))
        h.addWidget(self.normal_btn)

        self.like_btn = QtWidgets.QPushButton('Like')
        self.like_btn.setStyleSheet('background-color: lightgreen')
        self.like_btn.clicked.connect(lambda: self.set_status('liked'))
        h.addWidget(self.like_btn)

        self.dislike_btn = QtWidgets.QPushButton('Dislike')
        self.dislike_btn.setStyleSheet('background-color: lightcoral')
        self.dislike_btn.clicked.connect(lambda: self.set_status('disliked'))
        h.addWidget(self.dislike_btn)

        control.setLayout(h)
        self.addToolBar(QtCore.Qt.BottomToolBarArea, self._wrap_widget_as_toolbar(control))

        # state
        self.current_root = None
        self.playlist = []  # list of Path
        self.meta = None
        self.current_playing_path = None

        # settings
        self.settings = QtCore.QSettings()

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
        self.build_tree(self.playlist)

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

    def on_item_clicked(self, item, column):
        rel_path = item.data(0, QtCore.Qt.UserRole)
        if rel_path:  # it's a file
            p = self.current_root / rel_path
            self.play_file(p)
        else:  # it's a folder, toggle expand
            item.setExpanded(not item.isExpanded())

    def play_file(self, path: Path):
        if not path.exists():
            QtWidgets.QMessageBox.warning(self, 'Missing', f'File not found: {path}')
            return
        self.current_playing_path = path
        self.vlc.play(path)
        self.play_btn.setText('Pause')
        meta = self.meta.get(str(path.relative_to(self.current_root)))
        speed = meta.get('speed', 1.0)
        QtCore.QTimer.singleShot(300, lambda: self.vlc.set_rate(speed))
        self.repeat_checkbox.setChecked(meta.get('repeat', False))
        meta['last_played'] = QtCore.QDateTime.currentDateTime().toString()
        self.meta.set(str(path.relative_to(self.current_root)), meta)

    def toggle_play_pause(self):
        if self.vlc.is_playing():
            self.vlc.pause()
            self.play_btn.setText('Play')
        else:
            # resume
            self.vlc.player.play()
            self.play_btn.setText('Pause')

    def stop_playback(self):
        self.vlc.stop()
        self.play_btn.setText('Play')

    def set_position(self, position):
        self.vlc.set_position(position / 1000.0)

    def set_volume(self, volume):
        self.vlc.set_volume(volume)

    def update_ui(self):
        if self.vlc.is_playing():
            pos = self.vlc.get_position()
            self.position_slider.setValue(int(pos * 1000))

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

    def on_speed_changed(self, val):
        self.vlc.set_rate(val)
        cur = self.current_playing_rel()
        if cur:
            m = self.meta.get(cur)
            m['speed'] = val
            self.meta.set(cur, m)

    def on_repeat_changed(self, state):
        cur = self.current_playing_rel()
        if cur:
            m = self.meta.get(cur)
            m['repeat'] = bool(state)
            self.meta.set(cur, m)

    def check_mouse_edge(self):
        pos = QtGui.QCursor.pos()
        local_pos = self.mapFromGlobal(pos)
        w = self.width()
        if local_pos.x() >= w - 40:
            if self.playlist_dock.isHidden():
                self.playlist_dock.show()
        else:
            if not self.playlist_dock.isHidden() and local_pos.x() < w - 200:
                self.playlist_dock.hide()
