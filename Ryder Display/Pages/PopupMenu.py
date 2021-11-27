from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QMainWindow, QFrame

class PopupMenu(QMainWindow):
    def __init__(self, title):
        super().__init__()

        self.setWindowTitle(title)
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.frame = QFrame(self)
        self.frame.setGeometry(0, 0, self.width(), self.height())
        self.frame.setStyleSheet('border:4px solid #333333;border-radius:30px;background:black;')
        self.frame.show()

    def resizeEvent(self, event):
        self.frame.setGeometry(0, 0, self.width(), self.height())


