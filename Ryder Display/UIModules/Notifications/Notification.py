import os
import sys
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QPainterPath, QBrush, QFont, QPalette
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtSvg import QSvgWidget

class Notification(object):
    def __init__(self, window, stylesheet=["","",""], img_margin = 5, pos=[0,0], size=[100,20], path=''):
        self._path = path
        self._background_main_stylesheet = stylesheet[0]
        self._background = QLabel(window)
        self._background.setGeometry(pos[0], pos[1], size[0], size[1])
        self._background.show()

        self._logo = QSvgWidget(path+'/Resources/Discord-Logo.svg', self._background)
        print(path+'/Resources/Discord-Logo.svg')
        self._logo.setGeometry(
            img_margin, img_margin,
            size[1] - img_margin*2, size[1] - img_margin*2
        )
        self._logo.show()

        self._title = QLabel(self._background)
        self._title.setAttribute(Qt.WA_TranslucentBackground)
        self._title.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._title.setStyleSheet('QLabel{'+stylesheet[1]+'}')
        self._title.setText('Title')
        self._title.adjustSize()
        self._title.setGeometry(
            img_margin + self._logo.width() + 4, img_margin,
            size[0] - img_margin - self._logo.width() - 4, self._title.height()
        )
        self._title.show()

        self._message = QLabel(self._background)
        self._message.setAttribute(Qt.WA_TranslucentBackground)
        self._message.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._message.setStyleSheet('QLabel{'+stylesheet[2]+'}')
        self._message.setText('Message')
        self._message.adjustSize()
        self._message.setGeometry(
            img_margin + self._logo.width() + 8, img_margin + self._title.height() + 2,
            size[0] - img_margin - self._logo.width() - 8, self._message.height()
        )
        self._message.show()

    def setText(self, app, title, message):
        if app == "Discord":
            self._logo.load(self._path+'/Resources/Discord-Logo.svg')
            color = '#36393f'
        elif app == "Steam":
            self._logo.load(self._path+'/Resources/Steam-Logo.svg')
            color = '#1b1c20'
        else:
            color = '#32a852'

        self._background.setStyleSheet('QLabel {background-color:'+color+';'+self._background_main_stylesheet+'}')
        self._logo.setStyleSheet('background-color:'+color+';')
        self._title.setText(title)
        self._message.setText(message)

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
        self._background.move(x, y)
