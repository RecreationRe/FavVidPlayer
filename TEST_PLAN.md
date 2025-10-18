# Comprehensive Test Plan for FavVidPlayer

## Test Coverage Analysis

### Unit Tests (favvid/models/*.py, favvid/services/*.py)

#### Models Tests (`tests/test_models.py`)
- ✓ Video model creation and properties
- ✓ VideoMetadata creation and serialization
- ✓ Playlist model operations (add, remove, search, shuffle)
- ✓ AppSettings model with defaults
- Tests for: Shuffle toggle, search filtering, status checks

#### Services Tests (`tests/test_services_comprehensive.py`)

**VideoScanner**
- ✓ Scan directory for supported formats
- ✓ Recursive directory scanning
- ✓ Empty directory handling
- ✓ Format filtering (ignore non-video files)

**MetadataService**
- ✓ Metadata file creation
- ✓ Get/set metadata operations
- ✓ JSON persistence
- ✓ Metadata loading from existing JSON
- ✓ Status setting
- ✓ Favorites creation (hardlink/copy)
- ✓ Favorites removal
- ✓ UTF-8 encoding handling
- ✓ Cache management

**PlaybackService**
- ✓ Play video file
- ✓ Handle missing files gracefully
- ✓ Seek forward/backward
- ✓ Volume control
- ✓ Speed adjustment
- ✓ Position tracking
- ✓ Time queries

**SettingsService**
- ✓ Default settings loading
- ✓ Qt settings bridge
- ✓ Persist/load cycle
- ✓ Individual setting get/set

### Integration Tests (`tests/test_integration.py`)

**End-to-End Workflows**
1. Folder Loading
   - Scan folder → Load metadata → Update playlist → All metadata loaded
   
2. Video Playback
   - Play video → Restore speed/position → Save on stop → Metadata persisted
   
3. Rating System
   - Rate video → Save metadata → Create/remove favorite → Color coding
   
4. Seek Operations
   - Seek forward → Update position → Persist → Verify
   - Seek backward → Update position → Persist → Verify
   
5. Shuffle Mode
   - Toggle shuffle → Playlist reorders → Original preserved
   - Toggle off → Original order restored
   
6. Search Filtering
   - Search query → Filter results → Clear search → Full list back
   
7. Settings Persistence
   - Change setting → Save → New service instance → Setting restored

### System Tests (`tests/test_system.py`)

**UI Layer**
1. PlayerWindow initialization
   - Controller created
   - Services connected
   - Widgets initialized
   - Signals connected

2. Menu Operations
   - Open folder → Dialog → Load folder
   - Settings → Dialog → Update settings
   - Hotkeys → Show message

3. Toolbar Interactions
   - Play/Pause button
   - Prev/Next buttons
   - Volume slider
   - Position slider
   - Speed control
   - Rating buttons
   - Shuffle/Repeat toggles

4. Keyboard Shortcuts
   - Space (play/pause)
   - Z/X (seek)
   - 1/2/3 (ratings)
   - Up/Down (volume)
   - S (shuffle)
   - R (repeat)
   - M (mute)

5. Video Interactions
   - Single click (play/pause)
   - Double click (fullscreen)
   - Mouse wheel (volume)
   - Click on seek bar (seek)

6. Playlist UI
   - List view vs Tree view toggle
   - Search filtering in list
   - Search filtering in tree
   - Color coding by status
   - Item selection and playback

### E2E Tests (`tests/test_e2e.py`)

**Complete User Workflows**

1. **New User Scenario**
   ```
   - App starts
   - Select folder with videos
   - Videos appear in playlist
   - Click video → plays
   - Rate video as "liked"
   - Video shows in green, appears in Favorites folder
   - App closes and reopens
   - Last folder loaded, volume restored, position restored
   ```

2. **Advanced User Scenario**
   ```
   - App has existing library
   - Enable shuffle
   - Play → next → next (shuffled order)
   - Disable shuffle → returns to original order
   - Search "action"
   - 3 videos show, click one, plays
   - Clear search → full playlist returns
   - Rate 3 videos as liked
   - All 3 appear in favorites folder
   - Toggle repeat → current video replays
   - Fullscreen with F11
   - Use Z/X to seek, 1/2/3 for ratings
   - Mute with M → volume → unmute
   ```

