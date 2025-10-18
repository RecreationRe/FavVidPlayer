# FavVidPlayer API Reference

## Models API

### Video

```python
from favvid.models.video import Video, VideoMetadata

video = Video(path=Path("video.mp4"))
# Properties
video.name  # "video" (stem without extension)
video.exists  # bool
video.metadata  # VideoMetadata object

# Methods
video.set_status(status: str)  # 'normal', 'liked', 'disliked'
video.update_position(position: float)  # 0.0 to 1.0
video.mark_played()
```

### VideoMetadata

```python
from favvid.models.video import VideoMetadata

metadata = VideoMetadata(path=Path("video.mp4"))
# Attributes
metadata.status  # "normal" (default)
metadata.position  # 0.0 to 1.0, playback position
metadata.speed  # 1.0 (playback speed)
metadata.last_played  # ISO datetime string or None
metadata.custom_data  # dict for future extensions

# Methods
metadata.to_dict()  # Convert to JSON-serializable dict
VideoMetadata.from_dict(data, path=None)  # Load from dict
metadata.is_liked()  # bool
metadata.is_disliked()  # bool
metadata.is_normal()  # bool
```

### Playlist

```python
from favvid.models.playlist import Playlist
from favvid.models.video import Video

playlist = Playlist()

# Methods
playlist.add_video(video: Video)
playlist.remove_video(video: Video)
playlist.clear()
playlist.shuffle()
playlist.unshuffle()
playlist.toggle_shuffle()
playlist.is_shuffled()  # bool
playlist.search(query: str)  # Returns list of matching videos
playlist.next_video(video: Video)  # Get next video or None
playlist.previous_video(video: Video)  # Get previous video or None

# Attributes
playlist.videos  # List[Video] - current order
```

### AppSettings

```python
from favvid.models.settings import AppSettings

settings = AppSettings()
# All attributes (with defaults):
settings.volume  # int: 0-100, default 50
settings.persist_volume  # bool, default True
settings.persist_position  # bool, default True
settings.seek_small_seconds  # float, default 5.0
settings.seek_large_seconds  # float, default 30.0
settings.pin_playlist  # bool, default False
settings.file_explorer_mode  # bool, default False
settings.last_folder  # Optional[str], default None
settings.auto_next_enabled  # bool, default True
settings.repeat_mode  # str: 'off'/'one'/'all', default 'off'
settings.shuffle_enabled  # bool, default False
settings.last_volume  # int, default 50
settings.is_muted  # bool, default False

# Methods
settings.to_dict()  # Convert to dict
AppSettings.from_dict(data: dict)  # Create from dict
```

## Services API

### VideoScanner

```python
from favvid.services.scanner import VideoScanner

scanner = VideoScanner()
videos = scanner.scan_folder(Path("/path/to/videos"))
# Returns List[Video] of all video files found
```

### MetadataService

```python
from favvid.services.metadata import MetadataService

service = MetadataService(root_folder=Path("/videos"))

# Get metadata for a video
metadata = service.get(video: Video)

# Update metadata for a video
service.set(video: Video, metadata: VideoMetadata)

# Set rating/status
service.set_status(video: Video, status: str)

# Favorites management
service.create_favorite(video: Video)  # Copies to Favorites folder
service.remove_favorite(video: Video)  # Removes from Favorites

# Metadata persisted to .favmeta.json in root folder
```

### PlaybackService

```python
from favvid.services.playback import PlaybackService

service = PlaybackService()

# Playback control
service.play(video_path: Path)
service.pause()
service.resume()
service.stop()
service.toggle_play_pause()

# Position control
service.get_position()  # 0.0 to 1.0
service.set_position(position: float)
service.get_time()  # Current time in milliseconds
service.get_duration()  # Total duration in milliseconds
service.get_length()  # Alias for get_duration()

# Seeking
service.seek_forward()  # Small seek (configurable)
service.seek_backward()  # Small seek (configurable)
service.seek_forward_large()  # Large seek (NEW)
service.seek_backward_large()  # Large seek (NEW)

# Volume
service.get_volume()  # 0-100
service.set_volume(volume: int)
service.set_mute(muted: bool)
service.toggle_mute()

# Speed control (NEW)
service.get_rate()  # Current playback rate
service.set_rate(rate: float)  # 0.25x to 4.0x

# State
service.is_playing()  # bool
service.current_video  # Video object or None
```

### SettingsService

```python
from favvid.services.settings import SettingsService

service = SettingsService()

# Access settings
service.app_settings  # AppSettings object
service.get(key: str, default=None)  # Get a setting value

# Modify settings
service.set(key: str, value)  # Set and save a setting
service.save()  # Persist all settings to Qt settings
service.load()  # Reload settings from Qt settings

# Example
service.set('volume', 75)
volume = service.get('volume')  # Returns 75
```

## Controllers API

### ApplicationController

```python
from favvid.controllers.application import ApplicationController

controller = ApplicationController()

# Loading
controller.load_folder(path: Path)
controller.set_playback_service(widget)

# Playback control
controller.toggle_play_pause()
controller.play_next()
controller.play_previous()
controller.play_video(video: Video)
controller.set_video_position(position: float)  # 0.0 to 1.0
controller.set_volume(volume: int)  # 0-100
controller.enable_shuffle()
controller.disable_shuffle()
controller.toggle_shuffle()
controller.toggle_repeat()  # Cycles: off → one → all → off

# Seeking
controller.seek_forward()
controller.seek_backward()
controller.seek_forward_large()
controller.seek_backward_large()

# Mute (NEW)
controller.toggle_mute()

# Speed (NEW)
controller.set_speed(rate: float)

# Ratings
controller.set_video_rating(video: Video, status: str)

# Search
controller.search_playlist(query: str)  # Returns List[Video]

# State queries
controller.get_is_playing()  # bool

# Properties
controller.playlist  # Playlist object
controller.playback_service  # PlaybackService
controller.settings_service  # SettingsService
controller.metadata_service  # MetadataService

# Signals (PyQt5)
controller.videos_loaded  # Emitted with List[Video]
controller.video_started  # Emitted with Video
controller.playlist_updated  # Emitted when playlist changes
controller.rating_changed  # Emitted with (Video, status)
```

