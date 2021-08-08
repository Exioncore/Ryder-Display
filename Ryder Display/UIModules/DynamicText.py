from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from UIModules.Utils import *
from Utils.InternalMetrics import InternalMetrics

class DynamicText(object):
    def __init__(self, window, settings):
        # Retrieve settings
        ### UI Related
        stylesheet = settings['stylesheet'] if 'stylesheet' in settings else ""
        self._alignment = settings['alignment'] if 'alignment' in settings else 'top-left'
        self._pos = settings['pos'] if 'pos' in settings else [0, 0]
        max_text_length = settings['max_text_length'] if 'max_text_length' in settings else "AAAAAAAAAAAAAAAAAAAAAAA"
        ### Metric related
        self._metric = settings['metric'] if 'metric' in settings else None
        if 'unit' in settings:
            if not isinstance(settings['unit'], list):
                if settings['unit'] == "" or settings['unit'][0] == "_":
                    self._unit_after = True
                else:
                    self._unit_after = False
                self._unit = settings['unit'].replace('_','')
            else:
                self._unit = settings['unit']
        else:
            self._unit = ""
        # Create components
        self._label = QLabel(window)
        self._label.setStyleSheet('QLabel{'+stylesheet+'}')
        self._label.setAttribute(Qt.WA_TranslucentBackground)
        self._label.setText(max_text_length)
        self._label.adjustSize()
        self._size = [self._label.size().width(), self._label.fontMetrics().height()]
        pos = getPosFromAlignment(self._pos, self._size, self._alignment)
        self._label.setText("")
        if 'left' in self._alignment:
            self._label.setAlignment(Qt.AlignLeft)
        elif self._alignment == 'top' or self._alignment == 'center' or self._alignment == 'bottom':
            self._label.setAlignment(Qt.AlignHCenter)
        elif 'right' in self._alignment:
            self._label.setAlignment(Qt.AlignRight)
        self._label.move(pos[0], pos[1])
        self._label.show()

    def setParent(self, p):
        self._label.setParent(p)

    def deleteLater(self):
        self._label.deleteLater()

    def move(self, x, y):
        self._pos = getPosFromAlignment([x, y], self._size, self._alignment)
        self._label.move(self._pos[0], self._pos[1])

    def x(self):
        return self._pos[0]

    def y(self):
        return self._pos[1]

    def width(self):
        return self._label.size().width()

    def height(self):
        return self._label.fontMetrics().height()

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
                value = InternalMetrics().metrics[self._metric['name'][0][1:]]
            
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
        