import sys
import os
import json
import shutil
from pathlib import Path
from PyQt5 import QtWidgets, QtGui, QtCore
import vlc

VIDEO_EXTS = {'.mp4', '.mkv', '.avi', '.webm', '.mov', '.flv', '.wmv', '.mpg', '.mpeg', '.gif'}
META_FILENAME = '.favmeta.json'
FAV_FOLDER_NAME = 'Favorites_FavVidPlayer'


def scan_videos(root: Path):
    files = []
    for p in root.rglob('*'):
        if p.is_file() and p.suffix.lower() in VIDEO_EXTS:
            files.append(p)
    files.sort()
    return files


class PlayerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FavVidPlayer')
        self.resize(1200, 800)

        # central widget for video
        self.video_frame = QtWidgets.QFrame()
        self.setCentralWidget(self.video_frame)

        # VLC
        self.instance = vlc.Instance()
        self.mediaplayer = self.instance.media_player_new()

        # right playlist dock
        self.playlist_dock = QtWidgets.QDockWidget('Playlist', self)
        self.playlist_widget = QtWidgets.QListWidget()
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
        self.meta = {}
        self.current_playing_path = None  # track currently playing file

        # mouse tracking for auto-hide
        self.setMouseTracking(True)
        self.playlist_dock.setMouseTracking(True)
        self.playlist_hidden = False

        # timer to check edge
        self.edge_timer = QtCore.QTimer()
        self.edge_timer.timeout.connect(self.check_mouse_edge)
        self.edge_timer.start(200)

        # timer to update position slider
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self.update_ui)
        self.update_timer.start(100)

        # video frame native handle setup
        if sys.platform.startswith('win'):
            self.mediaplayer.set_hwnd(self.video_frame.winId())
        else:
            self.mediaplayer.set_xwindow(self.video_frame.winId())

    def _wrap_widget_as_toolbar(self, widget):
        tb = QtWidgets.QToolBar()
        tb.addWidget(widget)
        return tb

    def open_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select folder to scan')
        if not folder:
            return
        root = Path(folder)
        self.current_root = root
        self.load_meta()
        self.playlist = scan_videos(root)
        self.refresh_playlist()
        # ensure favorites folder exists
        (root / FAV_FOLDER_NAME).mkdir(exist_ok=True)

    def refresh_playlist(self):
        self.playlist_widget.clear()
        for p in self.playlist:
            item = QtWidgets.QListWidgetItem(str(p.relative_to(self.current_root)))
            status = self.meta.get(str(p.relative_to(self.current_root)), {}).get('status')
            if status == 'liked':
                item.setBackground(QtGui.QColor('lightgreen'))
            elif status == 'disliked':
                item.setBackground(QtGui.QColor('lightcoral'))
            self.playlist_widget.addItem(item)

    def on_item_clicked(self, item):
        rel = item.text()
        p = self.current_root / rel
        self.play_file(p)

    def play_file(self, path: Path):
        if not path.exists():
            QtWidgets.QMessageBox.warning(self, 'Missing', f'File not found: {path}')
            return
        self.current_playing_path = path
        media = self.instance.media_new(str(path))
        self.mediaplayer.set_media(media)
        self.mediaplayer.play()
        self.play_btn.setText('Pause')
        # apply saved speed if exists
        meta = self.meta.setdefault(str(path.relative_to(self.current_root)), {})
        speed = meta.get('speed', 1.0)
        QtCore.QTimer.singleShot(300, lambda: self.mediaplayer.set_rate(speed))
        # set repeat
        self.repeat_checkbox.setChecked(meta.get('repeat', False))
        # remember last played
        meta['last_played'] = QtCore.QDateTime.currentDateTime().toString()
        self.save_meta()

    def on_speed_changed(self, val):
        try:
            self.mediaplayer.set_rate(val)
        except Exception:
            pass
        # set default for current file
        cur = self.current_playing_rel()
        if cur:
            meta = self.meta.setdefault(cur, {})
            meta['speed'] = val
            self.save_meta()

    def on_repeat_changed(self, state):
        cur = self.current_playing_rel()
        if cur:
            meta = self.meta.setdefault(cur, {})
            meta['repeat'] = bool(state)
            self.save_meta()

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
        meta = self.meta.setdefault(cur, {})
        prev = meta.get('status')
        meta['status'] = status
        self.save_meta()
        # update playlist coloring
        self.refresh_playlist()
        # handle favorites folder
        src = self.current_root / cur
        fav_dir = self.current_root / FAV_FOLDER_NAME
        fav_path = fav_dir / Path(cur).name
        try:
            if status == 'liked':
                # create hardlink if possible
                try:
                    if fav_path.exists():
                        fav_path.unlink()
                    os.link(str(src), str(fav_path))
                except Exception:
                    shutil.copy2(str(src), str(fav_path))
            else:
                # remove from favorites if exists
                if fav_path.exists():
                    fav_path.unlink()
        except Exception as e:
            QtWidgets.QMessageBox.warning(self, 'Favorites', f'Could not update favorites: {e}')

    def load_meta(self):
        self.meta = {}
        if not self.current_root:
            return
        path = self.current_root / META_FILENAME
        if path.exists():
            try:
                with open(path, 'r', encoding='utf-8') as f:
                    self.meta = json.load(f)
            except Exception:
                self.meta = {}

    def save_meta(self):
        if not self.current_root:
            return
        path = self.current_root / META_FILENAME
        try:
            with open(path, 'w', encoding='utf-8') as f:
                json.dump(self.meta, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print('Failed to save meta:', e)

    def check_mouse_edge(self):
        pos = QtGui.QCursor.pos()
        geom = self.geometry()
        global_right = geom.right() + self.frameGeometry().x() - self.frameGeometry().x()
        # get global geometry
        win_rect = self.frameGeometry()
        right_edge = win_rect.right()
        # if cursor is within 30px of right edge of window, show playlist
        local_pos = self.mapFromGlobal(pos)
        w = self.width()
        if local_pos.x() >= w - 40:
            if self.playlist_hidden:
                self.playlist_dock.show()
                self.playlist_hidden = False
        else:
            # if cursor not near edge, hide
            if not self.playlist_hidden and local_pos.x() < w - 200:
                self.playlist_dock.hide()
                self.playlist_hidden = True

    def toggle_play_pause(self):
        if self.mediaplayer.is_playing():
            self.mediaplayer.pause()
            self.play_btn.setText('Play')
        else:
            self.mediaplayer.play()
            self.play_btn.setText('Pause')

    def stop_playback(self):
        self.mediaplayer.stop()
        self.play_btn.setText('Play')

    def set_position(self, position):
        self.mediaplayer.set_position(position / 1000.0)

    def set_volume(self, volume):
        self.mediaplayer.audio_set_volume(volume)

    def update_ui(self):
        # update position slider
        if self.mediaplayer.is_playing():
            pos = self.mediaplayer.get_position()
            self.position_slider.setValue(int(pos * 1000))


if __name__ == '__main__':
    app = QtWidgets.QApplication(sys.argv)
    win = PlayerWindow()
    win.show()
    sys.exit(app.exec_())
