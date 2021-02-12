import sys
import keyboard
import threading
from gevent import monkey
# PyQt5
from PyQt5.QtWidgets import QMainWindow, QApplication
from PyQt5.QtCore import Qt
# Ryder Display Files
from Pages.Home import Home
from Network.Server import Server

class Window(QMainWindow): 
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
        self.page.create_ui()

if __name__ == "__main__":
    # monkey.patch_all()
    # Create PyQt5 app
    app = QApplication(sys.argv)

    # Set app global stylesheet
    app.setStyleSheet('QLabel{color: rgb(225, 225, 225);}')

    # Flask server
    server = Server('Ryder Engine')
    threading.Thread(target=server.run, daemon=True).start()

    # Create the instance of our Window
    window = Window()
    window.initialize(server)

    # Hotkey for closing application
    if sys.platform != 'win32':
        keyboard.on_press_key("q", lambda _:app.exit())

    # Start the app
    sys.exit(app.exec())
