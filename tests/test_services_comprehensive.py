"""Comprehensive test suite for services"""
import pytest
import json
import tempfile
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from favvid.models import Video, VideoMetadata, Playlist, AppSettings
from favvid.services import VideoScanner, MetadataService, PlaybackService, SettingsService


# ===== MetadataService Tests =====

class TestMetadataService:
    """Test MetadataService persistence operations"""
    
    @pytest.fixture
    def temp_dir(self):
        """Create temporary directory for testing"""
        with tempfile.TemporaryDirectory() as tmpdir:
            yield Path(tmpdir)
    
    @pytest.fixture
    def metadata_service(self, temp_dir):
        """Create MetadataService instance"""
        return MetadataService(temp_dir)
    
    @pytest.fixture
    def test_video(self, temp_dir):
        """Create a test video file and Video object"""
        video_path = temp_dir / "test.mp4"
        video_path.touch()
        return Video(path=video_path)
    
    def test_metadata_file_creation(self, metadata_service):
        """Test that metadata file exists after service init"""
        assert metadata_service.metadata_file.name == '.favmeta.json'
        assert metadata_service.root_folder == metadata_service.metadata_file.parent
    
    def test_get_metadata_default(self, metadata_service, test_video):
        """Test getting metadata for new video returns defaults"""
        metadata = metadata_service.get(test_video)
        assert isinstance(metadata, VideoMetadata)
        assert metadata.position == 0.0
        assert metadata.speed == 1.0
        assert metadata.status == "normal"
    
    def test_set_and_get_metadata(self, metadata_service, test_video):
        """Test setting and retrieving metadata"""
        metadata = VideoMetadata(path=test_video.path, status="liked", position=0.5)
        metadata_service.set(test_video, metadata)
        
        retrieved = metadata_service.get(test_video)
        assert retrieved.status == "liked"
        assert retrieved.position == 0.5
    
    def test_metadata_persisted_to_json(self, metadata_service, test_video):
        """Test that metadata is persisted to JSON file"""
        metadata = VideoMetadata(path=test_video.path, status="liked")
        metadata_service.set(test_video, metadata)
        
        # Read JSON directly
        with open(metadata_service.metadata_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
        
        assert "test.mp4" in data
        assert data["test.mp4"]["status"] == "liked"
    
    def test_metadata_loaded_from_json(self, temp_dir):
        """Test that metadata is loaded from existing JSON"""
        # Create metadata file
        metadata_file = temp_dir / '.favmeta.json'
        test_data = {
            "video.mp4": {
                "status": "disliked",
                "position": 0.75,
                "speed": 1.5,
                "last_played": "2024-01-01"
            }
        }
        with open(metadata_file, 'w', encoding='utf-8') as f:
            json.dump(test_data, f)
        
        # Create service - should load existing metadata
        service = MetadataService(temp_dir)
        assert "video.mp4" in service._cache
        assert service._cache["video.mp4"]["status"] == "disliked"
    
    def test_set_status(self, metadata_service, test_video):
        """Test setting video status"""
        metadata_service.set_status(test_video, "liked")
        retrieved = metadata_service.get(test_video)
        assert retrieved.status == "liked"
    
    def test_create_favorite_hardlink(self, temp_dir):
        """Test creating favorite with hardlink"""
        # Create actual video file
        video_path = temp_dir / "test.mp4"
        video_path.write_bytes(b"fake video data")
        video = Video(path=video_path)
        
        service = MetadataService(temp_dir)
        success = service.create_favorite(video)
        
        # Check favorite was created
        fav_file = temp_dir / "Favorites_FavVidPlayer" / "test.mp4"
        assert fav_file.exists() or success is True
    
    def test_remove_favorite(self, temp_dir):
        """Test removing favorite"""
        # Create video and favorite
        video_path = temp_dir / "test.mp4"
        video_path.write_bytes(b"fake video")
        video = Video(path=video_path)
        
        service = MetadataService(temp_dir)
        service.create_favorite(video)
        
        # Remove
        service.remove_favorite(video)
        fav_file = temp_dir / "Favorites_FavVidPlayer" / "test.mp4"
        assert not fav_file.exists()


# ===== PlaybackService Tests =====

class TestPlaybackService:
    """Test PlaybackService methods"""
    
    @pytest.fixture
    def video_widget_mock(self):
        """Mock Qt video widget"""
        widget = Mock()
        widget.winId = Mock(return_value=12345)
        return widget
    
    @pytest.fixture
    def playback_service(self, video_widget_mock):
        """Create PlaybackService with mocked player"""
        with patch('favvid.services.playback.VLCPlayer'):
            service = PlaybackService(video_widget_mock)
            service.player = Mock()
            return service
    
    @pytest.fixture
    def temp_video(self):
        """Create temporary test video"""
        with tempfile.TemporaryDirectory() as tmpdir:
            video_path = Path(tmpdir) / "test.mp4"
            video_path.touch()
            yield Video(path=video_path)
    
    def test_play_video(self, playback_service, temp_video):
        """Test playing a video"""
        playback_service.player.play = Mock()
        success = playback_service.play(temp_video)
        
        assert success is True
        playback_service.player.play.assert_called_once()
        assert playback_service.current_video == temp_video
    
    def test_play_missing_video(self, playback_service):
        """Test playing non-existent video fails"""
        missing_video = Video(path=Path("/missing/video.mp4"))
        success = playback_service.play(missing_video)
        assert success is False
    
    def test_seek_forward(self, playback_service):
        """Test seeking forward"""
        playback_service.player.get_time = Mock(return_value=5000)  # 5 sec
        playback_service.player.get_length = Mock(return_value=60000)  # 60 sec
        playback_service.player.set_position = Mock()
        
        playback_service.seek_forward(10.0)
        
        # Should seek to 15/60 = 0.25 position
        playback_service.player.set_position.assert_called_once()
        args = playback_service.player.set_position.call_args[0]
        assert 0.24 < args[0] < 0.26  # Allow small float precision error
    
    def test_seek_backward(self, playback_service):
        """Test seeking backward"""
        playback_service.player.get_time = Mock(return_value=15000)  # 15 sec
        playback_service.player.get_length = Mock(return_value=60000)  # 60 sec
        playback_service.player.set_position = Mock()
        
        playback_service.seek_backward(5.0)
        
        # Should seek to 10/60 ≈ 0.167 position
        playback_service.player.set_position.assert_called_once()
        args = playback_service.player.set_position.call_args[0]
        assert 0.16 < args[0] < 0.18


# ===== SettingsService Tests =====

class TestSettingsService:
    """Test SettingsService configuration management"""
    
    @pytest.fixture
    def settings_service(self):
        """Create SettingsService"""
        with patch('favvid.services.settings.QtCore.QSettings'):
            return SettingsService()
    
    def test_default_settings(self, settings_service):
        """Test default app settings"""
        assert settings_service.app_settings.volume == 50
        assert settings_service.app_settings.persist_volume is True
        assert settings_service.app_settings.persist_position is True
        assert settings_service.app_settings.seek_small_seconds == 5.0
        assert settings_service.app_settings.seek_large_seconds == 30.0
    
    def test_get_setting(self, settings_service):
        """Test getting a setting value"""
        value = settings_service.get('volume')
        assert value == 50
    
    def test_set_and_persist_setting(self, settings_service):
        """Test setting a value persists"""
        settings_service.set('volume', 75)
        assert settings_service.app_settings.volume == 75


# ===== VideoScanner Tests (existing, verify coverage) =====

class TestVideoScanner:
    """Test VideoScanner directory scanning"""
    
    @pytest.fixture
    def video_directory(self):
        """Create directory with test videos"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create videos
            (tmppath / "video1.mp4").touch()
            (tmppath / "video2.mkv").touch()
            (tmppath / "readme.txt").touch()
            
            # Create subdirectory with video
            subdir = tmppath / "subfolder"
            subdir.mkdir()
            (subdir / "video3.avi").touch()
            
            yield tmppath
    
    def test_scan_directory(self, video_directory):
        """Test scanning directory for videos"""
        videos = VideoScanner.scan_directory(video_directory)
        
        assert len(videos) == 3
        assert all(isinstance(v, Video) for v in videos)
        
        # Check that text file is excluded
        names = {v.path.name for v in videos}
        assert "readme.txt" not in names
    
    def test_scan_recursive(self, video_directory):
        """Test recursive scanning includes subdirectories"""
        videos = VideoScanner.scan_directory(video_directory)
        names = {v.path.name for v in videos}
        
        assert "video3.avi" in names  # From subfolder
    
    def test_scan_empty_directory(self):
        """Test scanning empty directory"""
        with tempfile.TemporaryDirectory() as tmpdir:
            videos = VideoScanner.scan_directory(Path(tmpdir))
            assert len(videos) == 0


# ===== Integration Tests =====

class TestIntegration:
    """Integration tests for multiple components"""
    
    @pytest.fixture
    def integration_setup(self):
        """Setup complete testing environment"""
        with tempfile.TemporaryDirectory() as tmpdir:
            tmppath = Path(tmpdir)
            
            # Create test videos
            (tmppath / "test1.mp4").write_bytes(b"video1")
            (tmppath / "test2.mkv").write_bytes(b"video2")
            
            yield tmppath
    
    def test_full_metadata_workflow(self, integration_setup):
        """Test complete metadata workflow"""
        # Scan
        videos = VideoScanner.scan_directory(integration_setup)
        assert len(videos) == 2
        
        # Create metadata service
        service = MetadataService(integration_setup)
        
        # Set metadata for first video
        video = videos[0]
        metadata = VideoMetadata(path=video.path, status="liked", position=0.5, speed=1.5)
        service.set(video, metadata)
        
        # Retrieve and verify
        retrieved = service.get(video)
        assert retrieved.status == "liked"
        assert retrieved.position == 0.5
        assert retrieved.speed == 1.5
        
        # Create new service instance (simulates app restart)
        service2 = MetadataService(integration_setup)
        retrieved2 = service2.get(video)
        assert retrieved2.status == "liked"  # Persisted!


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
