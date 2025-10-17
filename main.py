import sys
from PyQt5 import QtWidgets
from favvid.ui import PlayerWindow


def main():
    app = QtWidgets.QApplication(sys.argv)
    win = PlayerWindow()
    win.show()
    sys.exit(app.exec_())


if __name__ == '__main__':
    main()
