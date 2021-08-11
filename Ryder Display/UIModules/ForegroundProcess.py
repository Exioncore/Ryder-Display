import os
import sys
import base64
import gevent
from threading import Lock
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QLabel

from UIModules.Utils import *
from Network.RyderClient import RyderClient

class ForegroundProcess(object):
    _label : QLabel
    _currentProgram : str
    _iconsPath : str

    def __init__(self, window, settings, path=''):
        # Retrieve settings
        ### UI Related
        pos = settings['pos'] if 'pos' in settings else [0, 0]
        alignment = settings['alignment'] if 'alignment' in settings else 7
        size = settings['size'] if 'size' in settings else 25
        self._currentProgram = ""
        # Process alignment
        pos, _ = getPosFromAlignment(pos, [size, size], alignment)
        ### Create cache folder if it doesn't exist
        self._iconsPath = path + '/cache/icons/'
        if not os.path.exists(self._iconsPath):
            os.makedirs(self._iconsPath)
        # Create components
        self._label = QLabel(window)
        self._label.setGeometry(pos[0], pos[1], size, size)
        self._label.setAttribute(Qt.WA_TranslucentBackground)
        self._label.show()
        # Bind Server
        RyderClient().addEndPoint('foregroundProcessName', self._newProcessName)
        RyderClient().addEndPoint('foregroundProcessIcon', self._newProcessIcon)
        RyderClient().addEndPoint('on_connect', self._onConnect)

    def setParent(self, p):
        self._label.setParent(p)

    def deleteLater(self):
        # Remove Server Bindings
        RyderClient().removeEndPoint('foregroundProcessName', self._newProcessName)
        RyderClient().removeEndPoint('foregroundProcessIcon', self._newProcessIcon)
        RyderClient().removeEndPoint('on_connect', self._onConnect)
        # Remove from layout
        self._label.deleteLater()

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
