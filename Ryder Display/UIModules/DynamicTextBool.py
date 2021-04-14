from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

from Utils.InternalMetrics import InternalMetrics

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
            if self._metric['name'][0][0] != "*":
                value = status
                # Navigate status json to desired metric
                for i in range(0, len(self._metric['name'])):
                    if self._metric['name'][i] in value:
                        value = value[self._metric['name'][i]]
                    else:
                        # Interrupt update if desired metric is not found
                        return
            else:
                # Get computed metric
                value = InternalMetrics().metrics[self._metric['name'][0]]
            is_true = (value == self._metric['target_value'] if self._metric['operator'] == '=' else 
                       (value > self._metric['target_value'] if self._metric['operator'] == '>' else 
                        (value < self._metric['target_value'] if self._metric['operator'] == '<' else False)))
            if is_true != self._is_true:
                if is_true:
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
