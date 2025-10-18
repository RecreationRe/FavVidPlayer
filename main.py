import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from favvid.ui import PlayerWindow


class GlobalEventFilter(QtCore.QObject):
    """Global event filter to catch key events that VLC might consume"""
    def __init__(self, window):
        super().__init__()
        self.window = window
    
    def eventFilter(self, obj, event):
        if event.type() == QtCore.QEvent.KeyPress:
            if event.key() == QtCore.Qt.Key_Space and not event.isAutoRepeat():
                self.window.toggle_play_pause()
                return True
        return False


def main():
    QtCore.QCoreApplication.setOrganizationName("FavVidPlayer")
    QtCore.QCoreApplication.setApplicationName("FavVidPlayer")
    app = QtWidgets.QApplication(sys.argv)
    win = PlayerWindow()
    
    # Install global event filter for Space key
    event_filter = GlobalEventFilter(win)
    app.installEventFilter(event_filter)
    
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
