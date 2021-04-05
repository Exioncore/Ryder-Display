from PyQt5.QtWidgets import QProgressBar
from PyQt5.QtCore import Qt
from Utils.Transitioner import Transitioner

class ProgressBar(object):
    def __init__(self, window, transition_frames, pos=[0,0], size=[50,50], direction="left", style=["",""], metric=[], bounds=[0,100]):
        self._transition_frames = transition_frames
        self._metric = metric
        self._elem_t = Transitioner(bounds[0])
        self._elem_t.setMinMax(bounds[0], bounds[1])
        # UI
        self._elem = QProgressBar(window)
        self._elem.setGeometry(pos[0], pos[1], size[0], size[1])
        if direction == "left":
            self._elem.setOrientation(Qt.Horizontal)
            self._elem.setInvertedAppearance(True)
        elif direction == "right":
            self._elem.setOrientation(Qt.Horizontal)
        elif direction == "bottom":
            self._elem.setOrientation(Qt.Vertical)
            self._elem.setInvertedAppearance(True)
        elif direction == "top":
            self._elem.setOrientation(Qt.Vertical)
        self._elem.setMinimum(bounds[0])
        self._elem.setMaximum(bounds[1])
        self._elem.setTextVisible(False)
        self._elem.setStyleSheet("QProgressBar{"+style[0]+"}QProgressBar::chunk{"+style[1]+"}")
        self._elem.show()

    def update(self, status):
        if status is not None:
            value = status[self._metric[0]]
            for i in range(1, len(self._metric)):
                value = value[self._metric[i]]
            self._elem_t.transition(value, self._transition_frames)

        if not self._elem_t.isDone():
            self._elem.setValue(self._elem_t.update())
            self._elem.update()