### PersistenceController

```python
from favvid.controllers.persistence import PersistenceController

controller = PersistenceController(app_controller: ApplicationController)

# State persistence
controller.save_state()  # Save all state to metadata
controller.load_state()  # Load state from metadata

# Favorites management
controller.is_favorite(video: Video)  # bool
controller.add_to_favorites(video: Video)
controller.remove_from_favorites(video: Video)
controller.get_favorites()  # Returns List[Video]
```

## UI API

### PlayerWindow

```python
from favvid.ui.main_window import PlayerWindow
from PyQt5 import QtWidgets

app = QtWidgets.QApplication([])
window = PlayerWindow()
window.show()

# User-facing methods
window.open_folder()  # Open folder dialog
window.toggle_play_pause()
window.stop_playback()
window.previous_video()
window.next_video()
window.seek_video(value)  # 0-1000 slider value
window.seek_forward()  # Z key
window.seek_backward()  # X key
window.set_volume(value)  # 0-100
window.volume_up()
window.volume_down()
window.toggle_fullscreen()
window.set_rating(status)  # 'liked', 'disliked', 'normal'
window.search_playlist(query: str)
window.show_settings()  # Show settings dialog
window.show_hotkeys()  # Show hotkeys help

# Properties
window.controller  # ApplicationController
window.playlist_view  # QListWidget or QTreeWidget
window.volume_slider  # QSlider
window.position_slider  # QSlider
window.search_box  # QLineEdit
window.play_action  # QAction

# Keyboard shortcuts (automatically set up)
# Space - Play/Pause
# Z - Seek backward small
# X - Seek forward small
# Ctrl+Z - Seek backward large (NEW)
# Ctrl+X - Seek forward large (NEW)
# 1/2/3 - Toggle normal/liked/disliked
# S - Toggle shuffle
# R - Cycle repeat modes (NEW)
# M - Toggle mute (NEW)
# Up/Down - Volume control
# Left/Right - Previous/Next video
# F11 - Toggle fullscreen
# Ctrl+F - Focus search
# Ctrl+O - Open folder
# A - Toggle auto-hide
# Mouse wheel on video - Volume control
# Click video - Play/Pause
# Double click video - Fullscreen
```

## Usage Examples

### Example 1: Basic Playback

```python
from PyQt5 import QtWidgets
from favvid.ui.main_window import PlayerWindow

app = QtWidgets.QApplication([])
window = PlayerWindow()
window.show()
window.open_folder()  # User selects folder
app.exec_()
```

### Example 2: Programmatic Control

```python
from favvid.controllers.application import ApplicationController
from pathlib import Path

controller = ApplicationController()
controller.load_folder(Path("/videos"))

# Play first video and set volume
if controller.playlist.videos:
    controller.play_video(controller.playlist.videos[0])
    controller.set_volume(75)
    controller.toggle_shuffle()
```

### Example 3: Metadata Access

```python
from favvid.services.metadata import MetadataService
from pathlib import Path

service = MetadataService(Path("/videos"))

for video in videos:
    metadata = service.get(video)
    print(f"{video.name}: {metadata.status} at {metadata.position*100}%")
```

### Example 4: Settings Management

```python
from favvid.services.settings import SettingsService

settings = SettingsService()

# Modify settings
settings.set('volume', 80)
settings.set('repeat_mode', 'one')
settings.set('seek_small_seconds', 10.0)
settings.save()

# Access settings
print(settings.get('volume'))  # 80
print(settings.app_settings.repeat_mode)  # 'one'
```

## Error Handling

All services follow a consistent error pattern:

```python
try:
    controller.play_video(video)
except Exception as e:
    print(f"Error: {e}")
```

Common exceptions:
- `FileNotFoundError`: Video file not found
- `ValueError`: Invalid status/rate value
- `IOError`: Metadata file I/O error
- `RuntimeError`: VLC player error

## Threading Model

- Single-threaded PyQt5 event loop
- VLC handles threading internally
- No explicit thread management needed
- All API calls are synchronous

## Performance

- Typical folder with 1000 videos: < 1 second to scan and load
- Metadata JSON I/O: < 100ms for typical usage
- UI update rate: 100ms for playback, 200ms for auto-hide
- Search: O(n) complexity, instant for typical playlists

## Deprecations

- Legacy `ui.py` (948 lines) - replaced by new PlayerWindow and services
- Old `MetaStore` - replaced by MetadataService
- Direct VLC usage - use PlaybackService instead
- `repeat_enabled` boolean - use `repeat_mode` string

## Backward Compatibility

The new architecture maintains data compatibility with legacy:
- Metadata JSON format unchanged
- Settings keys compatible with Qt settings
- Video file formats unchanged (VLC compatibility)

## Future APIs

Planned additions:
- `PlaylistService`: Advanced playlist operations
- `ThemeService`: UI theme management
- `PluginService`: Plugin architecture
- `StatisticsService`: Watch statistics
- `NetworkService`: Remote playback control
