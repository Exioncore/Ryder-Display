from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from UIModules.Utils import *
from Utils.InternalMetrics import InternalMetrics

class DynamicLabel(object):
    def __init__(self, window, settings):
        # Retrieve settings
        ### UI Related
        stylesheet = settings['stylesheet'] if 'stylesheet' in settings else ""
        self._geometry = settings['geometry'] if 'geometry' in settings else [0, 0, 23, 7]
        self._unit_after = settings['unit_after'] if 'unit_after' in settings else True
        ### Metric related
        self._metric = settings['metric'] if 'metric' in settings else None
        if 'unit' in settings:
            self._unit = settings['unit']
        else:
            self._unit = ""
        # Create components
        self._label = QLabel(window)
        self._label.setStyleSheet('QLabel{'+stylesheet+'}')
        self._label.setAttribute(Qt.WA_TranslucentBackground)
        self._label.setText(self._geometry[2])
        self._label.adjustSize()
        # Process alignment
        if len(self._geometry) == 3: self._geometry.append(7)
        self._geometry[2] = self._label.size().width()
        self._geometry.insert(3, self._label.size().height())
        self._label.setText("")
        self._geometry, h_alignment = getPosFromGeometry(self._geometry)
        if h_alignment < 0:
            self._label.setAlignment(Qt.AlignLeft)
        elif h_alignment > 0:
            self._label.setAlignment(Qt.AlignRight)
        else:
            self._label.setAlignment(Qt.AlignHCenter)
        self._label.move(self._geometry[0], self._geometry[1])

        self._label.show()

    def setParent(self, p):
        self._label.setParent(p)

    def deleteLater(self):
        self._label.deleteLater()

    def move(self, x, y):
        self._geometry[0] = x; self._geometry[1] = y
        self._geometry, _ = getPosFromGeometry(self._geometry)
        self._label.move(self._geometry[0], self._geometry[1])

    def x(self):
        return self._geometry[0]

    def y(self):
        return self._geometry[1]

    def width(self):
        return self._geometry[2]

    def height(self):
        return self._geometry[3]

    def update(self, refresh = False):
        if refresh:
            if self._metric['name'][0][0] != "*":
                value = InternalMetrics().metrics
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
            value = value[-1]
            
            # Enforce value to be within bounds
            if 'bounds' in self._metric:
                value = min(max(value, self._metric['bounds'][0]), self._metric['bounds'][1])

            self.updateDirect(value)

    def updateDirect(self, value):
        if isinstance(self._unit, dict):
            self._label.setText(self._refineValue(value))
        else:
            if self._unit_after:
                self._label.setText(str(value)+self._unit)
            else:
                self._label.setText(self._unit+str(value))

    def _refineValue(self, value):
        if isinstance(self._unit, dict):
            if not isinstance(self._unit['unit'], list) or len(self._unit['unit']) == 1:
                if 'divisor' in self._unit:
                    value /= self._unit['divisor']
                if isinstance(self._unit['unit'], list):
                    unit_txt = self._unit['unit'][0]
                else:
                    unit_txt = self._unit['unit']
            else:
                i = 0
                # Determine unit
                while value > self._unit['divisor']:
                    value /= self._unit['divisor']
                    i += 1
                unit_txt = self._unit['unit'][i]
            # Determine decimal points
            if 'rounding' in self._unit:
                if isinstance(self._unit['rounding'], list):
                    for r in range(len(self._unit['rounding'])):
                        if value < self._unit['rounding'][r]['value']:
                            break;
                    r = min(r, len(self._unit['rounding']) - 1)
                    decimalPoints = self._unit['rounding'][r]['decimal_points']
                else:
                    decimalPoints = self._unit['rounding']
                result = '{:.{prec}f}'.format(value, prec=decimalPoints)
            else:
                result = str(value)
        else:
            result = str(value)
        # Add unit to value
        if self._unit_after:
            result = result + unit_txt
        else:
            result = unit_txt + result
        return result
        