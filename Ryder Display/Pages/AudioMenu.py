import sys
import copy
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton
from PyQt5.QtCore import QSize, pyqtSlot, Qt
from PyQt5.QtGui import QIcon

from Network.Client import Client

class AudioMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Audio")
        self.setWindowFlag(Qt.Popup)
        self.setStyleSheet(
            'border: 1px solid rgba(237,174,28,100%);'
        )

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
        print(str(i))
        Client.sendQuery(Client()._url, { "request": "audioProfile", "devices": self._profiles[i] } ,Client()._timeout)
        self.close()