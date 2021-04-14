from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

class DynamicTextBool(object):
    def __init__(self, window, stylesheet=["",""], txt=["",""], alignment="center",  pos=[0,0], metric=[]):
        self._stylesheet = stylesheet
        self._text = txt
        self._alignment = alignment
        self._pos = pos
        self._metric = metric
        self._is_true = False

        self._label = QLabel(window)
        self._label.setStyleSheet('QLabel{'+stylesheet[0]+'}')
        self._label.setAttribute(Qt.WA_TranslucentBackground)
        self._label.setText(txt[0])
        self._label.adjustSize()
        if alignment == "left":
            self._label.setAlignment(Qt.AlignLeft)
            self._label.move(pos[0],pos[1])
        elif alignment == "center":
            self._label.setAlignment(Qt.AlignHCenter)
            self._label.move(pos[0] - self._label.width() / 2,pos[1])
        elif alignment == "right":
            self._label.setAlignment(Qt.AlignRight)
            self._label.move(pos[0] - self._label.width(),pos[1])
        self._label.show()

    def update(self, status):
         if status is not None:
            value = status
            for i in range(0, len(self._metric['name'])):
                value = value[self._metric['name'][i]]
            is_true = value == self._metric['true_value']
            if is_true != self._is_true:
                if value == self._metric['true_value']:
                    self._label.setText(self._text[1])
                    self._label.setStyleSheet('QLabel{'+self._stylesheet[1]+'}')
                else:
                    self._label.setText(self._text[0])
                    self._label.setStyleSheet('QLabel{'+self._stylesheet[0]+'}')
                self._label.adjustSize()
                self._alignTxt()
                self._is_true = is_true

    def _alignTxt(self):
        if self._alignment == "left":
            self._label.move(self._pos[0],self._pos[1])
        elif self._alignment == "center":
            self._label.move(self._pos[0] - self._label.width() / 2,self._pos[1])
        elif self._alignment == "right":
            self._label.move(self._pos[0] - self._label.width(),self._pos[1])
