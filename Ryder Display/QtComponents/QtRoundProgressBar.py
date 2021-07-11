from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap

class QtRoundProgressBar(QWidget):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self._redraw = True

        self._bounds = [0, 100]
        self._bounds_range = self._bounds[1] - self._bounds[0]
        self._current_value = self._bounds[0]

        self._angle_bounds = [-45, 225]
        self._max_angle = self._angle_bounds[1] - self._angle_bounds[0]
        self._current_angle = self._target_angle = 0
        self._overdraw = 1.0
        self._fill_direction = -1

        # Cache commonly reused variables
        thickness = 10
        ofst_b = thickness / 2.0

        self._pen_background = QPen(QColor(40, 40, 40), thickness, Qt.SolidLine)
        self._pen_foreground = QPen(QColor('red'), thickness - 2, Qt.SolidLine)
        self._rect = QRect(0, 0, self.width(), self.height())
        self._rect_arc = QRect(
            ofst_b, ofst_b,
            self.width() - ofst_b * 2.0, self.height() - ofst_b * 2.0
        )
        self.setRoundOff(False)

        # Double buffering
        self._background_buffer = QPixmap(self.width(), self.height())
        self._background_buffer.fill(Qt.transparent)

    def setBounds(self, start, end):
        mul = (self._current_value - self._bounds[0]) / self._bounds_range
        self._bounds = [start, end]
        self._bounds_range = self._bounds[1] - self._bounds[0]
        self._current_value = self._bounds_range * mul + self._bounds[0]
        self._target_angle = self._current_angle = (self._max_angle / self._bounds_range * (self._current_value - self._bounds[0]))

    def setAngleBounds(self, start, end):
        self._angle_bounds = [start, end]
        self._max_angle = self._angle_bounds[1] - self._angle_bounds[0]
        self._target_angle = self._current_angle = self._max_angle / self._bounds_range * self._current_value

    def setForegroundColor(self, color):
        self._pen_foreground.setColor(color)

    def setBackgroundColor(self, color):
        self._pen_background.setColor(color)

    def setRefreshOverdraw(self, val):
        self._overdraw = val

    def setFillDirection(self, direction):
        self._fill_direction = direction

    def setRoundOff(self, enable):
        if enable:
            self._pen_background.setCapStyle(Qt.RoundCap)
            self._pen_foreground.setCapStyle(Qt.RoundCap)
        else:
            self._pen_background.setCapStyle(Qt.FlatCap)
            self._pen_foreground.setCapStyle(Qt.FlatCap)

    def setValue(self, val):
        self._current_value = max(self._bounds[0], min(val, self._bounds[1]))
        self._target_angle = (self._max_angle / self._bounds_range * (self._current_value - self._bounds[0]))

    def setThickness(self, val):
        ofst_b = val / 2.0
        self._rect_arc = QRect(ofst_b, ofst_b, self.width() - ofst_b * 2.0, self.height() - ofst_b * 2.0)
        self._pen_background.setWidth(val)
        self._pen_foreground.setWidth(val - 2)

    def redraw(self):
        self._redraw = True

    def setGeometry(self, x, y, w, h):
        """ Override setGeometry method """
        super().setGeometry(x, y, w, h)

        ofst_b = self._pen_background.width() / 2.0
        self._rect = QRect(0, 0, self.width(), self.height())
        self._rect_arc= QRect(ofst_b, ofst_b, self.width() - ofst_b * 2.0, self.height() - ofst_b * 2.0)

        self._background_buffer = QPixmap(self.width(), self.height())
        self._background_buffer.fill(Qt.transparent)
        self._foreground_buffer = QPixmap(self.width(), self.height())
        self._foreground_buffer.fill(Qt.transparent)

    def paintEvent(self, e):
        """ Override Paint Function """
        paint = QPainter()

        if self._redraw:
            paint.begin(self._background_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            self._background_buffer.fill(Qt.transparent)
            paint.setPen(self._pen_background) 
            paint.drawArc(self._rect_arc, (self._angle_bounds[0]) * 16.0, self._max_angle * 16.0)
            paint.end()

            paint.begin(self._foreground_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            self._foreground_buffer.fill(Qt.transparent)
            paint.setPen(self._pen_foreground)
            if self._fill_direction > 0:
                paint.drawArc(self._rect_arc, self._angle_bounds[0] * 16.0, self._target_angle * 16.0)
            else:
                paint.drawArc(
                    self._rect_arc,
                    (self._angle_bounds[1] - self._target_angle) * 16.0, self._target_angle * 16.0
                )
            paint.end()
            self._redraw = False
        else:
            if self._current_angle != self._target_angle:
                paint.begin(self._foreground_buffer)
                paint.setRenderHint(QPainter.Antialiasing)
                self._foreground_buffer.fill(Qt.transparent)
                paint.setPen(self._pen_foreground)
                if self._fill_direction > 0:
                    paint.drawArc(self._rect_arc, self._angle_bounds[0] * 16.0, self._target_angle * 16.0)
                else:
                    paint.drawArc(
                        self._rect_arc,
                        (self._angle_bounds[1] - self._target_angle) * 16.0, self._target_angle * 16.0
                    )
                paint.end()
                self._current_angle = self._target_angle

        paint.begin(self)
        paint.drawPixmap(self._rect, self._background_buffer)
        paint.drawPixmap(self._rect, self._foreground_buffer)
        paint.end()

        self._current_angle = self._target_angle