3. **Settings Scenario**
   ```
   - Open Settings dialog
   - Change seek intervals (2s, 60s)
   - Change persist flags
   - Close dialog
   - Play video, seek with new intervals
   - Close app
   - Reopen → new seek intervals in effect
   ```

4. **Favorites Scenario**
   ```
   - Rate multiple videos as "liked"
   - Check Favorites_FavVidPlayer folder
   - All liked videos have hardlinks there
   - Unlike a video
   - Hardlink removed from Favorites
   - Like video again
   - Hardlink recreated
   ```

5. **Playback Restoration Scenario**
   ```
   - Play video to 50%
   - Change speed to 1.5x
   - Stop or close app
   - Reopen → video loads
   - Position restored to 50%
   - Speed restored to 1.5x
   - Click play → continues from saved point
   ```

## Test Execution Strategy

### Phase 1: Unit Tests (Fast Feedback)
```bash
pytest tests/test_models.py -v
pytest tests/test_services_comprehensive.py -v
```
Expected: All pass, < 5 seconds

### Phase 2: Integration Tests (Comprehensive)
```bash
pytest tests/test_integration.py -v
```
Expected: All pass, 10-30 seconds

### Phase 3: System Tests (UI Verification)
```bash
pytest tests/test_system.py -v
```
Expected: All pass, requires X11/display (may need mocking)

### Phase 4: E2E Tests (Manual Verification)
```bash
pytest tests/test_e2e.py -v
```
Expected: Manual scenarios confirmed

### Full Test Suite
```bash
pytest tests/ -v --tb=short
```

## Code Coverage Goals

- **Models**: 95%+ (dataclasses, simple logic)
- **Services**: 90%+ (main business logic)
- **Controller**: 85%+ (orchestration logic)
- **UI**: 70%+ (presentation layer, some manual testing acceptable)

## Regression Test Suite

Quick tests to run after any changes:

```bash
# Core functionality
pytest tests/test_models.py::TestPlaylist -v
pytest tests/test_services_comprehensive.py::TestMetadataService -v
pytest tests/test_integration.py::TestIntegration::test_full_metadata_workflow -v

# Persistence
pytest tests/test_services_comprehensive.py::TestMetadataService::test_metadata_persisted_to_json -v
pytest tests/test_integration.py::TestIntegration -v

# Playback
pytest tests/test_services_comprehensive.py::TestPlaybackService -v
```

## Known Testing Challenges

1. **VLC Integration**: VLCPlayer requires actual X11/display for initialization
   - Solution: Mock in tests or use virtual display
   
2. **Qt GUI Testing**: Some UI interactions hard to test without display
   - Solution: Use pytest-qt or mock Qt
   
3. **File I/O**: Metadata persistence requires actual file system
   - Solution: Use tempfile.TemporaryDirectory (already implemented)
   
4. **Timing**: Seek position delayed for VLC initialization
   - Solution: Mock timers in tests

## Test Results Template

```
Test Suite Results - [Date]

Unit Tests (models, services):
  ✓ Models: 100% (24/24)
  ✓ VideoScanner: 100% (8/8)
  ✓ MetadataService: 95% (19/20)
  ✓ PlaybackService: 90% (18/20)
  ✓ SettingsService: 100% (5/5)
  
Integration Tests:
  ✓ Metadata Workflow: PASS
  ✓ Playback Workflow: PASS
  ✓ Search Workflow: PASS
  
System Tests (requires manual):
  - Toolbar interactions: PASS
  - Keyboard shortcuts: PASS
  - Video interactions: PASS
  
E2E Tests (manual scenarios):
  - New user workflow: PASS
  - Advanced user workflow: PASS
  - Settings persistence: PASS
  - Favorites management: PASS
```

## Continuous Integration

Recommended CI/CD setup:

```yaml
tests:
  unit:
    - pytest tests/test_models.py
    - pytest tests/test_services_comprehensive.py
  integration:
    - pytest tests/test_integration.py
  system:
    - pytest tests/test_system.py (optional, needs display)
  coverage:
    - pytest --cov=favvid tests/
    - target: 85%+ coverage
```

