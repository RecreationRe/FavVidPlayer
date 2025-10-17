import sys
from PyQt5 import QtWidgets, QtCore
from favvid.ui import PlayerWindow


def main():
    QtCore.QCoreApplication.setOrganizationName("FavVidPlayer")
    QtCore.QCoreApplication.setApplicationName("FavVidPlayer")
    app = QtWidgets.QApplication(sys.argv)
    win = PlayerWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
