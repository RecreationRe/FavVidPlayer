"""Main application window - refactored for modularity"""
from pathlib import Path
from PyQt5 import QtWidgets, QtCore
from ..controllers.application import ApplicationController
from .toolbar import ToolbarManager
from .dialogs import SettingsDialog, HotkeysDialog
from .playlist import PlaylistManager
from .shortcuts import ShortcutsManager
from .interactions import VideoInteractionsManager
from .handlers import SignalHandlers


class PlayerWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle('FavVidPlayer')
        self.resize(1200, 800)
        
        self.controller = ApplicationController()
        self.toolbar_mgr = ToolbarManager(self)
        self.playlist_mgr = PlaylistManager(self)
        self.shortcuts_mgr = ShortcutsManager(self)
        self.interactions_mgr = VideoInteractionsManager(self)
        self.handlers = SignalHandlers(self)
        self.view_mode = 'flat'
        self.last_volume = 50
        self.is_fullscreen = False
        
        # Timer for updating playback position
        self.update_timer = QtCore.QTimer()
        self.update_timer.timeout.connect(self._update_playback_display)
        self.update_timer.start(200)  # Update every 200ms
        
        # Fullscreen auto-hide timer
        self.fullscreen_hide_timer = QtCore.QTimer()
        self.fullscreen_hide_timer.timeout.connect(self._hide_fullscreen_ui)
        
        # Track mouse position for fullscreen
        self.last_mouse_y = 0
        self.setMouseTracking(True)
        
        self._setup_ui()
        self._load_settings()
    
    def _setup_ui(self):
        self._setup_menu_bar()
        self._setup_central_widget()
        self.toolbar_mgr.setup()
        self.playlist_mgr.setup()
        self._setup_status_bar()
        self.shortcuts_mgr.setup_all()
        self.interactions_mgr.setup()
        self.handlers.setup()
    
    def _setup_menu_bar(self):
        menu_bar = self.menuBar()
        file_menu = menu_bar.addMenu('File')
        file_menu.addAction('Open Folder', self.open_folder, 'Ctrl+O')
        file_menu.addSeparator()
        file_menu.addAction('Save Settings', self._save_settings, 'Ctrl+S')
        file_menu.addSeparator()
        file_menu.addAction('Exit', self.close)
        
        view_menu = menu_bar.addMenu('View')
        self.explorer_action = view_menu.addAction('File Explorer Mode')
        self.explorer_action.setCheckable(True)
        self.explorer_action.triggered.connect(self._toggle_view_mode)
        
        view_menu.addSeparator()
        self.auto_hide_action = view_menu.addAction('Auto-hide Playlist')
        self.auto_hide_action.setCheckable(True)
        
        help_menu = menu_bar.addMenu('Help')
        help_menu.addAction('Settings', self.show_settings)
        help_menu.addAction('Hotkeys', self.show_hotkeys)
    
    def _setup_central_widget(self):
        self.video_frame = QtWidgets.QFrame()
        self.video_frame.setStyleSheet('background-color: black;')
        self.setCentralWidget(self.video_frame)
        self.controller.set_playback_service(self.video_frame)
    
    def _setup_status_bar(self):
        self.status_bar = self.statusBar()
        self.status_label = QtWidgets.QLabel('Ready')
        self.status_bar.addWidget(self.status_label)
    
    def _load_settings(self):
        settings = self.controller.settings_service
        vol = settings.get('volume', 50)
        self.toolbar_mgr.volume_slider.setValue(vol)
        self.last_volume = vol
        
        last_folder = settings.get('last_folder')
        if last_folder and Path(last_folder).exists():
            self.controller.load_folder(last_folder)
    
    def open_folder(self):
        folder = QtWidgets.QFileDialog.getExistingDirectory(self, 'Select Video Folder')
        if folder:
            self.controller.load_folder(Path(folder))
    
    def toggle_play_pause(self):
        self.controller.toggle_play_pause()
        is_playing = self.controller.get_is_playing()
        self.toolbar_mgr.update_play_icon(is_playing)
    
    def stop_playback(self):
        if self.controller.playback_service:
            self.controller.playback_service.stop()
        self.toolbar_mgr.update_play_icon(False)
    
    def previous_video(self):
        self.controller.play_previous()
    
    def next_video(self):
        self.controller.play_next()
    
    def seek_video(self, value):
        if self.controller.playback_service and self.controller.playback_service.current_video:
            # value is 0-1000, convert to 0.0-1.0 normalized position
            position = value / 1000.0
            self.controller.set_video_position(position)
    
    def seek_forward(self):
        if self.controller.playback_service:
            interval = self.controller.settings_service.get('small_seek_interval', 5)
            self.controller.playback_service.seek_forward(interval)
    
    def seek_backward(self):
        if self.controller.playback_service:
            interval = self.controller.settings_service.get('small_seek_interval', 5)
            self.controller.playback_service.seek_backward(interval)
    
    def seek_forward_large(self):
        if self.controller.playback_service:
            interval = self.controller.settings_service.get('large_seek_interval', 30)
            self.controller.playback_service.seek_forward(interval)
    
    def seek_backward_large(self):
        if self.controller.playback_service:
            interval = self.controller.settings_service.get('large_seek_interval', 30)
            self.controller.playback_service.seek_backward(interval)
    
    def set_volume(self, value):
        self.controller.set_volume(value)
        self.last_volume = value if value > 0 else self.last_volume
    
    def volume_up(self):
        new_vol = min(100, self.toolbar_mgr.volume_slider.value() + 5)
        self.toolbar_mgr.volume_slider.setValue(new_vol)
    
    def volume_down(self):
        new_vol = max(0, self.toolbar_mgr.volume_slider.value() - 5)
        self.toolbar_mgr.volume_slider.setValue(new_vol)
    
    def toggle_mute(self):
        current_vol = self.toolbar_mgr.volume_slider.value()
        if current_vol > 0:
            self.last_volume = current_vol
            self.toolbar_mgr.volume_slider.setValue(0)
        else:
            self.toolbar_mgr.volume_slider.setValue(self.last_volume)
    
    def toggle_fullscreen(self):
        if self.isFullScreen():
            self.showNormal()
        else:
            self.showFullScreen()
    
    def set_rating(self, status):
        if self.controller.playback_service and self.controller.playback_service.current_video:
            self.controller.set_video_rating(
                self.controller.playback_service.current_video,
                status
            )
            self.playlist_mgr.update_colors(self.controller.playlist.videos)
    
    def search_playlist(self, query):
        results = self.controller.search_playlist(query)
        self.playlist_mgr.update_view(results if query else self.controller.playlist.videos)
    
    def _on_playlist_item_selected(self):
        """Handle playlist item selection"""
        selected = self.playlist_mgr.playlist_view.selectedItems()
        if not selected:
            return
        
        if isinstance(self.playlist_mgr.playlist_view, QtWidgets.QListWidget):
            # Flat list view - get by relative path
            rel_path = selected[0].text()
            video = next((v for v in self.controller.playlist.videos 
                         if str(v.path.relative_to(self.playlist_mgr.root_path)) == rel_path), None)
        else:
            # Tree view - get from UserRole data
            video = selected[0].data(0, QtCore.Qt.UserRole)
        
        if video:
            self.controller.play_video(video)
    
    def show_settings(self):
        dialog = SettingsDialog(self, self.controller)
        if dialog.exec_() == QtWidgets.QDialog.Accepted:
            self.toolbar_mgr.volume_slider.setValue(dialog.volume_slider.value())
    
    def show_hotkeys(self):
        dialog = HotkeysDialog(self)
        dialog.exec_()
    
    def _toggle_shuffle(self):
        self.toolbar_mgr.shuffle_btn.setChecked(not self.toolbar_mgr.shuffle_btn.isChecked())
    
    def _on_shuffle_toggled(self, checked):
        if checked:
            self.controller.enable_shuffle()
        else:
            self.controller.disable_shuffle()
    
    def _toggle_repeat(self):
        self.controller.toggle_repeat()
        mode = self.controller.settings_service.app_settings.repeat_mode
        text = {'off': '🔁 Off', 'one': '🔂 Once', 'all': '🔁 All'}.get(mode, '🔁 Off')
        self.toolbar_mgr.repeat_btn.setText(text)
    
    def _toggle_auto_hide(self):
        self.auto_hide_action.setChecked(not self.auto_hide_action.isChecked())
        if not self.auto_hide_action.isChecked():
            self.playlist_mgr.playlist_dock.show()
    
    def _toggle_view_mode(self):
        """Toggle between flat list and file explorer tree view"""
        is_explorer = self.explorer_action.isChecked()
        self.playlist_mgr.set_explorer_mode(is_explorer)
        view_type = 'File Explorer' if is_explorer else 'Flat List'
        self.status_label.setText(f'View mode: {view_type}')
        self.controller.settings_service.set('explorer_mode', is_explorer)
    
    def toggle_fullscreen(self):
        """Toggle fullscreen with auto-hiding UI"""
        self.is_fullscreen = not self.is_fullscreen
        if self.is_fullscreen:
            self.showFullScreen()
            self.menuBar().hide()
            self.toolbar_mgr.toolbar.hide()
            self.playlist_mgr.playlist_dock.hide()
            self.statusBar().hide()
            self.fullscreen_hide_timer.start(3000)  # Auto-hide after 3 seconds of no motion
        else:
            self.showNormal()
            self.menuBar().show()
            self.toolbar_mgr.toolbar.show()
            self.playlist_mgr.playlist_dock.show()
            self.statusBar().show()
            self.fullscreen_hide_timer.stop()
    
    def toggle_playlist(self):
        """Toggle playlist dock visibility"""
        self.playlist_mgr.playlist_dock.setVisible(not self.playlist_mgr.playlist_dock.isVisible())
    
    def _hide_fullscreen_ui(self):
        """Hide fullscreen UI elements"""
        if self.is_fullscreen and (self.last_mouse_y > 50 and self.last_mouse_y < self.height() - 50):
            self.menuBar().hide()
            self.toolbar_mgr.toolbar.hide()
            self.statusBar().hide()
    
    def _show_fullscreen_ui(self):
        """Show fullscreen UI elements"""
        if self.is_fullscreen:
            self.menuBar().show()
            self.toolbar_mgr.toolbar.show()
            self.statusBar().show()
            self.fullscreen_hide_timer.start(3000)
    
    def mouseMoveEvent(self, event):
        """Handle mouse movement in fullscreen"""
        self.last_mouse_y = event.y()
        if self.is_fullscreen and (event.y() < 50 or event.y() > self.height() - 50):
            self._show_fullscreen_ui()
        super().mouseMoveEvent(event)
    
    def _focus_search(self):
        self.playlist_mgr.focus_search()
    
    def _save_settings(self):
        self.controller.settings_service.set('volume', self.toolbar_mgr.volume_slider.value())
        self.status_label.setText('Settings saved')
    
    def _update_playback_display(self):
        """Update slider position and time label with current playback state"""
        if not self.controller.playback_service or not self.controller.playback_service.current_video:
            return
        
        current_ms = self.controller.playback_service.get_time()
        total_ms = self.controller.playback_service.get_length()
        
        if total_ms <= 0:
            return
        
        # Update slider without triggering sliderMoved signal
        self.toolbar_mgr.position_slider.blockSignals(True)
        position_normalized = (current_ms / total_ms) * 1000.0  # Slider max is 1000
        self.toolbar_mgr.position_slider.setValue(int(position_normalized))
        self.toolbar_mgr.position_slider.blockSignals(False)
        
        # Update time label
        current_sec = current_ms // 1000
        total_sec = total_ms // 1000
        current_time = f'{current_sec // 60:02d}:{current_sec % 60:02d}'
        total_time = f'{total_sec // 60:02d}:{total_sec % 60:02d}'
        self.toolbar_mgr.time_label.setText(f'{current_time} / {total_time}')
    
    def _on_auto_hide_timeout(self):
        if self.auto_hide_action.isChecked():
            self.playlist_mgr.playlist_dock.hide()
            self.playlist_mgr.playlist_was_visible = False
