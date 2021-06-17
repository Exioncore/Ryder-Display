import os
import sys
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QPainterPath, QBrush, QFont, QPalette

class Notification(object):
    def __init__(self, window, stylesheet=["","",""], img_margin = 5, top_margin = 5, pos=[0,0], size=[100,20], path='', vals=None):
        self._path = path
        self._pos = pos

        # Check if initialization values are present
        if vals != None:
            self._currApp = vals[0]
            if vals[0] == "Discord":
                logo_path = self._path+'/Resources/Discord-Logo.svg'
                color = '#36393f'
            elif vals[0] == "Steam":
                logo_path = self._path+'/Resources/Steam-Logo.svg'
                color = '#1b1c20'
            else:
                color = '#32a852'
            title = vals[1]
            message = vals[2]
        else:
            # Default values 
            self._currApp = 'null'
            logo_path = self._path+'/Resources/Steam-Logo.svg'
            color = '#1E1E1E'
            title = 'Steam'
            message = 'Demo Steam Notification'

        # Create components
        ### Notification Background
        self._background_main_stylesheet = stylesheet[0]
        self._background = QLabel(window)
        self._background.setGeometry(pos[0], pos[1], size[0], size[1])
        ### Notification Logo
        self._logo = QSvgWidget(logo_path, self._background)
        self._logo.setGeometry(
            img_margin, img_margin,
            size[1] - img_margin*2, size[1] - img_margin*2
        )
        self._logo.setStyleSheet('background-color:'+color+';')
        self._logo.show()
        ### Notification Title
        self._title = QLabel(self._background)
        self._title.setAttribute(Qt.WA_TranslucentBackground)
        self._title.setAlignment(Qt.AlignTop | Qt.AlignLeft)
        self._title.setStyleSheet('QLabel{'+stylesheet[1]+'}')
        self._title.setText(title)
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
        self._message.setText(message)
        self._message.adjustSize()
        self._message.setGeometry(
            img_margin + self._logo.width() + 8, top_margin + self._title.height() + 2,
            size[0] - img_margin - self._logo.width() - 8, self._message.height() * 2
        )
        self._message.show()

        if vals != None:
            self._background.show()
        else:
            self._background.hide()

    def setText(self, app, title, message):
        if self._currApp != app:
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
