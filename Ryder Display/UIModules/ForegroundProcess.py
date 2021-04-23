import os
import sys
import base64
import gevent
from threading import Lock
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from PyQt5.QtSvg import QSvgWidget

from Network.RyderClient import RyderClient

class ForegroundProcess(object):
    _label : QLabel
    _currentProgram : str
    _iconsPath : str

    def __init__(self, window, pos=[0, 0], size=25, path=""):
        # Create cache folder if it doesn't exist
        self._iconsPath = path + '/cache/icons/'
        if not os.path.exists(self._iconsPath):
            os.makedirs(self._iconsPath)
        # Store variables
        self._currentProgram = ""
        # UI
        self._label = QLabel(window)
        self._label.setGeometry(pos[0], pos[1], size, size)
        self._label.setAttribute(Qt.WA_TranslucentBackground)
        self._label.show()
        # Bind Server
        RyderClient().addEndPoint('foregroundProcessName', self._newProcessName)
        RyderClient().addEndPoint('foregroundProcessIcon', self._newProcessIcon)
        RyderClient().addEndPoint('on_connect', self._onConnect)

    def update(self, status):
        pass
    
    def _onConnect(self):
        RyderClient().send("[\"foregroundProcessName\"]")

    def _newProcessName(self, data):
        if data[1] != self._currentProgram:
            if data[1] is None:
                self._currentProgram = None
                self._label.setPixmap(QPixmap())
                self._label.update()
            else:
                if not os.path.exists(self._iconsPath + data[1] + '.png'):
                    # Request icon if not in cache
                    RyderClient().send("[\"foregroundProcessIcon\"]")
                else:
                    self._currentProgram = data[1]
                    # Load from cache
                    pixmap = QPixmap()
                    pixmap.load(self._iconsPath + self._currentProgram + '.png')
                    self._label.setPixmap(pixmap)
                    self._label.update()

    def _newProcessIcon(self, data):
        if self._currentProgram != data[1]:
            pixmap = QPixmap()
            if data[1] is None:
                self._currentProgram = None
            else:
                self._currentProgram = data[1]
                if data[2] is not None:
                    path = self._iconsPath + self._currentProgram + '.png'
                    if not os.path.exists(path):
                        # Store new icon in cache
                        pixmap.loadFromData(base64.b64decode(data[2]))
                        pixmap.save(path)
                    else:
                        # Load from cache
                        pixmap.load(path)
            self._label.setPixmap(pixmap)
            self._label.update()
