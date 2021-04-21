import os
import gc
import sys
import gevent
import keyboard
import threading
import _locale
# PyQt5
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QThread
# Ryder Display Files
from Utils.ConfigurationParser import ConfigurationParser
from Network.Server import Server
from Pages.Home import Home

class RyderDisplay(QMainWindow): 
    def __init__(self):
        super().__init__()

        # Setting title
        self.setWindowTitle("Ryder Display")

        # Parse configuration files
        self._ui, self._settings = ConfigurationParser.prepare(os.path.dirname(os.path.abspath(__file__)))

        # Set Geometry
        self.setGeometry(
            self._settings['ui']['x'], self._settings['ui']['y'],
            self._settings['ui']['width'], self._settings['ui']['height']
        )

        if self._settings['ui']['hide_title_bar']:
            # Hide title bar
            self.setWindowFlag(Qt.FramelessWindowHint)

    def initialize(self, server):
        self.page = Home(self, server)
        self.page.create_ui(os.path.dirname(os.path.abspath(__file__)), self._ui, self._settings)

        if self._settings['ui']['full_screen'] or 'full_screen' not in self._settings['ui']:
            # Show in Full Screen
            self.showFullScreen()
        else:
            # Show windowed
            self.show()

def pyqtLoop(app):
    while True:
        app.processEvents()
        gevent.sleep(0.005)

def killApp(e):
    if e.key() == Qt.Key_Q:
        os._exit(1)

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

    # Flask server
    server = Server('Ryder Display Server')

    # Create the instance of our Window
    window = RyderDisplay()
    window.initialize(server)

    # Hotkey for closing application
    window.keyPressEvent = killApp

    # Run Server
    gevent.joinall([gevent.spawn(server.run), gevent.spawn(pyqtLoop, app)])
