# Implementation Plan: Completing the New Architecture

## Priority 1: Critical Missing Features

### 1.1 VideoOverlay Component
**File**: `favvid/ui/video_overlay.py`
**Status**: Not Started
**Effort**: 2-3 hours

**Implementation**:
```python
class VideoOverlay(QtWidgets.QWidget):
    single_clicked = QtCore.pyqtSignal()
    double_clicked = QtCore.pyqtSignal()
    wheel_scrolled = QtCore.pyqtSignal(int)
```

**Tasks**:
- [ ] Create VideoOverlay class with signals
- [ ] Implement click detection with 250ms threshold
- [ ] Implement wheel event handling
- [ ] Integrate with PlayerWindow.video_frame
- [ ] Test signal forwarding

### 1.2 Large Seek Intervals (Ctrl+Z/Ctrl+X)
**Files**: `favvid/services/playback.py`, `favvid/controllers/application.py`
**Status**: Partially Implemented
**Effort**: 1 hour

**Current State**: Only small seek_forward/seek_backward
**Missing**: Large seek methods using `large_seek_seconds` setting

**Tasks**:
- [ ] Add `seek_forward_large()` and `seek_backward_large()` to PlaybackService
- [ ] Add corresponding methods to ApplicationController
- [ ] Add keyboard shortcuts in PlayerWindow
- [ ] Test with different large_seek_seconds values

### 1.3 Mute Toggle (M Key)
**Files**: `favvid/services/playback.py`, `favvid/controllers/application.py`, `favvid/ui/main_window.py`
**Status**: Not Implemented
**Effort**: 1 hour

**Implementation Pattern**:
- Store last_volume when muting
- Restore last_volume when unmuting

**Tasks**:
- [ ] Add `toggle_mute()` to PlaybackService
- [ ] Add `toggle_mute()` to ApplicationController
- [ ] Connect M key shortcut in PlayerWindow
- [ ] Test mute/unmute with volume memory

### 1.4 3-State Repeat Mode
**Files**: `favvid/models/settings.py`, `favvid/services/playback.py`, `favvid/controllers/application.py`, `favvid/ui/main_window.py`
**Status**: Partially Implemented (2-state boolean)
**Effort**: 2 hours

**Current State**: `repeat_enabled` boolean in settings
**Missing**: 3-state cycle: off → one → all → off

**Tasks**:
- [ ] Update AppSettings.repeat_mode from boolean to string ('off', 'one', 'all')
- [ ] Update SettingsService to handle new repeat_mode
- [ ] Implement repeat logic in playback flow
- [ ] Update UI to cycle through 3 states on R key
- [ ] Test each repeat mode

