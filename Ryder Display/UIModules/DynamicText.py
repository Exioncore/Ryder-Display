from PyQt5.QtWidgets import QLabel
from PyQt5.QtCore import Qt

from Utils.InternalMetrics import InternalMetrics

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
            
            # Enforce value to be within bounds
            if 'bounds' in self._metric:
                value = min(max(value, self._metric['bounds'][0]), self._metric['bounds'][1])

            if isinstance(self._unit, list):
                # Value needs to be further refined before adding unit
                self._label.setText(self._refineValue(value))
            else:
                # Add metric unit either before or after value
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
        