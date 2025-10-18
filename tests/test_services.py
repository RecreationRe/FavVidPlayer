"""Tests for services"""
import pytest
from pathlib import Path
from favvid.services import VideoScanner
from favvid.models import Video


class TestVideoScanner:
    def test_supported_extensions(self):
        assert '.mp4' in VideoScanner.VIDEO_EXTENSIONS
        assert '.mkv' in VideoScanner.VIDEO_EXTENSIONS
        assert '.avi' in VideoScanner.VIDEO_EXTENSIONS
    
    def test_scan_empty_directory(self, tmp_path):
        videos = VideoScanner.scan_directory(tmp_path)
        assert len(videos) == 0
    
    def test_scan_with_videos(self, tmp_path):
        # Create test video files
        (tmp_path / "video1.mp4").touch()
        (tmp_path / "video2.mkv").touch()
        (tmp_path / "notavideo.txt").touch()
        
        videos = VideoScanner.scan_directory(tmp_path)
        assert len(videos) == 2
        assert all(isinstance(v, Video) for v in videos)
    
    def test_scan_recursive(self, tmp_path):
        # Create nested structure
        sub_dir = tmp_path / "subfolder"
        sub_dir.mkdir()
        (tmp_path / "video1.mp4").touch()
        (sub_dir / "video2.mp4").touch()
        
        videos = VideoScanner.scan_directory(tmp_path)
        assert len(videos) == 2
    
    def test_scan_nonexistent(self):
        videos = VideoScanner.scan_directory(Path("/nonexistent/path"))
        assert len(videos) == 0
