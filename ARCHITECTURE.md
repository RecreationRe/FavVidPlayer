# FavVidPlayer - Architecture Documentation

## Overview
FavVidPlayer has been refactored from a monolithic 950+ line `ui.py` into a clean, maintainable MVC architecture following SOLID principles and OOP best practices.

## Architecture Pattern: MVC (Model-View-Controller)

```
┌─────────────────────────────────────────────────────────────┐
│                    User Interface (View)                    │
│                   favvid/ui/main_window.py                  │
│  - PlayerWindow: Only presentation logic, no business logic │
│  - Menu bar, toolbar, video list, playback controls         │
└────────────────────────────┬────────────────────────────────┘
                             │ Qt Signals/Slots
                             ▼
┌─────────────────────────────────────────────────────────────┐
│              Application Controller (Controller)             │
│                  favvid/controller.py                        │
│  - ApplicationController: Orchestrates services & models     │
│  - Emits signals for UI updates                             │
│  - Receives UI actions and delegates to services            │
└────────────────────────────┬────────────────────────────────┘
                             │ Uses
                ┌────────────┴──────────────┐
                ▼                           ▼
    ┌──────────────────────┐    ┌─────────────────────┐
    │  Business Logic      │    │  Domain Models      │
    │  (Services)          │    │  (Models)           │
    │  favvid/services/    │    │  favvid/models/     │
    │   - VideoScanner     │    │   - Video           │
    │   - MetadataService  │    │   - VideoMetadata   │
    │   - PlaybackService  │    │   - Playlist        │
    │   - SettingsService  │    │   - AppSettings     │
    └──────────────────────┘    └─────────────────────┘
```

## Layer Descriptions

### 1. **Domain Models** (`favvid/models/`)
Pure data structures with business methods, no UI or I/O dependencies.

- **video.py**
  - `Video`: Represents a video file with path and metadata
  - `VideoMetadata`: Stores playback state (rating, position, speed, repeat flag)
  - Methods for status checks, position updates, serialization

- **playlist.py**
  - `Playlist`: Manages a collection of videos
  - Support for shuffle (preserves original order), search, filtering by status
  - Navigation: get_next(), get_previous(), current_index management

- **settings.py**
  - `AppSettings`: Application configuration as dataclass
  - Persisted via SettingsService
  - Settings include: volume, seek intervals, UI state, feature toggles

### 2. **Services** (`favvid/services/`)
Business logic layer with single responsibility. Each service handles one concern.

- **scanner.py** (`VideoScanner`)
  - Recursively scans directories for video files
  - Returns Videos as domain objects
  - Supports 18+ video formats (.mp4, .mkv, .avi, etc.)
  - No UI dependencies - purely functional

- **metadata.py** (`MetadataService`)
  - Persists VideoMetadata to `.favmeta.json`
  - JSON-based storage with UTF-8 encoding
  - Caches metadata in memory for performance
  - Handles favorites folder with hardlinks
  - Testable: can be tested independently of UI

- **playback.py** (`PlaybackService`)
  - Wrapper around VLC player (python-vlc)
  - Consistent API: play(), pause(), resume(), stop()
  - Position and volume control
  - Speed adjustment
  - Stores reference to currently playing video

- **settings.py** (`SettingsService`)
  - Bridges Qt QSettings and domain AppSettings model
  - Load/save app configuration
  - Provides singleton app_settings instance

### 3. **Controller** (`favvid/controller.py`)
Orchestrates communication between UI, services, and models.

- **ApplicationController** (inherits QObject for Qt signals)
  - **Signals**: videos_loaded, video_started, playback_state_changed, position_changed, time_updated
  - **Methods**: load_folder(), play_video(), toggle_play_pause(), play_next/previous(), seek, volume control, rating, shuffle toggle, search
  - Delegates to appropriate service for each action
  - Emits signals to notify UI of changes

### 4. **View** (`favvid/ui/`)
Pure presentation layer - no business logic.

- **main_window.py** (`PlayerWindow`)
  - Menu bar: File, View, Help
  - Toolbar: Play, Pause, Next, Previous, Volume, Speed, Shuffle, Repeat
  - Video list (QListWidget) with search
  - Time display and seek slider
  - Rating buttons (1-5 stars)
  - Keyboard shortcuts
  - All interactions delegate to controller via methods

## Key Principles

### SOLID
- **Single Responsibility**: Each class has one reason to change
  - VideoScanner only scans directories
  - MetadataService only persists metadata
  - PlaybackService only controls playback
  - VideoMetadata only holds video state
  
- **Open/Closed**: Easy to extend without modifying existing code
  - Add new video formats by updating VIDEO_EXTENSIONS
  - Add new services without changing existing services
  - Add new UI controls by connecting to controller signals

- **Liskov Substitution**: Services can be mocked for testing

- **Interface Segregation**: Each service exposes minimal, focused API

