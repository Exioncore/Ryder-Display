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
    _mutex : Lock
    _label : QLabel
    _client : Client
    _currentProgram : str
    _iconsPath : str

    def __init__(self, window, client : Client, server : Server, pos=[0, 0], size=25):
        self._mutex = Lock()
        # Create cache folder if it doesn't exist
        self._iconsPath = os.getcwd() + '/cache/icons/'
        if not os.path.exists(self._iconsPath):
            os.makedirs(self._iconsPath)
        # Store variables
        self._client = client
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
        self._mutex.acquire()
        if request != self._currentProgram:
            if request == "null":
                self._currentProgram = "null"
                self._label.setPixmap(QPixmap())
                self._label.update()
            else:
                if not os.path.exists(self._iconsPath + request + '.png'):
                    # Request icon if not in cache
                    self._client.requestForegroundProcessIcon()
                else:
                    self._currentProgram = request
                    # Load from cache
                    pixmap = QPixmap()
                    pixmap.load(self._iconsPath + self._currentProgram + '.png')
                    self._label.setPixmap(pixmap)
                    self._label.update()
        self._mutex.release()

    def _newProcessIcon(self, request):
        self._mutex.acquire()
        if self._currentProgram != request[0]:
            pixmap = QPixmap()
            if request[0] == "null":
                self._currentProgram = "null"
            else:
                self._currentProgram = request[0]
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
        self._mutex.release()
