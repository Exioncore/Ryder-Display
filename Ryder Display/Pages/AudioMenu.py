import sys
import copy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton, QFrame

from Network.RyderClient import RyderClient

class AudioMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Audio")
        self.setWindowFlags(Qt.Popup | Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground, True)

        self.frame = QFrame(self)
        self.frame.setGeometry(0, 0, self.width(), self.height())
        self.frame.setStyleSheet('border:4px solid #333333;border-radius:30px;background:black;')
        self.frame.show()

    def resizeEvent(self, event):
        self.frame.setGeometry(0, 0, self.width(), self.height())

    def setParent(self, p):
        return

    def deleteLater(self):
        return

    def createUI(self, path, profiles, pos=[0,0]):
        self._path = path
        self._profiles = profiles

        gap = 25
        size = [100, 100]
        w_size = [size[0] * len(profiles) + gap * (len(profiles) + 1), size[1] + gap * 2]

        self.setGeometry(
            pos[0] - w_size[0] / 2, pos[1] - w_size[1] / 2,
            w_size[0], w_size[1]
        )

        self._buttons = []
        ofst = 0;
        for i in range(len(profiles)):
            ofst += gap
            btn = QPushButton('', self)
            btn.setIcon(QIcon(path + '/Resources/Audio/'+str(i)+'.png'))
            btn.setIconSize(QSize(size[0], size[1]))
            btn.setGeometry(ofst, gap, size[0], size[1])
            btn.setStyleSheet('border: none;')
            btn.clicked.connect(lambda x, i=i: self.onClick(i))
            btn.show()
            self._buttons.append(btn)
            ofst += size[0]

    def show(self):
        super().show()

    @pyqtSlot()
    def onClick(self, i: int):
        audio = self._profiles[i]
        print(
            "Request Audio Profile: "+audio['playbackDevice']+", "+
            audio['playbackDeviceCommunication']+", "+audio['recordingDevice']
        )
        RyderClient().send(
            "[\"audioProfile\",\""+
            audio['playbackDevice']+"\",\""+
            audio['playbackDeviceCommunication']+"\",\""+
            audio['recordingDevice']+"\"]"
        )
        self.close()
