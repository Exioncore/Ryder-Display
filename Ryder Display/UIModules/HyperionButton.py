import sys
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow
from PyQt5.QtCore import pyqtSlot
from PyQt5.QtCore import QSize
from PyQt5.QtGui import QIcon

from Pages.HyperionMenu import HyperionMenu

class HyperionButton(object):
    _menu : HyperionMenu

    def __init__(self, window: QMainWindow, pos, size, path):
        self._window = window
        self._path = path
        self._menu = None
        self._button = QPushButton('', window)
        self._button.setIcon(QIcon(path + '/Resources/Hyperion/Logo.png'))
        self._button.setIconSize(QSize(size[0], size[1]))
        self._button.setGeometry(pos[0], pos[1], size[0], size[1])
        self._button.clicked.connect(lambda:self.onClick())
        self._button.show()

    @pyqtSlot()
    def onClick(self):
        print("onClick")
        if self._menu == None:
            self._menu = HyperionMenu()
            center = [
                self._window.frameGeometry().width() / 2,
                self._window.frameGeometry().height() / 2
            ]
            self._menu.createUI(self._menu, self._path, center)
        if not self._menu.isVisible():
            self._menu.show()

    def onClose(self):
        self._menu = None
