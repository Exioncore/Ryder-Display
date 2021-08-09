import os
import sys

from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt, QSize
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QLabel, QPushButton

def getPosFromAlignment(pos, size, alignment):
    newPos = [pos[0], pos[1]]
    if 'center' in alignment:
        newPos[0] -= size[0] / 2
        newPos[1] -= size[1] / 2
    else:
        if 'top' in alignment:
            newPos[1] = pos[1]
        elif 'bottom' in alignment:
            newPos[1] -= size[1]
        elif 'vmid' in alignment:
            newPos[1] -= size[1] / 2
        if 'left' in alignment:
            newPos[0] = pos[0]
        elif 'right' in alignment:
            newPos[0] -= size[0]
        elif 'hmid':
            newPos[0] -= size[0] / 2
    return newPos

def createLabel(window, settings):
    # Retrieve settings
    stylesheet = settings['stylesheet'] if 'stylesheet' in settings else ""
    text = settings['text']['msg'] if 'text' in settings and 'msg' in settings['text'] else ""
    alignment = settings['text']['alignment'] if 'text' in settings and 'alignment' in settings['text'] else 'top-left'
    pos = settings['pos'] if 'pos' in settings else [0, 0]
    # Create components
    label = QLabel(window)
    label.setText(text)
    label.setStyleSheet('QLabel{'+stylesheet+'}')
    label.setAttribute(Qt.WA_TranslucentBackground)
    label.adjustSize()
    pos = getPosFromAlignment(pos, [label.size().width(), label.size().height()], alignment)
    if 'left' in alignment:
        label.setAlignment(Qt.AlignLeft)
    elif (alignment == 'top' or alignment == 'center' or alignment == 'bottom') or 'hmid' in alignment:
        label.setAlignment(Qt.AlignHCenter)
    elif 'right' in alignment:
        label.setAlignment(Qt.AlignRight)
    label.move(pos[0], pos[1])
    label.show()
    return label

def createPageLoader(window, settings, path):
    # Retrieve settings
    icon = settings['icon'] if 'icon' in settings else ''
    pos = settings['pos'] if 'pos' in settings else [0, 0]
    size = settings['size'] if 'size' in settings else [50, 50]
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
    pos = settings['pos'] if 'pos' in settings else [0, 0]
    size = settings['size'] if 'size' in settings else [50, 50]
    alignment = settings['alignment'] if 'alignment' in settings else 'center'
    # Create components
    path = path+'/Resources/'+image
    pos = getPosFromAlignment(pos, size, alignment)
    extension = path[(path.rfind('.')+1):]
    elem = None
    if extension == 'svg':
        elem = QSvgWidget(path, window)
        elem.setGeometry(pos[0], pos[1], size[0], size[1])
        elem.show()
    return elem
