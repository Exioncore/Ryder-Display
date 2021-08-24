import os
import sys

from PyQt5.QtGui import QIcon, QPixmap
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QLabel, QPushButton

def getPosFromAlignment(pos, size, alignment):
    newPos = [pos[0], pos[1]]
    h_alignment = 0
    if alignment == 5:
        newPos[0] -= size[0] / 2
        newPos[1] -= size[1] / 2
    else:
        if alignment >= 7 and alignment <= 9:
            newPos[1] = pos[1]
        elif alignment >= 1 and alignment <= 3:
            newPos[1] -= size[1]
        else:
            newPos[1] -= size[1] / 2
        if alignment == 1 or alignment == 4 or alignment == 7:
            newPos[0] = pos[0]
            h_alignment = -1
        elif alignment == 3 or alignment == 6 or alignment == 9:
            newPos[0] -= size[0]
            h_alignment = 1
        else:
            newPos[0] -= size[0] / 2
    return newPos, h_alignment

def getPosFromGeometry(geometry):
    h_alignment = 0
    if geometry[4] == 5:
        geometry[0] -= geometry[2] / 2
        geometry[1] -= geometry[3] / 2
    else:
        if geometry[4] >= 1 and geometry[4] <= 3:
            geometry[1] -= geometry[3]
        elif geometry[4] >= 4 and geometry[4] <= 6:
            geometry[1] -= geometry[3] / 2
        if geometry[4] == 1 or geometry[4] == 4 or geometry[4] == 7:
            h_alignment = -1
        elif geometry[4] == 3 or geometry[4] == 6 or geometry[4] == 9:
            geometry[0] -= geometry[2]
            h_alignment = 1
        else:
            geometry[0] -= geometry[2] / 2
    return geometry, h_alignment

def createLabel(window, settings):
    # Retrieve settings
    geometry = settings['geometry'] if 'geometry' in settings else [0, 0, 7]
    text = settings['text'] if 'text' in settings else ""
    stylesheet = settings['stylesheet'] if 'stylesheet' in settings else ""
    # Create components
    label = QLabel(window)
    label.setText(text)
    label.setStyleSheet('QLabel{'+stylesheet+'}')
    label.setAttribute(Qt.WA_TranslucentBackground)
    label.adjustSize()
    # Process alignment
    if len(geometry) == 2: geometry.append(7)
    geometry.insert(2, label.size().width())
    geometry.insert(3, label.size().height())
    geometry, h_alignment = getPosFromGeometry(geometry)
    if h_alignment < 0:
        label.setAlignment(Qt.AlignLeft)
    elif h_alignment > 0:
        label.setAlignment(Qt.AlignRight)
    else:
        label.setAlignment(Qt.AlignHCenter)
    label.move(geometry[0], geometry[1])
    label.show()
    return label

def createPageLoader(window, settings, path):
    # Retrieve settings
    icon = settings['icon'] if 'icon' in settings else ''
    pos = settings['pos'] if 'pos' in settings else [0, 0]
    size = settings['size'] if 'size' in settings else [50, 50]
    alignment = settings['alignment'] if 'alignment' in settings else 7
    # Process Settings
    pos, _ = getPosFromAlignment(pos, size, alignment)
    # Create component
    elem = QPushButton('', window)
    elem.setStyleSheet('border: none;')
    elem.setIcon(QIcon(path + '/Resources/' + icon))
    elem.setIconSize(QSize(size[0], size[1]))
    elem.setGeometry(pos[0], pos[1], size[0], size[1])
    elem.clicked.connect(lambda:window.loadPage(settings['ui_file']))
    elem.show()
    return elem

def createImage(window, settings, path):
    # Retrieve settings
    image = settings['path'] if 'path' in settings else ''
    geometry = settings['geometry'] if 'geometry' in settings else [0, 0, 50, 50, 7]
    # Process alignment
    if len(geometry) == 4: geometry.append(7)
    geometry, _ = getPosFromGeometry(geometry)
    # Process image path
    path = path+'/Resources/'+image
    extension = path[(path.rfind('.')+1):]
    # Create components
    elem = None
    if extension == 'svg':
        elem = QSvgWidget(path, window)
        elem.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        elem.show()
    else:
        elem = QLabel(window)
        elem.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
        pixmap = QPixmap(path)
        elem.setPixmap(pixmap)
        elem.show()
    return elem

def createShape(window, settings):
    # Retrieve settings
    geometry = settings['geometry'] if 'geometry' in settings else [0, 0, 50, 50, 7]
    stylesheet = settings['stylesheet'] if 'stylesheet' in settings else ""
    # Process alignment
    if len(geometry) == 4: geometry.append(7)
    geometry, _ = getPosFromGeometry(geometry)
    # Create components
    label = QLabel(window)
    label.setStyleSheet('QLabel{'+stylesheet+'}')
    label.setGeometry(geometry[0], geometry[1], geometry[2], geometry[3])
    label.show()
    return label
