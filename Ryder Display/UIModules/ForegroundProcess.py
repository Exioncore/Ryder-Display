import os
import sys
import base64
from threading import Lock
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel
from PyQt5.QtSvg import QSvgWidget

from Network.Client import Client
from Network.Server import Server

class ForegroundProcess(object):
    _label : QLabel
    _currentProgram : str
    _iconsPath : str

    def __init__(self, window, server : Server, pos=[0, 0], size=25, path=""):
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
        server.add_endpoint('/foregroundProcessName', 'foregroundProcessName', self._newProcessName)
        server.add_endpoint('/foregroundProcessIcon', 'foregroundProcessIcon', self._newProcessIcon)

    def update(self, status):
        pass
    
    def _newProcessName(self, request):
        if request != self._currentProgram:
            if request is None:
                self._currentProgram = "null"
                self._label.setPixmap(QPixmap())
                self._label.update()
            else:
                if not os.path.exists(self._iconsPath + request + '.png'):
                    # Request icon if not in cache
                    Client().requestForegroundProcessIcon()
                else:
                    self._currentProgram = request
                    # Load from cache
                    pixmap = QPixmap()
                    pixmap.load(self._iconsPath + self._currentProgram + '.png')
                    self._label.setPixmap(pixmap)
                    self._label.update()

    def _newProcessIcon(self, request):
        if self._currentProgram != request[0]:
            pixmap = QPixmap()
            if request[0] is None:
                self._currentProgram = "null"
            else:
                self._currentProgram = request[0]
                if request[1] is not None:
                    path = self._iconsPath + self._currentProgram + '.png'
                    if not os.path.exists(path):
                        # Store new icon in cache
                        pixmap.loadFromData(base64.b64decode(request[1]))
                        pixmap.save(path)
                    else:
                        # Load from cache
                        pixmap.load(path)
            self._label.setPixmap(pixmap)
            self._label.update()
