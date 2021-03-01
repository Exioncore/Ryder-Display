import os
import gc
import sys
import gevent
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
        self.setWindowTitle("Ryder Display")

        # Set Geometry
        self.setGeometry(0, 0, 800, 480)

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

def killApp(app, server):
    server._steam._steamClient.disconnect()
    app.quit()
    # Ensure everything is killed
    gevent.killall([obj for obj in gc.get_objects() if isinstance(obj, gevent.Greenlet)])

if __name__ == "__main__":
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
    if sys.platform != 'win32':
        keyboard.on_press_key("q",  lambda _:killApp(app, server))

    # Run Server
    gevent.joinall([gevent.spawn(server.run), gevent.spawn(pyqtLoop, app)])
