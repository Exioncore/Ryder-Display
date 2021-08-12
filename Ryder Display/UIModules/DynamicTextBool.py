from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from UIModules.Utils import *
from Utils.InternalMetrics import InternalMetrics

class DynamicTextBool(object):
    def __init__(self, window, settings):
        # Retrieve settings
        ### UI Related
        self._stylesheet = settings['stylesheet'] if 'stylesheet' in settings and len(settings['stylesheet']) == 2 else ["", ""]
        pos = settings['pos'] if 'pos' in settings else [0, 0]
        alignment = settings['alignment'] if 'alignment' in settings else 7
        self._evaluation = settings['evaluation']
        if 'stylesheet' not in self._evaluation['true']:
            self._evaluation['true']['stylesheet'] = ""
        if 'stylesheet' not in self._evaluation['false']:
            self._evaluation['false']['stylesheet'] = ""
        if 'text' not in self._evaluation['true']:
            self._evaluation['true']['text'] = ""
        if 'text' not in self._evaluation['false']:
            self._evaluation['false']['text'] = ""
        ### Metric related
        self._metric = settings['metric']
        self._is_true = False
        # Create components
        self._label = QLabel(window)
        self._label.setAttribute(Qt.WA_TranslucentBackground)
        # Get size of longest text
        self._label.setStyleSheet('QLabel{'+self._evaluation['true']['stylesheet']+'}')
        self._label.setText(self._evaluation['true']['text'])
        self._label.adjustSize()
        size = [self._label.size().width(), self._label.fontMetrics().height()]
        self._label.setStyleSheet('QLabel{'+self._evaluation['false']['stylesheet']+'}')
        self._label.setText(self._evaluation['false']['text'])
        self._label.adjustSize()
        size[0] = size[0] if self._label.size().width() < size[0] else self._label.size().width()
        # Process alignment
        pos, h_alignment = getPosFromAlignment(pos, size, alignment)
        print(pos)
        if h_alignment < 0:
            self._label.setAlignment(Qt.AlignLeft)
        elif h_alignment > 0:
            self._label.setAlignment(Qt.AlignRight)
        else:
            self._label.setAlignment(Qt.AlignHCenter)
        self._label.move(pos[0], pos[1])

        self._label.show()

    def setParent(self, p):
        self._label.setParent(p)

    def deleteLater(self):
        self._label.deleteLater()

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
            is_true = (value == self._metric['target_value'] if self._metric['operator'] == '=' else 
                       (value > self._metric['target_value'] if self._metric['operator'] == '>' else 
                        (value < self._metric['target_value'] if self._metric['operator'] == '<' else False)))
            if is_true != self._is_true:
                if is_true:
                    self._label.setText(self._evaluation['true']['text'])
                    self._label.setStyleSheet('QLabel{'+self._evaluation['true']['stylesheet']+'}')
                else:
                    self._label.setText(self._evaluation['false']['text'])
                    self._label.setStyleSheet('QLabel{'+self._evaluation['false']['stylesheet']+'}')
                self._label.adjustSize()
                self._is_true = is_true
