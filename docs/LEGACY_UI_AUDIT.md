# Legacy UI.py Comprehensive Audit

## Overview
This document details a complete line-by-line audit of the legacy `favvid/ui.py` (948 lines) to identify missing features and patterns not yet implemented in the new OOP/SOLID architecture.

## Critical Missing Components

### 1. **VideoOverlay Class** (Lines 62-97)
**Purpose**: Transparent overlay widget for handling video interactions
**Features**:
- Single click detection with 250ms threshold
- Double click handling
- Mouse wheel scrolling
- Event forwarding to parent VideoWidget

**Status**: ❌ NOT IMPLEMENTED
**Implementation Plan**:
- Create as separate UI component in `favvid/ui/video_overlay.py`
- Use signals: `single_clicked`, `double_clicked`, `wheel_scrolled`
- Integrate with PlayerWindow

### 2. **VideoWidget Class** (Lines 99-127)
**Purpose**: Custom QFrame for video with embedded overlay and signal forwarding
**Features**:
- Inherits from QFrame
- Contains VideoOverlay instance
- Forwards all signals from overlay
- Handles resize events to keep overlay in sync
- Auto-raises overlay to front on resize

**Status**: ⚠️ PARTIAL (basic structure exists, overlay missing)
**Implementation Plan**:
- Enhance existing video_frame with proper VideoOverlay integration
- Ensure overlay covers entire frame
- Test signal forwarding chain

### 3. **SettingsDialog Class** (Lines 10-55)
**Purpose**: Settings modal dialog with persistence options
**Features**:
- Persist Volume checkbox
- Persist Last Position checkbox  
- Small seek interval input (0.1-60 seconds, default 5.0)
- Large seek interval input (1-300 seconds, default 30.0)
- OK/Cancel buttons with Qt settings persistence

**Status**: ✅ PARTIALLY IMPLEMENTED (basic version in new UI)
**Gaps**:
- Missing seek interval range validation
- Settings not persisted correctly
- Default values hardcoded instead of from AppSettings model

**Implementation Plan**:
- Enhance SettingsDialog in new PlayerWindow
- Use SettingsService instead of Qt settings directly
- Add range validation

### 4. **Keyboard Shortcuts** (Lines 773-814)
**Purpose**: 16 keyboard shortcuts for full playback control
**Shortcuts**:
- `Space` → toggle_play_pause
- `Left` → previous_video
- `Right` → next_video  
- `Ctrl+S` → stop_playback
- `F11` → toggle_fullscreen
- `Up` → volume_up
- `Down` → volume_down
- `M` → toggle_mute
- `1` → toggle_status('normal')
- `2` → toggle_status('liked')
- `3` → toggle_status('disliked')
- `Z` → seek_backward_small
- `X` → seek_forward_small
- `Ctrl+Z` → seek_backward_large
- `Ctrl+X` → seek_forward_large
- `S` → toggle_shuffle
- `R` → toggle repeat checkbox
- `A` → toggle auto_next checkbox
- `Ctrl+F` → focus search box
- `Ctrl+O` → open_folder

**Status**: ⚠️ PARTIAL (most implemented, mute and seek_large missing)
**Missing**: 
- Mute toggle (M key with volume memory)
- Ctrl+Z/Ctrl+X for large seek intervals
- Settings persistence for seek intervals

