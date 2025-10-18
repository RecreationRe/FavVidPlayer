"""Settings service"""
from PyQt5 import QtCore
from ..models import AppSettings


class SettingsService:
    """Service for managing application settings"""
    
    def __init__(self):
        self.qt_settings = QtCore.QSettings()
        self.app_settings = self._load_settings()
    
    def _load_settings(self) -> AppSettings:
        """Load settings from Qt settings"""
        settings = AppSettings()
        
        # Load each setting
        settings.volume = self.qt_settings.value("volume", 50, type=int)
        settings.persist_volume = self.qt_settings.value("persist_volume", True, type=bool)
        settings.persist_position = self.qt_settings.value("persist_position", True, type=bool)
        settings.seek_small_seconds = self.qt_settings.value("seek_small_seconds", 5.0, type=float)
        settings.seek_large_seconds = self.qt_settings.value("seek_large_seconds", 30.0, type=float)
        settings.pin_playlist = self.qt_settings.value("pin_playlist", False, type=bool)
        settings.file_explorer_mode = self.qt_settings.value("file_explorer_mode", False, type=bool)
        settings.last_folder = self.qt_settings.value("last_folder", None, type=str)
        settings.auto_next_enabled = self.qt_settings.value("auto_next_enabled", True, type=bool)
        settings.repeat_enabled = self.qt_settings.value("repeat_enabled", False, type=bool)
        settings.shuffle_enabled = self.qt_settings.value("shuffle_enabled", False, type=bool)
        
        return settings
    
    def load(self) -> None:
        """Reload settings from Qt settings"""
        self.app_settings = self._load_settings()
    
    def save(self) -> None:
        """Save all settings to Qt settings"""
        settings_dict = self.app_settings.to_dict()
        for key, value in settings_dict.items():
            self.qt_settings.setValue(key, value)
    
    def get(self, key: str, default=None):
        """Get a setting value"""
        return getattr(self.app_settings, key, default)
    
    def set(self, key: str, value) -> None:
        """Set a setting value and save"""
        if hasattr(self.app_settings, key):
            setattr(self.app_settings, key, value)
            self.save()

