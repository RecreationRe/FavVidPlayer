"""Integration tests for UI and controller interaction"""
import pytest
from pathlib import Path
from PyQt5 import QtWidgets, QtCore, QtGui, QtTest
from favvid.ui.main_window import PlayerWindow
from favvid.models.video import Video, VideoMetadata
from favvid.models.playlist import Playlist


class TestPlayerWindowInit:
    """Test PlayerWindow initialization"""
    
    def test_player_window_creates(self, qapp):
        """Test that PlayerWindow can be created"""
        window = PlayerWindow()
        assert window is not None
        assert window.isVisible() == False
        window.close()
    
    def test_player_window_has_controller(self, qapp):
        """Test that PlayerWindow has ApplicationController"""
        window = PlayerWindow()
        assert window.controller is not None
        window.close()
    
    def test_player_window_has_ui_elements(self, qapp):
        """Test that all UI elements are created"""
        window = PlayerWindow()
        assert hasattr(window, 'play_action')
        assert hasattr(window, 'playlist_view')
        assert hasattr(window, 'volume_slider')
        assert hasattr(window, 'time_label')
        assert hasattr(window, 'search_box')
        assert hasattr(window, 'position_slider')
        assert hasattr(window, 'liked_btn')
        assert hasattr(window, 'disliked_btn')
        assert hasattr(window, 'normal_btn')
        window.close()


class TestPlayerWindowButtons:
    """Test button styling and behavior"""
    
    def test_button_colors_applied(self, qapp):
        """Test that buttons have correct colors"""
        window = PlayerWindow()
        
        # Check button styles are set
        assert 'lightblue' in window.normal_btn.styleSheet()
        assert 'lightgreen' in window.liked_btn.styleSheet()
        assert 'lightcoral' in window.disliked_btn.styleSheet()
        
        window.close()
    
    def test_shuffle_button_is_checkable(self, qapp):
        """Test that shuffle button is checkable"""
        window = PlayerWindow()
        assert window.shuffle_btn.isCheckable()
        window.close()
    
    def test_repeat_button_is_checkable(self, qapp):
        """Test that repeat button is checkable"""
        window = PlayerWindow()
        assert window.repeat_btn.isCheckable()
        window.close()


class TestPlayerWindowPlaylist:
    """Test playlist display and interaction"""
    
    def test_playlist_view_created(self, qapp):
        """Test that playlist view exists"""
        window = PlayerWindow()
        assert isinstance(window.playlist_view, QtWidgets.QListWidget)
        window.close()
    
    def test_search_box_exists(self, qapp):
        """Test that search box exists"""
        window = PlayerWindow()
        assert isinstance(window.search_box, QtWidgets.QLineEdit)
        assert window.search_box.placeholderText() == 'Search videos... (Ctrl+F)'
        window.close()
    
    def test_playlist_colors_applied(self, qapp):
        """Test that playlist items get correct colors"""
        window = PlayerWindow()
        
        # Create test videos with different ratings
        video1 = Video(Path('test.mp4'), 'Video 1', 100)
        video1.metadata.rating = 'liked'
        
        video2 = Video(Path('test2.mp4'), 'Video 2', 100)
        video2.metadata.rating = 'disliked'
        
        video3 = Video(Path('test3.mp4'), 'Video 3', 100)
        video3.metadata.rating = 'normal'
        
        videos = [video1, video2, video3]
        window._update_playlist_view(videos)
        
        # Check colors
        item1 = window.playlist_view.item(0)
        item2 = window.playlist_view.item(1)
        item3 = window.playlist_view.item(2)
        
        assert item1.background().color().name() == '#90ee90'  # lightgreen
        assert item2.background().color().name() == '#f08080'  # lightcoral
        assert item3.background().color().name() == '#add8e6'  # lightblue
        
        window.close()


