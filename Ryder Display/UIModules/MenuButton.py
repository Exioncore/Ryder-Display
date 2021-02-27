import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

class MenuButton(object):
    _menu : QMainWindow

    def __init__(self, window: QMainWindow, pos, size, path, icon, popup):
        self._window = window
        self._menu = popup
        self._path = path
        self._button = QPushButton('', window)
        self._button.setIcon(QIcon(path + icon))
        self._button.setIconSize(QSize(size[0], size[1]))
        self._button.setGeometry(pos[0], pos[1], size[0], size[1])
        self._button.clicked.connect(lambda:self.onClick())
        self._button.show()

    @pyqtSlot()
    def onClick(self):
        if not self._menu.isVisible():
            self._menu.show()