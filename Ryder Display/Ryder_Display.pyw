import gevent.monkey
gevent.monkey.patch_ssl()
import os
import gc
import sys
import gevent
import keyboard
import threading
import _locale
# PyQt5
from PyQt5.QtCore import Qt, QThread
from PyQt5.QtWidgets import QMainWindow, QApplication
# Ryder Display Files
from Pages.Home import Home
from Network.RyderClient import RyderClient
from Utils.ConfigurationParser import ConfigurationParser

class RyderDisplay(QMainWindow): 
    def __init__(self):
        super().__init__()
        self._firstInit = True

        # Setting title
        self.setWindowTitle("Ryder Display")

        # Parse configuration files
        self._ui, self._settings = ConfigurationParser.prepare(os.path.dirname(os.path.abspath(sys.argv[0])))

        # Set Geometry
        self.setGeometry(
            self._settings['ui']['x'], self._settings['ui']['y'],
            self._settings['ui']['width'], self._settings['ui']['height']
        )

        if self._settings['ui']['hide_title_bar']:
            # Hide title bar
            self.setWindowFlag(Qt.FramelessWindowHint)

    def initialize(self):
        self.page = Home(self)
        self.page.create_ui(os.path.dirname(os.path.abspath(sys.argv[0])), self._ui, self._settings)

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
        # This ensure the window is empty and no endpoints by the ui exist
        # Necessary to enable window reloading the UI
        RyderClient().clearEndPoints()
        self.page.dispose()
        for i in reversed(range(len(self.children()))):
            if i > 0:
                self.children()[i].deleteLater()
        # Reparse ui configuration file
        self._ui, self._settings = ConfigurationParser.prepare(
            os.path.dirname(os.path.abspath(sys.argv[0])),
            self._settings
        )
        self.initialize()
        # Call on_connect endpoint to initialize widgets properly when required
        if 'on_connect' in RyderClient()._endpoints:
            for endpoint in RyderClient()._endpoints['on_connect']:
                endpoint()

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
