"""Tests for models"""
import pytest
from pathlib import Path
from favvid.models import Video, VideoMetadata, Playlist, AppSettings


class TestVideoMetadata:
    def test_create_metadata(self):
        path = Path("test.mp4")
        meta = VideoMetadata(path=path, status="liked")
        assert meta.path == path
        assert meta.status == "liked"
        assert meta.is_liked() is True
    
    def test_to_dict(self):
        path = Path("test.mp4")
        meta = VideoMetadata(path=path)
        data = meta.to_dict()
        assert isinstance(data, dict)
        assert data['path'] == str(path)
    
    def test_from_dict(self):
        data = {'path': 'test.mp4', 'status': 'liked', 'position': 0.5}
        meta = VideoMetadata.from_dict(data)
        assert meta.path == Path('test.mp4')
        assert meta.status == 'liked'
        assert meta.position == 0.5


class TestVideo:
    def test_create_video(self):
        path = Path("test.mp4")
        video = Video(path=path)
        assert video.path == path
        assert video.name == "test"
    
    def test_set_status(self):
        video = Video(path=Path("test.mp4"))
        video.set_status("liked")
        assert video.is_liked() is True
        
        with pytest.raises(ValueError):
            video.set_status("invalid")
    
    def test_update_position(self):
        video = Video(path=Path("test.mp4"))
        video.update_position(0.5)
        assert video.metadata.position == 0.5
        
        # Test clamping
        video.update_position(1.5)
        assert video.metadata.position == 1.0
        
        video.update_position(-0.5)
        assert video.metadata.position == 0.0


class TestPlaylist:
    def test_create_playlist(self):
        playlist = Playlist()
        assert len(playlist) == 0
    
    def test_add_video(self):
        playlist = Playlist()
        video = Video(path=Path("test.mp4"))
        playlist.add_video(video)
        assert len(playlist) == 1
        assert video in playlist.videos
    
    def test_remove_video(self):
        playlist = Playlist()
        video = Video(path=Path("test.mp4"))
        playlist.add_video(video)
        playlist.remove_video(video)
        assert len(playlist) == 0
    
    def test_shuffle(self):
        playlist = Playlist()
        for i in range(5):
            playlist.add_video(Video(path=Path(f"video{i}.mp4")))
        
        original_order = [v.path for v in playlist.videos]
        playlist.shuffle()
        assert playlist.is_shuffled() is True
        
        playlist.unshuffle()
        assert playlist.is_shuffled() is False
        assert [v.path for v in playlist.videos] == original_order
    
    def test_search(self):
        playlist = Playlist()
        playlist.add_video(Video(path=Path("action_movie.mp4")))
        playlist.add_video(Video(path=Path("comedy_show.mp4")))
        
        results = playlist.search("action")
        assert len(results) == 1
        assert results[0].name == "action_movie"
    
    def test_get_next(self):
        playlist = Playlist()
        v1 = Video(path=Path("video1.mp4"))
        v2 = Video(path=Path("video2.mp4"))
        v3 = Video(path=Path("video3.mp4"))
        
        playlist.add_video(v1)
        playlist.add_video(v2)
        playlist.add_video(v3)
        
        next_video = playlist.get_next(v1)
        assert next_video == v2
        
        next_video = playlist.get_next(v3)
        assert next_video is None
    
    def test_get_previous(self):
        playlist = Playlist()
        v1 = Video(path=Path("video1.mp4"))
        v2 = Video(path=Path("video2.mp4"))
        
        playlist.add_video(v1)
        playlist.add_video(v2)
        
        prev_video = playlist.get_previous(v2)
        assert prev_video == v1
        
        prev_video = playlist.get_previous(v1)
        assert prev_video is None


class TestAppSettings:
    def test_default_settings(self):
        settings = AppSettings()
        assert settings.volume == 50
        assert settings.auto_next_enabled is True
        assert settings.repeat_enabled is False
    
    def test_to_dict(self):
        settings = AppSettings(volume=75)
        data = settings.to_dict()
        assert data['volume'] == 75
    
    def test_from_dict(self):
        data = {'volume': 80, 'persist_volume': True}
        settings = AppSettings.from_dict(data)
        assert settings.volume == 80