### 1.5 Speed Control
**Files**: `favvid/models/video.py`, `favvid/services/playback.py`, `favvid/controllers/application.py`, `favvid/ui/main_window.py`
**Status**: Partially Implemented (UI exists, playback doesn't work)
**Effort**: 1.5 hours

**Current State**: Speed spinbox in toolbar (0.25x-4.0x)
**Missing**: Backend implementation

**Tasks**:
- [ ] Verify VLC player supports rate/speed setting
- [ ] Add `set_speed()` to PlaybackService
- [ ] Add `set_speed()` to ApplicationController  
- [ ] Connect speed spinbox to controller
- [ ] Persist speed in metadata
- [ ] Test speed changes

### 1.6 Enhanced Settings Dialog
**Files**: `favvid/ui/main_window.py`
**Status**: Basic implementation exists
**Effort**: 1.5 hours

**Current Implementation**: Basic settings in dialog
**Missing**: Proper seek interval configuration and validation

**Tasks**:
- [ ] Add seek interval controls (small: 0.1-60s, large: 1-300s)
- [ ] Add range validation
- [ ] Bind to SettingsService
- [ ] Test settings persistence

## Priority 2: UX Enhancements

### 2.1 Tree View Search with Auto-Expand
**Files**: `favvid/ui/main_window.py`
**Status**: Basic search works
**Effort**: 1 hour

**Current State**: Basic text matching
**Missing**: Auto-expand matching folders

**Tasks**:
- [ ] Enhance search_playlist to expand matching folders
- [ ] Test with nested folder structures
- [ ] Ensure search clears correctly

### 2.2 Auto-Hide Playlist Refinement
**Files**: `favvid/ui/main_window.py`
**Status**: Basic timer exists
**Effort**: 30 minutes

**Current State**: Mouse edge detection
**Missing**: Parameter tuning, animation consideration

**Tasks**:
- [ ] Test edge detection threshold (40px from right edge)
- [ ] Verify auto-show/hide working smoothly
- [ ] Adjust threshold if needed
- [ ] Consider adding slide animation

### 2.3 Metadata Enhancements
**Files**: `favvid/models/video.py`, `favvid/services/metadata.py`
**Status**: Basic structure exists
**Effort**: 1.5 hours

**Current State**: path, status, position, speed stored
**Missing**: last_played timestamp, watch count

**Tasks**:
- [ ] Add last_played tracking in VideoMetadata
- [ ] Add watch_count tracking
- [ ] Update MetadataService persistence
- [ ] Update UI to show watch count (optional)

## Priority 3: Testing & Documentation

### 3.1 Integration Tests
**Files**: `tests/test_ui_integration.py`
**Status**: Framework exists (but outside tests/ folder now)
**Effort**: 2 hours

**Tasks**:
- [ ] Move test_ui_integration.py to tests/ folder ✅
- [ ] Move verify_all.py to tests/ folder ✅
- [ ] Add tests for VideoOverlay
- [ ] Add tests for seek intervals
- [ ] Add tests for mute functionality
- [ ] Add tests for 3-state repeat
- [ ] Add tests for speed control
- [ ] Run full test suite

### 3.2 E2E Testing Plan
**Files**: Tests to be created
**Status**: Not Started
**Effort**: 3 hours

**Scenarios to Test**:
- [ ] Open folder → Load videos → Display playlist with colors
- [ ] Single click video → Play/Pause
- [ ] Double click video → Fullscreen
- [ ] Mouse wheel → Volume change
- [ ] Space key → Play/Pause
- [ ] Z key → Seek backward small
- [ ] X key → Seek forward small
- [ ] Ctrl+Z → Seek backward large (NEW)
- [ ] Ctrl+X → Seek forward large (NEW)
- [ ] 1/2/3 keys → Toggle ratings
- [ ] S key → Toggle shuffle
- [ ] R key → Cycle repeat modes (NEW)
- [ ] M key → Toggle mute (NEW)
- [ ] Up/Down → Volume control
- [ ] Speed control → Adjust playback speed (NEW)
- [ ] Settings dialog → Save seek intervals
- [ ] Search → Filter playlist
- [ ] Auto-hide → Hide playlist at edge

## File Organization

### Current Issues:
- ✅ `test_ui_integration.py` - moved to `tests/`
- ✅ `verify_all.py` - moved to `tests/`
- ❌ `favvid/controller.py` - old, should delete
- ❌ `favvid/persistence_controller.py` - old, should delete
- ❌ `favvid/meta.py` - old, should delete
- ❌ `favvid/scanner.py` - old (16 lines), should delete
- ❌ `favvid/ui.py` - old (948 lines), should delete

### New Files Needed:
- [ ] `favvid/ui/video_overlay.py` - VideoOverlay component
- [ ] `docs/LEGACY_UI_AUDIT.md` - ✅ Created
- [ ] `docs/IMPLEMENTATION_PLAN.md` - ✅ Creating this file
- [ ] `docs/ARCHITECTURE.md` - Update existing
- [ ] `docs/API.md` - Reference for all public APIs

## Timeline Estimate

| Phase | Tasks | Est. Hours | Status |
|-------|-------|-----------|--------|
| P1.1-P1.3 | Video Overlay, Large Seek, Mute | 6 | Not Started |
| P1.4-P1.6 | Repeat Mode, Speed, Settings | 4.5 | Partial |
| P2.1-P2.3 | UX Enhancements | 3 | Partial |
| P3.1-P3.2 | Testing | 5 | Framework Done |
| **Total** | | **18.5 hours** | |

## Execution Order

1. **Immediate** (Phase 1):
   - VideoOverlay (blocker for click/wheel)
   - Large seek intervals
   - Mute toggle

2. **Short Term** (Phase 2):
   - 3-state repeat
   - Speed control
   - Settings dialog enhancement

3. **Testing** (Phase 3):
   - Integration tests
   - E2E testing
   - Cleanup old files

## Dependencies

```
VideoOverlay → PlayerWindow.video_frame
Large Seek → PlaybackService → ApplicationController → PlayerWindow shortcuts
Mute → PlaybackService → ApplicationController → PlayerWindow
Repeat Mode → Playlist → PlaybackService → ApplicationController
Speed → PlaybackService → ApplicationController
Settings → SettingsService → AppSettings
```

## Success Criteria

- [ ] All 22 features from legacy code implemented
- [ ] All keyboard shortcuts working (20+ shortcuts)
- [ ] Button colors correct (lightgreen, lightcoral, lightblue)
- [ ] Playlist colors applied correctly
- [ ] Auto-hide working smoothly
- [ ] Search filtering in both flat and tree modes
- [ ] All E2E scenarios passing
- [ ] No import errors
- [ ] Application launches without errors
- [ ] Feature parity with legacy ui.py verified
