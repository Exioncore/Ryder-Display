import os
import sys
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QPainterPath, QBrush, QFont, QPalette

class Notification(object):
    def __init__(
        self, window, styleFunction, stylesheet=["","",""], img_margin = 5, top_margin = 5, pos=[0,0], size=[100,20]
        ):
        self._styleFunction = styleFunction
        self._currApp = ''
        self._pos = pos

        # Create components
        ### Notification Background
        self._background_main_stylesheet = stylesheet[0]
        self._background = QLabel(window)
        self._background.setGeometry(pos[0], pos[1], size[0], size[1])
        self._background.hide()
        ### Notification Logo
        self._logo = QSvgWidget('', self._background)
        self._logo.setGeometry(
            img_margin, img_margin,
            size[1] - img_margin*2, size[1] - img_margin*2
        )
        self._logo.show()
        ### Notification Title
        self._title = QLabel(self._background)
        self._title.setAttribute(Qt.WA_TranslucentBackground)
        self._title.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._title.setStyleSheet('QLabel{'+stylesheet[1]+'}')
        self._title.setText('Title')
        self._title.adjustSize()
        self._title.setGeometry(
            img_margin + self._logo.width() + 4, top_margin,
            size[0] - img_margin - self._logo.width() - 4, self._title.height()
        )
        self._title.show()
        ### Notification Message
        self._message = QLabel(self._background)
        self._message.setAttribute(Qt.WA_TranslucentBackground)
        self._message.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._message.setStyleSheet('QLabel{'+stylesheet[2]+'}')
        self._message.setText('Message')
        self._message.adjustSize()
        self._message.setGeometry(
            img_margin + self._logo.width() + 8, top_margin + self._title.height() + 2,
            size[0] - img_margin - self._logo.width() - 8, self._message.height() * 2
        )
        self._message.show()

    def setParent(self, p):
        self._background.setParent(p)

    def deleteLater(self):
        self._background.deleteLater()

    def setText(self, app, title, message):
        if self._currApp != app:
            logoPath, backgroundColor = self._styleFunction(app)
            self._logo.load(logoPath)
            self._background.setStyleSheet('QLabel {background-color:'+backgroundColor+';'+self._background_main_stylesheet+'}')
            self._logo.setStyleSheet('background-color:'+backgroundColor+';')
            self._currApp = app

        # Update Textual Contents
        self._title.setText(title)
        self._message.setText(message)
        self._message.setWordWrap(True)

    def update(self):
        self._background.update()
        self._logo.update()
        self._title.update()
        self._message.update()

    def show(self):
        self._background.show()

    def hide(self):
        self._background.hide()

    def move(self, x, y):
        self._pos = [x, y]
        self._background.move(x, y)

    def moveX(self, x):
        self._pos[0] = x
        self._background.move(x, self._pos[1])

    def moveY(self, y):
        self._pos[1] = y
        self._background.move(self._pos[0], y)

    def bringToFront(self):
        self._background.raise_()

    def bringToBack(self):
        self._background.lower()
