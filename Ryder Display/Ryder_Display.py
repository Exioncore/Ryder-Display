import os
os.environ["GEVENT_SUPPORT"] = 'True'
#from gevent import monkey; monkey.patch_all();
import gevent

import sys
import keyboard
import threading
# PyQt5
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt, QThread
# Ryder Display Files
from Pages.Home import Home
from Network.Server import Server

class RyderDisplay(QMainWindow): 
    def __init__(self):
        super().__init__()

        # Setting title
        self.setWindowTitle("Ryder Engine")

        # Set Geometry
        self.setGeometry(0, 0, 800, 480)

        # Set background color
        self.setStyleSheet("background-color:black;")

        if sys.platform != 'win32':
            # Hide title bar
            self.setWindowFlag(Qt.FramelessWindowHint)
            # Show in Full Screen
            self.showFullScreen()
        else:
            # Show windowed
            self.show()

    def initialize(self, server):
        self.page = Home(self, server)
        self.page.create_ui(os.path.dirname(os.path.abspath(__file__)))

def pyqtLoop(app):
    while True:
        app.processEvents()
        gevent.sleep(0.005)

if __name__ == "__main__":
    # Create PyQt5 app
    app = QApplication(sys.argv)

    # Set app global stylesheet
    app.setStyleSheet('QLabel{color: rgb(225, 225, 225);}')

    # Flask server
    server = Server('Ryder Engine')

    # Create the instance of our Window
    window = RyderDisplay()
    window.initialize(server)

    # Hotkey for closing application
    if sys.platform != 'win32':
        keyboard.on_press_key("q", lambda _:app.exit())

    # Run Server
    gevent.joinall([gevent.spawn(server.run), gevent.spawn(pyqtLoop, app)])