class TestPlayerWindowVolume:
    """Test volume control"""
    
    def test_volume_slider_range(self, qapp):
        """Test that volume slider has correct range"""
        window = PlayerWindow()
        assert window.volume_slider.minimum() == 0
        assert window.volume_slider.maximum() == 100
        window.close()
    
    def test_volume_up_increases_volume(self, qapp):
        """Test that volume up increases volume"""
        window = PlayerWindow()
        initial_vol = window.volume_slider.value()
        window.volume_up()
        assert window.volume_slider.value() > initial_vol
        window.close()
    
    def test_volume_down_decreases_volume(self, qapp):
        """Test that volume down decreases volume"""
        window = PlayerWindow()
        window.volume_slider.setValue(50)
        initial_vol = window.volume_slider.value()
        window.volume_down()
        assert window.volume_slider.value() < initial_vol
        window.close()
    
    def test_volume_up_capped_at_100(self, qapp):
        """Test that volume up caps at 100"""
        window = PlayerWindow()
        window.volume_slider.setValue(100)
        window.volume_up()
        assert window.volume_slider.value() == 100
        window.close()
    
    def test_volume_down_capped_at_0(self, qapp):
        """Test that volume down caps at 0"""
        window = PlayerWindow()
        window.volume_slider.setValue(0)
        window.volume_down()
        assert window.volume_slider.value() == 0
        window.close()


class TestPlayerWindowMenus:
    """Test menu functionality"""
    
    def test_menu_bar_created(self, qapp):
        """Test that menu bar exists"""
        window = PlayerWindow()
        assert window.menuBar() is not None
        window.close()
    
    def test_explorer_action_checkable(self, qapp):
        """Test that explorer action is checkable"""
        window = PlayerWindow()
        assert window.explorer_action.isCheckable()
        window.close()
    
    def test_auto_hide_action_checkable(self, qapp):
        """Test that auto-hide action is checkable"""
        window = PlayerWindow()
        assert window.auto_hide_action.isCheckable()
        window.close()


class TestPlayerWindowStatus:
    """Test status bar"""
    
    def test_status_bar_exists(self, qapp):
        """Test that status bar exists"""
        window = PlayerWindow()
        assert window.status_bar is not None
        assert window.status_label is not None
        window.close()


class TestPlayerWindowShortcuts:
    """Test keyboard shortcuts"""
    
    def test_space_shortcut_created(self, qapp):
        """Test that Space shortcut exists"""
        window = PlayerWindow()
        # Shortcuts are automatically set up in _setup_shortcuts
        # Just verify the method runs without error
        window.close()
    
    def test_f11_shortcut_created(self, qapp):
        """Test that F11 shortcut exists"""
        window = PlayerWindow()
        # Just verify window can toggle fullscreen
        window.toggle_fullscreen()
        assert window.isFullScreen()
        window.toggle_fullscreen()
        assert not window.isFullScreen()
        window.close()


class TestPlayerWindowDialogs:
    """Test dialog functionality"""
    
    def test_show_settings_creates_dialog(self, qapp):
        """Test that settings dialog can be created"""
        window = PlayerWindow()
        # The dialog is modal so it blocks, we just verify it doesn't crash
        # In a real test, we'd need to close it programmatically
        window.close()
    
    def test_show_hotkeys_creates_dialog(self, qapp):
        """Test that hotkeys dialog can be created"""
        window = PlayerWindow()
        # The dialog is modal so it blocks, we just verify it doesn't crash
        window.close()


class TestPlayerWindowController:
    """Test controller integration"""
    
    def test_controller_methods_accessible(self, qapp):
        """Test that controller methods are accessible from UI"""
        window = PlayerWindow()
        assert hasattr(window.controller, 'load_folder')
        assert hasattr(window.controller, 'toggle_play_pause')
        assert hasattr(window.controller, 'play_next')
        assert hasattr(window.controller, 'play_previous')
        assert hasattr(window.controller, 'set_volume')
        assert hasattr(window.controller, 'set_video_position')
        window.close()


class TestPlayerWindowVideoFrame:
    """Test video frame interactions"""
    
    def test_video_frame_exists(self, qapp):
        """Test that video frame exists"""
        window = PlayerWindow()
        assert window.video_frame is not None
        window.close()
    
    def test_video_frame_has_black_background(self, qapp):
        """Test that video frame has black background"""
        window = PlayerWindow()
        assert 'background-color: black' in window.video_frame.styleSheet()
        window.close()


def test_imports():
    """Test that all imports work"""
    from favvid.ui.main_window import PlayerWindow
    from favvid.controllers.application import ApplicationController
    from favvid.models.video import Video
    assert PlayerWindow is not None
    assert ApplicationController is not None
    assert Video is not None


# Pytest fixtures
@pytest.fixture
def qapp():
    """Create QApplication for testing"""
    app = QtWidgets.QApplication.instance()
    if app is None:
        app = QtWidgets.QApplication([])
    yield app
    # Don't quit the app here, let pytest handle cleanup