### 5. **Playlist Display and Colors** (Lines 440-490)
**Purpose**: Color-coded playlist items based on rating status
**Implementation Details**:
- `liked` → lightgreen (#90ee90)
- `disliked` → lightcoral (#f08080)  
- `normal` → lightblue (#add8e6)
- Applied to both QListWidget and QTreeWidget items

**Status**: ✅ IMPLEMENTED (in new PlayerWindow._update_playlist_view)
**Validation**: Colors correctly applied in new code

### 6. **Auto-Hide Playlist** (Lines 725-742)
**Purpose**: Auto-hide playlist dock when cursor leaves right edge
**Implementation Details**:
- `edge_timer` checks mouse position every 200ms
- Unpinned mode: shows when cursor x > width - 40px, hides when x < width - 200px
- Pinned mode: always visible (checked by pin_btn state)
- Pin button in custom title bar for playlist dock

**Status**: ⚠️ PARTIAL (timer logic implemented, may need refinement)
**Gaps**:
- Edge detection threshold may not match behavior
- Pin button placement in new code may differ

### 7. **Search and Filtering** (Lines 812-843)
**Purpose**: Real-time playlist search with tree traversal
**Implementation Details**:
- Case-insensitive search
- Works on both flat list and tree view
- For tree: shows items matching search OR containing matching children
- For tree: auto-expands matching folders during search
- Hides non-matching items

**Status**: ⚠️ PARTIAL (basic search exists, tree filtering may need enhancement)
**Gaps**:
- Tree expansion on search match not implemented
- Folder detection logic differs

### 8. **Seek Controls** (Lines 860-902)
**Purpose**: Seek by configurable intervals
**Implementation Details**:
- `seek_backward_small()` - decrease time by `small_seek_seconds` (default 5.0)
- `seek_forward_small()` - increase time by `small_seek_seconds`
- `seek_backward_large()` - decrease by `large_seek_seconds` (default 30.0)
- `seek_forward_large()` - increase by `large_seek_seconds`
- All methods respect video bounds (0 to total_time)
- Use position ratio for VLC player

**Status**: ❌ NOT FULLY IMPLEMENTED
**Gaps**:
- Only seek_forward/seek_backward in PlaybackService, not large intervals
- Need to add separate methods for large seek intervals

### 9. **Mute Toggle** (Lines 848-857)
**Purpose**: Toggle mute with volume memory
**Implementation Details**:
- Toggle mute: if volume > 0, save to `last_volume` and set to 0
- Toggle unmute: restore to previous `last_volume` (default 50)
- Uses `last_volume` attribute on PlayerWindow

**Status**: ❌ NOT IMPLEMENTED
**Implementation Plan**:
- Add `toggle_mute()` method to PlayerWindow
- Store last_volume as instance variable

### 10. **Repeat Mode** (Lines 714-721, 585-599)
**Purpose**: Global repeat state management
**Implementation Details**:
- `global_repeat_enabled` flag tracks repeat state across videos
- `is_repeating_current` flag prevents infinite loop on current repeat
- When video ends:
  - If repeat enabled and not already repeating: replay current video
  - Otherwise if auto_next enabled: play next video
- Repeat checkbox state persists to next video

**Status**: ⚠️ PARTIAL
**Current Implementation Issues**:
- AppSettings has `repeat_enabled` boolean (not adequate)
- Needs `repeat_mode` with 3 states: 'off', 'one', 'all'
- Need logic to handle repeat one vs repeat all

**Implementation Plan**:
- Modify AppSettings.repeat_mode to support 3 states
- Implement repeat logic in ApplicationController
- Update toggle_repeat to cycle through modes

### 11. **Shuffle Mode** (Lines 850-860)
**Purpose**: Randomize playlist order
**Implementation Details**:
- `shuffle_mode` flag tracks state
- `original_playlist` stores pre-shuffle order
- Shuffle: copy playlist → store to original → shuffle in place
- Unshuffle: restore from original
- Visual feedback via shuffle_action.setChecked(state)

**Status**: ✅ IMPLEMENTED (in new code)
**Validation**: Implementation matches legacy pattern

### 12. **Auto Next** (Lines 585-599)
**Purpose**: Automatically play next video when current ends
**Implementation Details**:
- `auto_next_checkbox` state determines behavior
- Checked (default true) = play next when current ends
- Unchecked = stop at end
- Skips if current video not in playlist

**Status**: ✅ IMPLEMENTED
**Validation**: Logic in new PlayerWindow._on_video_finished (need to verify)

### 13. **Speed Control** (Lines 699-707)
**Purpose**: Playback speed adjustment
**Implementation Details**:
- QDoubleSpinBox with range 0.25x to 4.0x
- Default 1.0x
- Steps of 0.25x
- Applied via `vlc.set_rate(val)`
- Persisted to metadata for this video

**Status**: ⚠️ NOT IMPLEMENTED
**Gaps**:
- Speed not in current PlaybackService API
- Need to add to VLC wrapper

### 14. **Repeat and Auto-Next Checkboxes** (Lines 210-219)
**Purpose**: Quick toggle for repeat and auto-next modes
**Features**:
- Checkboxes in toolbar
- State toggles via keyboard (R, A keys)
- Tooltips with hotkey info
- State managed through signals

**Status**: ⚠️ PARTIAL
**Gaps**:
- Repeat needs 3-state toggle (off/one/all), not boolean checkbox
- Need proper state cycling

### 15. **Status Bar** (Lines 145-148)
**Purpose**: Display hotkey reference and status
**Implementation Details**:
- Shows comprehensive hotkey guide
- Updated with status messages during playback

**Status**: ✅ IMPLEMENTED
**Validation**: Comprehensive help text in new code

### 16. **Menu Bar Actions** (Lines 141-158)
**Purpose**: File, View, Help menus
**Features**:
- File: Select Folder
- View: File Explorer Mode (checkable, toggle between flat/tree)
- Help: Settings, Hotkeys

**Status**: ✅ IMPLEMENTED
**Validation**: All menus in new code

### 17. **Toolbar** (Lines 160-231)
**Purpose**: Playback and control buttons
**Features**:
- Navigation: ⏮ ▶ ⏹ ⏭ buttons
- Position: time display + seek slider
- Volume: 🔊 icon + slider
- Fullscreen: ⛶ button
- Speed: label + spinbox
- Repeat: checkbox 🔁
- Auto-next: checkbox ⏭️
- Ratings: 😐👍👎 buttons with colors

**Status**: ✅ MOSTLY IMPLEMENTED
**Gaps**:
- Speed control not implemented
- Repeat checkbox logic needs 3-state handling

### 18. **Window Title** (Lines 821-825)
**Purpose**: Show current playing video name
**Implementation Details**:
- Default: 'FavVidPlayer'
- During playback: 'FavVidPlayer - {video_name}'
- Updates via `update_window_title()` called in update_ui timer

**Status**: ✅ IMPLEMENTED
**Validation**: Works in new code via signal handlers

### 19. **Position Slider Click Seek** (Lines 823-831)
**Purpose**: Seek by clicking on position bar (not dragging)
**Implementation Details**:
- Overrides slider mousePressEvent
- Calculates position based on click x-coordinate
- Converts to 0-1000 range for slider
- Calls `set_position()` with new value

**Status**: ✅ IMPLEMENTED
**Validation**: Working in new code

### 20. **Volume Mouse Wheel** (Lines 833-841)
**Purpose**: Adjust volume by scrolling mouse wheel
**Implementation Details**:
- On video area: mouse wheel adjusts volume ±5
- On volume slider: mouse wheel also works
- Respects volume bounds (0-100)

**Status**: ✅ IMPLEMENTED
**Validation**: Working via video_frame.wheel_scrolled signal

### 21. **Metadata Persistence** (Lines 545-562, 695-707)
**Purpose**: Save/restore per-video metadata
**Stored Data**:
- `status` - rating (liked, disliked, normal)
- `position` - playback position (0.0-1.0)
- `speed` - playback speed
- `last_played` - timestamp of last play

**Status**: ⚠️ PARTIAL
**Gaps**:
- Position persistence works via MetadataService
- Speed not in current implementation
- Last played timestamp not in metadata

### 22. **Folder Browsing** (Lines 427-437)
**Purpose**: Select folder and load videos
**Implementation Details**:
- QFileDialog for folder selection
- Scans folder for videos (via `scan_videos()`)
- Creates MetaStore for folder
- Saves last_folder to settings
- Builds playlist as list of Path objects

**Status**: ✅ IMPLEMENTED
**Validation**: Works in new code

## Summary of Missing/Incomplete Features

### Critical (Core Functionality):
- [ ] VideoOverlay component with click/wheel detection
- [ ] Large seek intervals (Ctrl+Z/Ctrl+X keys)
- [ ] Mute toggle (M key) with volume memory
- [ ] Proper 3-state repeat mode (off/one/all)
- [ ] Speed control in playback
- [ ] Tree view search with auto-expand
- [ ] Folder-based favorites (Favorites_FavVidPlayer folder)

### Important (User Experience):
- [ ] Settings dialog seek interval configuration
- [ ] Auto-hide playlist edge detection refinement
- [ ] Status persistence beyond current session
- [ ] Last played timestamp tracking

### Minor (Polish):
- [ ] Status bar dynamic updates during playback
- [ ] Repeat/Auto-next UI button styling refinement

## Architecture Issues in Legacy Code

### Not OOP/SOLID Compliant:
1. **Single Responsibility Violated**: PlayerWindow handles UI, playback, persistence, and business logic all mixed
2. **No Dependency Injection**: Direct instantiation of VLCPlayer, MetaStore, scanner
3. **Magic Strings**: Status values ('liked', 'disliked', 'normal') scattered throughout
4. **God Object**: PlayerWindow has 900+ lines doing everything
5. **No Separation of Concerns**: Business logic mixed with UI code
6. **Direct Qt Settings Access**: Should use SettingsService abstraction
7. **No Event Bus**: Direct signal/slot hell between components
8. **Tight Coupling**: MetaStore, VLCPlayer, scanner tightly coupled to UI

### Migration Strategy for Legacy Patterns:
- Extract VideoOverlay as separate UI component
- Move seek logic to PlaybackService
- Move repeat/shuffle logic to PlaybackService or Playlist
- Move mute logic to PlaybackService
- Enhance SettingsService for seek intervals
- Use ApplicationController for all playback operations
- Create DialogManager for Settings/Hotkeys dialogs

## Next Steps
1. ✅ Identify all missing components (THIS DOCUMENT)
2. ⏳ Create VideoOverlay component
3. ⏳ Implement large seek intervals
4. ⏳ Add mute toggle functionality
5. ⏳ Implement 3-state repeat mode
6. ⏳ Add speed control to PlaybackService
7. ⏳ Enhance tree search functionality
8. ⏳ Create comprehensive integration tests
