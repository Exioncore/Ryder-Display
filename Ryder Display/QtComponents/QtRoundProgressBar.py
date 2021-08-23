import math

from PyQt5.QtCore import Qt, QRect
from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap, QPainterPath

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
        self._fill_direction = -1

        self._foreground_color = QColor('red')
        self._background_color = QColor('black')
        self._border_color = QColor('white')

        self._thickness = 10
        self._border_thickness = 0

        # Cache commonly reused variables
        self._pen = QPen(self._foreground_color, self._thickness - self._border_thickness, Qt.SolidLine)

        arc_ofst = math.ceil(self._thickness / 2.0)
        self._rect = QRect(0, 0, self.width(), self.height())
        self._rect_arc = QRect(
            arc_ofst, arc_ofst,
            self.width() - arc_ofst * 2.0, self.height() - arc_ofst * 2.0
        )
        self.setRoundOff(False)

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
        self._foreground_color = color

    def setBackgroundColor(self, color):
        self._background_color = color

    def setBorderColor(self, color):
        self._border_color = color

    def setFillDirection(self, direction):
        self._fill_direction = direction

    def setRoundOff(self, enable):
        if enable == None:
            self._pen.setCapStyle(Qt.FlatCap)
        elif enable:
            self._pen.setCapStyle(Qt.RoundCap)
        else:
            self._pen.setCapStyle(Qt.SquareCap)

    def setValue(self, val):
        self._current_value = max(self._bounds[0], min(val, self._bounds[1]))
        self._target_angle = (self._max_angle / self._bounds_range * (self._current_value - self._bounds[0]))

    def setThickness(self, val):
        self._thickness = val
        arc_ofst = math.ceil(self._thickness / 2.0)
        self._rect_arc = QRect(
            arc_ofst, arc_ofst,
            self.width() - arc_ofst * 2.0, self.height() - arc_ofst * 2.0
        )
        self._pen.setWidth(self._thickness - self._border_thickness)

    def setBorderThickness(self, val):
        self._border_thickness = val
        self._pen.setWidth(self._thickness - self._border_thickness)

    def redraw(self):
        self._redraw = True

    def setGeometry(self, x, y, w, h):
        """ Override setGeometry method """
        super().setGeometry(x, y, w, h)

        arc_ofst = math.ceil(self._thickness / 2.0)
        self._rect = QRect(0, 0, self.width(), self.height())
        self._rect_arc = QRect(
            arc_ofst, arc_ofst,
            self.width() - arc_ofst * 2.0, self.height() - arc_ofst * 2.0
        )

        self._background_buffer = QPixmap(self.width(), self.height())
        self._background_buffer.fill(Qt.transparent)
        self._foreground_buffer = QPixmap(self.width(), self.height())
        self._foreground_buffer.fill(Qt.transparent)

    def paintEvent(self, e):
        """ Override Paint Function """
        paint = QPainter()

        # Draw background of the bar
        if self._redraw:
            self._background_buffer.fill(Qt.transparent)
            paint.begin(self._background_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            # Draw Border
            if self._border_thickness > 0:
                self._pen.setWidth(self._thickness)
                # Draw Border as a full bar
                self._pen.setColor(self._border_color)
                paint.setPen(self._pen) 
                paint.drawArc(self._rect_arc, self._angle_bounds[0] * 16.0, self._max_angle * 16.0)
                # Erase insides of the bar to create the border
                paint.setCompositionMode(QPainter.CompositionMode_Clear)
                self._pen.setWidth(self._thickness - self._border_thickness)
                paint.setPen(self._pen)
                paint.drawArc(self._rect_arc, self._angle_bounds[0] * 16.0, self._max_angle * 16.0)
                paint.setCompositionMode(QPainter.CompositionMode_SourceOver)
                #paint.setCompositionMode(QPainter.CompositionMode_Source)
            # Draw Background
            self._pen.setColor(self._background_color)
            paint.setPen(self._pen) 
            paint.drawArc(self._rect_arc, self._angle_bounds[0] * 16.0, self._max_angle * 16.0)
            paint.end()

            paint.setCompositionMode(QPainter.CompositionMode_SourceOver)
            self._pen.setColor(self._foreground_color)
        # Draw filled portion of the bar
        if self._current_angle != self._target_angle or self._redraw:
            paint.begin(self._foreground_buffer)
            paint.setRenderHint(QPainter.Antialiasing)
            self._foreground_buffer.fill(Qt.transparent)
            paint.setPen(self._pen)
            if self._fill_direction > 0:
                paint.drawArc(self._rect_arc, self._angle_bounds[0] * 16.0, self._target_angle * 16.0)
            elif self._fill_direction < 0:
                paint.drawArc(
                    self._rect_arc,
                    (self._angle_bounds[1] - self._target_angle) * 16.0, self._target_angle * 16.0
                )
            else:
                mid = (self._angle_bounds[1] - self._angle_bounds[0]) / 2 + self._angle_bounds[0]
                ofst = self._target_angle / 2
                paint.drawArc(self._rect_arc, (mid - ofst) * 16.0, self._target_angle * 16.0)
            paint.end()
            # Update flags
            self._current_angle = self._target_angle
            self._redraw = False

        paint.begin(self)
        paint.drawPixmap(self._rect, self._background_buffer)
        paint.drawPixmap(self._rect, self._foreground_buffer)
        paint.end()
