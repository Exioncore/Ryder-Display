from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel

from UIModules.Utils import *
from Utils.InternalMetrics import InternalMetrics

class DynamicTextBool(object):
    def __init__(self, window, settings):
        # Retrieve settings
        ### UI Related
        self._stylesheet = settings['stylesheet'] if 'stylesheet' in settings and len(settings['stylesheet']) == 2 else ["", ""]
        alignment = settings['alignment'] if 'alignment' in settings else 'center'
        self._pos = settings['pos'] if 'pos' in settings else [0, 0]
        self._text = settings['text'] if 'text' in settings and len(settings['text']) == 2 else ["", ""]
        ### Metric related
        self._metric = settings['metric']
        self._is_true = False
        # Create components
        self._label = QLabel(window)
        self._label.setStyleSheet('QLabel{'+self._stylesheet[0]+'}')
        self._label.setAttribute(Qt.WA_TranslucentBackground)
        self._label.setText(self._text[1])
        self._label.adjustSize()
        size = [self._label.size().width(), self._label.fontMetrics().height()]
        self._label.setText(self._text[0])
        self._label.adjustSize()
        size[0] = size[0] if self._label.size().width() < size[0] else self._label.size().width()
        self._pos = getPosFromAlignment(self._pos, size, alignment)
        if 'left' in alignment:
            self._label.setAlignment(Qt.AlignLeft)
        elif alignment == 'top' or alignment == 'center' or alignment == 'bottom':
            self._label.setAlignment(Qt.AlignHCenter)
        elif 'right' in alignment:
            self._label.setAlignment(Qt.AlignRight)
        self._label.move(self._pos[0], self._pos[1])
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
                    self._label.setText(self._text[1])
                    self._label.setStyleSheet('QLabel{'+self._stylesheet[1]+'}')
                else:
                    self._label.setText(self._text[0])
                    self._label.setStyleSheet('QLabel{'+self._stylesheet[0]+'}')
                self._label.adjustSize()
                self._is_true = is_true
