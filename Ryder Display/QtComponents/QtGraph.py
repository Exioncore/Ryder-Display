from collections import deque
from PyQt5.QtWidgets import QWidget, QLabel
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QPainterPath, QFont
from PyQt5.QtCore import Qt, QRect

class QtGraph(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._bounds = [0, 1]
        self._bounds_range = self._bounds[1] - self._bounds[0]
        self._n_values = 30

        self._graph_scaling = [self.width() / self._n_values, self.height() / self._bounds_range]

        self._history = deque(maxlen=self._n_values)
        for i in range(self._n_values):
            self._history.append(0)

        self._graph_pen = QPen(QColor(36, 122, 228), 2, Qt.SolidLine)
        self._graph_pen.setCapStyle(Qt.FlatCap)
        self._graph_pen.setJoinStyle(Qt.RoundJoin)

    def setForegroundColor(self, color):
        self._graph_pen.setColor(color)

    def setThickness(self, val):
        self._graph_pen.setWidth(val)

    def setNumberOfValues(self, val):
        self._n_values = val
        self._graph_scaling[0] = self.width() / self._n_values
        self._history = deque(maxlen=self._n_values)
        for i in range(self._n_values):
            self._history.append(0)

    def setValue(self, val):
        self._history.append(val)
        self._bounds[1] = 0.01
        for v in self._history:
            self._bounds[1] = max(self._bounds[1], v)
        self._bounds_range = self._bounds[1] - self._bounds[0]
        self._graph_scaling[1] = self.height() / self._bounds_range

    def setGeometry(self, x, y, w, h):
        """ Override setGeometry method """
        super().setGeometry(x, y, w, h)
        self._graph_scaling = [self.width() / self._n_values, self.height() / self._bounds_range]

    def paintEvent(self, e):
        """ Override Paint Function """
        paint = QPainter()
        paint.begin(self)
        paint.setRenderHint(QPainter.Antialiasing)

        path = QPainterPath()
        first = True
        x = 0
        for val in self._history:
            if first:
                path.moveTo(x, self.height() - val * self._graph_scaling[1])
                first = False
            else:
                path.lineTo(x, self.height() - val * self._graph_scaling[1])
            x += self._graph_scaling[0]
        paint.setPen(self._graph_pen)
        paint.drawLine(0, self.height(), self.width(), self.height())
        paint.drawPath(path)
        paint.end()


