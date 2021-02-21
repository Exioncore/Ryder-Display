from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

class DynamicText(object):
    def __init__(self, window, stylesheet="", longest_text="", unit ="", alignment="center",  pos=[0,0], metric=[]):
        if not isinstance(unit, list):
            if unit == "" or unit[0] == "_":
                self._unit_after = True
            else:
                self._unit_after = False
            self._unit = unit.replace('_','')
        else:
            self._unit = unit
        self._metric = metric
        self._label = QLabel(window)
        self._label.setStyleSheet('QLabel{'+stylesheet+'}')
        self._label.setAttribute(Qt.WA_TranslucentBackground)
        self._label.setText(longest_text)
        self._label.adjustSize()
        self._label.setText("")
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
            value = status[self._metric[0]]
            for i in range(1, len(self._metric)):
                value = value[self._metric[i]]

            if isinstance(self._unit, list):
                self._label.setText(self._refineValue(value))
            else:
                if self._unit_after:
                    self._label.setText(str(value)+self._unit)
                else:
                    self._label.setText(self._unit+str(value))

    def updateDirect(self, value):
        if isinstance(self._unit, list):
            self._label.setText(self._refineValue(value))
        else:
            if self._unit_after:
                self._label.setText(str(value)+self._unit)
            else:
                self._label.setText(self._unit+str(value))

    def _refineValue(self, value):
        if len(self._unit) == 2:
            i = 0
            decimalPoints = 0
            # Determine unit
            while value > self._unit[1][-1][0]:
                value /= self._unit[0][0]
                i += 1
            # Determine number of decimal points
            for form in self._unit[1]:
                if value < form[0]:
                    decimalPoints = form[1]
                    break
            # Compute the end result string
            result = '{:.{prec}f}'.format(value, prec=decimalPoints)
            if self._unit[0][1][i][-1] == "_":
                result = self._unit[0][1][i][0:-1] + result
            else:
                result += self._unit[0][1][i].replace('_','')
        else:
            value /= self._unit[0]
            result = '{:.{prec}f}'.format(value, prec=self._unit[1])
            if self._unit[2][-1] == "_":
                result = self._unit[2][0:-1] + result
            else:
                result += self._unit[2].replace('_','')
        return result
        