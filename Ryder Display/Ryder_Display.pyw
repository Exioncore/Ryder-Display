# Monkey Patching SSL module (Required in order to use Steam api)
import gevent.monkey
gevent.monkey.patch_ssl()
# Imports
import os
import gc
import sys
import time
import gevent
import _locale
import keyboard
import threading
# PyQt5
from PyQt5.QtCore import Qt, QThread, QTimer
from PyQt5.QtWidgets import QMainWindow, QApplication
# Ryder Display Files
from Utils.Singleton import Singleton
from Network.RyderClient import RyderClient
from Utils.InternalMetrics import InternalMetrics
from Utils.ConfigurationParser import ConfigurationParser

class RyderDisplay(QMainWindow):
    _ui_dynamic = []
    _ui_static = []
    _fps = 1
    _timer : QTimer = None
    _status = None
    _last_update = 0

    def __init__(self):
        super().__init__()
        # Initialization
        self._firstInit = True
        self._path = os.path.dirname(os.path.abspath(sys.argv[0]))
        # Setting title
        self.setWindowTitle("Ryder Display")
        # Parse configuration files
        self._fps, self._ui, self._settings, self._ui_file = ConfigurationParser.prepare(self._path)
        # Set Geometry
        self.setGeometry(
            self._settings['ui']['x'], self._settings['ui']['y'],
            self._settings['ui']['width'], self._settings['ui']['height']
        )
        # Hide title bar
        if self._settings['ui']['hide_title_bar']:
            self.setWindowFlag(Qt.FramelessWindowHint)
        # Server EndPoint
        RyderClient().addEndPoint('status', self._newStatus)

    def initialize(self):
        # Clear UI
        for i in range(len(self._ui_dynamic)):
            self._ui_dynamic[i].setParent(None)
            self._ui_dynamic[i].deleteLater()
        for i in range(len(self._ui_static)):
            self._ui_static[i].setParent(None)
            self._ui_static[i].deleteLater()
        # Handle Timer
        if self._timer != None:
            self._timer.stop()
        else:
            self._timer = QTimer()
            self._timer.timeout.connect(self.update)

        # Initialize UI
        self._ui_dynamic, self._ui_static = ConfigurationParser.createUI(self, self._path, self._ui, self._settings, self.loadPage)
        self._timer.start(1000 / self._fps)

        # First initialization
        if self._firstInit:
            self._firstInit = False
            if self._settings['ui']['full_screen'] or 'full_screen' not in self._settings['ui']:
                # Show in Full Screen
                self.showFullScreen()
            else:
                # Show windowed
                self.show()
            # Run Client
            gevent.spawn(RyderClient().run)

    def reloadUI(self):
        # Reparse ui configuration file
        self._fps, self._ui, self._settings, self._ui_file = ConfigurationParser.prepare(self._path, self._ui_file, self._settings)
        self.initialize()
        # Call on_connect endpoint to initialize widgets properly when required
        if 'on_connect' in RyderClient()._endpoints:
            for endpoint in RyderClient()._endpoints['on_connect']:
                endpoint()

    def loadPage(self, ui_file: str):
        self._ui_file = ui_file
        self.reloadUI()

    def update(self):
        # Update UI
        for elem in self._ui_dynamic:
            elem.update(self._status)
        # Reset
        if self._status is not None:
            self._last_update = time.time()
            self._status = None

    def _newStatus(self, data):
        self._status = data[1]
        InternalMetrics().update(self._status)

    def keyboardEvent(self, e):
        if e.key() == Qt.Key_Q:
            os._exit(1)
        elif e.key() == Qt.Key_R:
            self.reloadUI()

def pyqtLoop(app):
    while True:
        app.processEvents()
        gevent.sleep(0.005)

if __name__ == "__main__":
    # Set locale
    _locale._getdefaultlocale = (lambda *args: ['en_US', 'utf8'])

    # Create PyQt5 app
    app = QApplication(sys.argv)

    # Set app global stylesheet
    app.setStyleSheet(
        'QLabel{color: rgb(225, 225, 225);}'
        'QMainWindow{background-color:black;}'
        'QPushButton{background-color:black;}'
    )

    # Create the instance of our Window
    window = RyderDisplay()
    window.initialize()
    window.keyPressEvent = window.keyboardEvent

    # Run PyQt Loop
    gevent.joinall([gevent.spawn(pyqtLoop, app)])
