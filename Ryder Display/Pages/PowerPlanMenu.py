import sys
import copy
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import QSize, pyqtSlot, Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QPushButton

from Network.RyderClient import RyderClient

class PowerPlanMenu(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("Power Plan")
        self.setWindowFlag(Qt.Popup)
        self.setStyleSheet(
            'border: 1px solid rgba(237,174,28,100%);'
        )

    def setParent(self, p):
        return

    def deleteLater(self):
        return

    def createUI(self, path, plans, pos=[0,0]):
        self._path = path
        self._plans = plans

        gap = 25
        size = [100, 100]
        w_size = [size[0] * len(plans) + gap * (len(plans) + 1), size[1] + gap * 2]

        self.setGeometry(
            pos[0] - w_size[0] / 2, pos[1] - w_size[1] / 2,
            w_size[0], w_size[1]
        )

        self._buttons = []
        ofst = 0;
        for i in range(len(plans)):
            ofst += gap
            btn = QPushButton('', self)
            btn.setIcon(QIcon(path + '/Resources/Power/'+str(i)+'.png'))
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
        print("Request Power Plan: " + self._plans[i])
        RyderClient().send("[\"powerPlan\",\""+self._plans[i]+"\"]")
        self.close()