- **Dependency Inversion**: UI depends on controller, not direct service access

### DRY (Don't Repeat Yourself)
- Business logic centralized in services
- Models define state and behavior once
- UI only handles presentation

### Testability
- Models are pure dataclasses - trivial to test
- Services have no UI dependencies - can be unit tested
- Controller can be mocked for UI testing
- Fixtures in `conftest.py` support test isolation

## File Structure
```
FavVidPlayer/
├── favvid/
│   ├── __init__.py
│   ├── controller.py           # MVC Controller
│   ├── player.py               # VLC wrapper (legacy)
│   ├── scanner.py              # Legacy scanner (kept for compatibility)
│   ├── models/
│   │   ├── __init__.py
│   │   ├── video.py            # Video, VideoMetadata dataclasses
│   │   ├── playlist.py         # Playlist model
│   │   └── settings.py         # AppSettings dataclass
│   ├── services/
│   │   ├── __init__.py
│   │   ├── scanner.py          # VideoScanner service
│   │   ├── metadata.py         # MetadataService
│   │   ├── playback.py         # PlaybackService
│   │   └── settings.py         # SettingsService
│   └── ui/
│       ├── __init__.py
│       └── main_window.py      # PlayerWindow (view layer)
├── tests/
│   ├── conftest.py             # Pytest fixtures
│   ├── test_models.py          # Model unit tests
│   └── test_services.py        # Service unit tests
├── main.py                     # Application entry point
├── requirements.txt            # Dependencies
└── ARCHITECTURE.md             # This file
```

## Data Flow Examples

### Loading a Folder
1. User clicks "Open Folder" → UI calls controller.load_folder(path)
2. Controller calls VideoScanner.scan_directory(path)
3. Scanner returns list of Video objects
4. Controller initializes MetadataService and loads metadata for each video
5. Controller creates Playlist and emits videos_loaded signal
6. UI receives signal, updates playlist widget with video names

### Playing a Video
1. User double-clicks video in list → UI calls controller.play_video(video)
2. Controller calls PlaybackService.play(video)
3. PlaybackService uses VLC to play the file
4. Controller emits video_started signal with video object
5. UI receives signal, updates current selection, shows video name
6. Controller starts timer to update position/time
7. Each timer tick: emit position_changed, time_updated signals
8. UI receives signals, updates seek slider and time display

### Rating a Video
1. User clicks rating button (e.g., "Like") → UI calls controller.set_video_rating(video, "liked")
2. Controller updates video metadata in-memory
3. Controller calls MetadataService.set(video, metadata) to persist
4. MetadataService saves to .favmeta.json
5. Controller emits appropriate signal
6. UI updates visual feedback on rating button

## Next Steps

### Immediate
1. **Implement UI callbacks** - Connect all toolbar/menu actions to controller methods
2. **Test keyboard shortcuts** - Space (play/pause), Z/X (seek), 1-5 (ratings)
3. **Implement video list interactions** - Click to select, double-click to play

### Medium Term
1. **Settings dialog** - UI for app preferences
2. **Hotkeys dialog** - Customize keyboard shortcuts
3. **Extend test suite** - Service tests, integration tests

### Long Term
1. **Plugin system** - Allow extensions without modifying core
2. **Theme support** - Switchable UI themes
3. **Advanced search** - Filter by rating, play count, date added
4. **Watch folders** - Automatic detection of new videos

## Benefits of This Architecture

✅ **Maintainable**: Each layer has clear responsibility  
✅ **Testable**: Services can be unit tested independently  
✅ **Debuggable**: Problems can be isolated to specific layers  
✅ **Extensible**: New features don't require refactoring existing code  
✅ **Reusable**: Services can be used in different UI contexts (CLI, web, etc.)  
✅ **Professional**: Follows industry-standard patterns  

## Technical Details

### Qt Signal/Slot Communication
Controller is QObject subclass that emits signals:
```python
videos_loaded = QtCore.pyqtSignal(list)  # Emitted when folder loaded
video_started = QtCore.pyqtSignal(object)  # Emitted when video plays
```

UI connects to these signals in `__init__`:
```python
self.controller.videos_loaded.connect(self._on_videos_loaded)
self.controller.video_started.connect(self._on_video_started)
```

### Dataclass Serialization
Models use `@dataclass` with `asdict()` for JSON:
```python
@dataclass
class VideoMetadata:
    path: Path
    status: str = "normal"
    position: float = 0.0
    
    def to_dict(self) -> dict:
        data = asdict(self)
        data['path'] = str(data['path'])  # Path → string for JSON
        return data
```

### Service Singleton Pattern
SettingsService provides app_settings singleton:
```python
settings_service = SettingsService()
settings = settings_service.app_settings
```

---
**Last Updated**: After architectural migration complete
**Status**: Core architecture stable, features in integration phase
