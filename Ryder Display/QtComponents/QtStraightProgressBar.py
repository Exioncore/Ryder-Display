from enum import Enum
from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap

class QtStraightProgressBar(QWidget):
    class Direction(Enum):
        LEFT = 1
        RIGHT = 2
        UP = 3
        DOWN = 4

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._redraw = True

        self._bounds = [0, 100]
        self._bounds_range = self._bounds[1] - self._bounds[0]
        self._old_value = self._current_value = 0

        self._pen_background = QPen(QColor(40, 40, 40), self.width(), Qt.SolidLine)
        self._pen_foreground = QPen(QColor('red'), self.width() - 2, Qt.SolidLine)
        self.setFillDirection(QtStraightProgressBar.Direction.RIGHT)

        # Cache commonly reused variables
        self._rect = QRect(0, 0, self.width(), self.height())
        self.setRoundOff(False)

        # Double buffering
        self._buffer = QPixmap(self.width(), self.height())
        self._buffer.fill(Qt.transparent)

    def setBounds(self, start, end):
        self._bounds = [start, end]
        self._bounds_range = self._bounds[1] - self._bounds[0]

    def setForegroundColor(self, color):
        self._pen_foreground.setColor(color)

    def setBackgroundColor(self, color):
        self._pen_background.setColor(color)

    def setRoundOff(self, enable):
        if enable:
            self._pen_background.setCapStyle(Qt.RoundCap)
            self._pen_foreground.setCapStyle(Qt.RoundCap)
        else:
            self._pen_background.setCapStyle(Qt.FlatCap)
            self._pen_foreground.setCapStyle(Qt.FlatCap)

    def setValue(self, val):
        self._current_value = max(self._bounds[0], min(val, self._bounds[1]))

    def setFillDirection(self, val):
        self._fill_direction = val
        if val == QtStraightProgressBar.Direction.RIGHT or val == QtStraightProgressBar.Direction.LEFT:
            thickness = self.height()
        else:
            thickness = self.width()
        if  val == QtStraightProgressBar.Direction.RIGHT:
            self._p1 = [0, self.height() / 2]
            self._p2 = [self.width(), self.height() / 2]
        elif  val == QtStraightProgressBar.Direction.LEFT:
            self._p1 = [self.width(), self.height() / 2]
            self._p2 = [0, self.height() / 2]
        elif val == QtStraightProgressBar.Direction.UP:
            self._p1 = [self.width() / 2, self.height()]
            self._p2 = [self.width() / 2, 0]
        elif  val == QtStraightProgressBar.Direction.DOWN:
            self._p1 = [self.width() / 2, 0]
            self._p2 = [self.width() / 2, self.height()]

        self._pen_foreground.setWidth(thickness)
        self._pen_background.setWidth(thickness)

    def _drawSection(self, paint, start, end, pen):
        start_p = (start - self._bounds[0]) / self._bounds_range
        end_p = (end - self._bounds[0]) / self._bounds_range
        paint.setPen(pen)
        if self._fill_direction == QtStraightProgressBar.Direction.RIGHT:
            paint.drawLine(
                self.width() * start_p, self._p1[1],
                self.width() * end_p, self._p2[1]
            )
        elif self._fill_direction == QtStraightProgressBar.Direction.LEFT:
            paint.drawLine(
                self.width() - self.width() * start_p, self._p1[1],
                self.width() - self.width() * end_p, self._p2[1]
            )
        elif self._fill_direction == QtStraightProgressBar.Direction.UP:
            paint.drawLine(
                self._p1[0], self.height() - self.height() * start_p,
                self._p2[0], self.height() - self.height() * end_p
            )
        elif self._fill_direction == QtStraightProgressBar.Direction.DOWN:
            paint.drawLine(
                self._p1[0], self.height() * start_p,
                self._p2[0], self.height() * end_p
            )

    def setGeometry(self, x, y, w, h):
        """ Override setGeometry method """
        super().setGeometry(x, y, w, h)

        self._rect = QRect(0, 0, self.width(), self.height())
        self.setFillDirection(self._fill_direction)

        self._buffer = QPixmap(self.width(), self.height())
        self._buffer.fill(Qt.transparent)

    def redraw(self):
        self._redraw = True

    def paintEvent(self, e):
        """ Override Paint Function """
        paint = QPainter()
        paint.begin(self._buffer)
        paint.setRenderHint(QPainter.Antialiasing)

        if self._redraw:
            self._drawSection(paint, self._bounds[0], self._bounds[1], self._pen_background)
            self._drawSection(paint, self._bounds[0], self._current_value, self._pen_foreground)
            self._redraw = False
        else:
            if self._current_value > self._old_value:
                self._drawSection(paint, self._old_value, self._current_value, self._pen_foreground)
            else:
                self._drawSection(paint, self._old_value, self._current_value, self._pen_background)
        paint.end()

        paint.begin(self)
        paint.drawPixmap(self._rect, self._buffer)
        paint.end()

        self._old_value = self._current_value
