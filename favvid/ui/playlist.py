"""Playlist view management"""
from PyQt5 import QtWidgets, QtCore, QtGui


class PlaylistManager:
    """Manages playlist view and search"""
    
    def __init__(self, parent):
        """Initialize playlist manager"""
        self.parent = parent
        self.playlist_dock = None
        self.playlist_view = None
        self.flat_list = None
        self.tree_list = None
        self.playlist_stack = None
        self.search_box = None
        self.auto_hide_timer = None
        self.playlist_was_visible = True
        self.root_path = None
    
    def setup(self):
        """Setup playlist dock widget"""
        self.playlist_dock = QtWidgets.QDockWidget('Playlist', self.parent)
        
        playlist_container = QtWidgets.QWidget()
        playlist_layout = QtWidgets.QVBoxLayout()
        
        # Search box
        self.search_box = QtWidgets.QLineEdit()
        self.search_box.setPlaceholderText('Search videos... (Ctrl+F)')
        self.search_box.textChanged.connect(self.parent.search_playlist)
        playlist_layout.addWidget(self.search_box)
        
        # Stack widget for flat/tree views
        self.playlist_stack = QtWidgets.QStackedWidget()
        
        # Flat list view
        self.flat_list = QtWidgets.QListWidget()
        self.flat_list.itemSelectionChanged.connect(self.parent._on_playlist_item_selected)
        self.playlist_stack.addWidget(self.flat_list)
        
        # Tree view for explorer mode
        self.tree_list = QtWidgets.QTreeWidget()
        self.tree_list.setHeaderLabels(['Files'])
        self.tree_list.itemSelectionChanged.connect(self.parent._on_playlist_item_selected)
        self.playlist_stack.addWidget(self.tree_list)
        
        self.playlist_view = self.flat_list  # Default to flat view
        playlist_layout.addWidget(self.playlist_stack)
        
        playlist_container.setLayout(playlist_layout)
        self.playlist_dock.setWidget(playlist_container)
        
        self.parent.addDockWidget(QtCore.Qt.RightDockWidgetArea, self.playlist_dock)
        
        # Setup auto-hide timer
        self.auto_hide_timer = QtCore.QTimer()
        self.auto_hide_timer.timeout.connect(self.parent._on_auto_hide_timeout)
        
        # Enable mouse tracking for auto-hide
        self.playlist_dock.enterEvent = lambda e: self._on_enter(e)
        self.playlist_dock.leaveEvent = lambda e: self._on_leave(e)
    
    def _on_enter(self, event):
        """Handle mouse enter playlist"""
        self.auto_hide_timer.stop()
        self.playlist_was_visible = True
    
    def _on_leave(self, event):
        """Handle mouse leave playlist"""
        if self.parent.auto_hide_action.isChecked():
            timeout = self.parent.controller.settings_service.get('autohide_timeout', 3)
            self.auto_hide_timer.start(int(timeout * 1000))
    
    def set_explorer_mode(self, enabled):
        """Switch between flat and tree view"""
        if enabled:
            self.playlist_view = self.tree_list
            self.playlist_stack.setCurrentWidget(self.tree_list)
        else:
            self.playlist_view = self.flat_list
            self.playlist_stack.setCurrentWidget(self.flat_list)
    
    def update_view(self, videos):
        """Update playlist view with proper colors"""
        if not videos or not self.root_path:
            return
        
        if self.playlist_view == self.flat_list:
            self._update_flat_view(videos)
        else:
            self._update_tree_view(videos)
    
    def _update_flat_view(self, videos):
        """Update flat list view"""
        self.flat_list.clear()
        for video in videos:
            # Show relative path (folder/filename)
            rel_path = str(video.path.relative_to(self.root_path))
            item = QtWidgets.QListWidgetItem(rel_path)
            self._set_item_color(item, video)
            self.flat_list.addItem(item)
    
    def _update_tree_view(self, videos):
        """Update tree view with folder structure"""
        self.tree_list.clear()
        
        # Build folder tree
        tree = {}
        for video in videos:
            rel = video.path.relative_to(self.root_path)
            parts = rel.parts
            current = tree
            
            # Navigate/create folder structure
            for part in parts[:-1]:
                if part not in current:
                    current[part] = {}
                current = current[part]
            
            # Add file to structure
            if '__files__' not in current:
                current['__files__'] = []
            current['__files__'].append((parts[-1], video))
        
        self._build_tree_items(self.tree_list.invisibleRootItem(), tree)
    
    def _build_tree_items(self, parent_item, node):
        """Recursively build tree items from nested dict"""
        for key, value in sorted(node.items()):
            if key == '__files__':
                for name, video in value:
                    file_item = QtWidgets.QTreeWidgetItem([name])
                    file_item.setData(0, QtCore.Qt.UserRole, video)
                    parent_item.addChild(file_item)
                    self._set_item_color(file_item, video)
            else:
                # Create folder item
                folder_item = QtWidgets.QTreeWidgetItem([key])
                parent_item.addChild(folder_item)
                self._build_tree_items(folder_item, value)
    
    def _set_item_color(self, item, video):
        """Set item background color based on video status"""
        status = video.metadata.status
        color = None
        if status == 'liked':
            color = QtGui.QColor('lightgreen')
        elif status == 'disliked':
            color = QtGui.QColor('lightcoral')
        else:
            color = QtGui.QColor('lightblue')
        
        # Handle both QListWidgetItem and QTreeWidgetItem
        if isinstance(item, QtWidgets.QListWidgetItem):
            item.setBackground(color)
        else:
            item.setBackground(0, color)
    
    
    def update_colors(self, videos):
        """Update all playlist item colors"""
        if self.playlist_view == self.flat_list:
            for i in range(self.flat_list.count()):
                item = self.flat_list.item(i)
                for video in videos:
                    if str(video.path.relative_to(self.root_path)) == item.text():
                        self._set_item_color(item, video)
                        break
        else:
            # Update tree items
            self._update_tree_colors(self.tree_list.invisibleRootItem(), videos)
    
    def _update_tree_colors(self, item, videos):
        """Recursively update tree item colors"""
        for i in range(item.childCount()):
            child = item.child(i)
            video_data = child.data(0, QtCore.Qt.UserRole)
            if video_data:
                self._set_item_color(child, video_data)
            self._update_tree_colors(child, videos)
    
    def focus_search(self):
        """Focus search box and select all"""
        self.search_box.setFocus()
        self.search_box.selectAll()

