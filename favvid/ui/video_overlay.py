"""Video overlay widget for interactive video frame controls"""
from PyQt5 import QtWidgets, QtCore


class VideoOverlay(QtWidgets.QFrame):
    """Transparent overlay for video frame with click/wheel handling"""
    
    # Signals
    single_clicked = QtCore.pyqtSignal()
    double_clicked = QtCore.pyqtSignal()
    wheel_scrolled = QtCore.pyqtSignal(int)
    
    CLICK_THRESHOLD = 250  # milliseconds
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setStyleSheet('background: transparent;')
        self.setAttribute(QtCore.Qt.WA_TransparentForMouseEvents, False)
        
        self.last_click_time = 0
        self.click_count = 0
    
    def mousePressEvent(self, event):
        """Handle mouse press - detect single vs double click"""
        current_time = QtCore.QTime.currentTime().msecsSinceStartOfDay()
        
        if current_time - self.last_click_time < self.CLICK_THRESHOLD:
            self.click_count += 1
            if self.click_count == 2:
                self.double_clicked.emit()
                self.click_count = 0
        else:
            self.click_count = 1
            QtCore.QTimer.singleShot(self.CLICK_THRESHOLD, self._emit_single_click)
        
        self.last_click_time = current_time
    
    def _emit_single_click(self):
        """Emit single click after threshold"""
        if self.click_count == 1:
            self.single_clicked.emit()
    
    def wheelEvent(self, event):
        """Handle mouse wheel - for volume control"""
        delta = event.angleDelta().y()
        self.wheel_scrolled.emit(delta)
        event.accept()
    
    def resizeEvent(self, event):
        """Keep overlay in sync with parent size"""
        super().resizeEvent(event)
