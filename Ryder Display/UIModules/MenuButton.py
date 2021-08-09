import sys
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSlot
from PyQt5.QtWidgets import QApplication, QWidget, QPushButton, QMainWindow

class MenuButton(object):
    _menu : QMainWindow
    _ui_elements = None

    def __init__(self, window: QMainWindow, pos, size, path, icon, popup, ui_elements = None):
        self._window = window
        self._menu = popup
        self._ui_elements = ui_elements
        self._path = path
        self._button = QPushButton('', window)
        self._button.setStyleSheet('border: none;')
        self._button.setIcon(QIcon(path + icon))
        self._button.setIconSize(QSize(size[0], size[1]))
        self._button.setGeometry(pos[0], pos[1], size[0], size[1])
        self._button.clicked.connect(lambda:self.onClick())
        self._button.show()

    def setParent(self, p):
        self._window = p
        self._menu.setParent(p)
        if self._ui_elements != None:
            for i in range(len(self._ui_elements)):
                self._ui_elements[i].setParent(p)
        self._button.setParent(p)

    def deleteLater(self):
        self._menu.deleteLater()
        if self._ui_elements != None:
            for i in range(len(self._ui_elements)):
                self._ui_elements[i].deleteLater()
        self._button.deleteLater()

    @pyqtSlot()
    def onClick(self):
        if not self._menu.isVisible():
            self._menu.move(
                self._window.pos().x() + self._window.size().width() / 2 - self._menu.size().width() / 2, 
                self._window.pos().y() + self._window.size().height() / 2 - self._menu.size().height() / 2
            )
            self._menu.show()
