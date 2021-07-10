import os
import sys
from PyQt5.QtCore import Qt
from PyQt5.QtSvg import QSvgWidget
from PyQt5.QtWidgets import QLabel

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
        else:
            newPos[1] -= size[1] / 2
        if 'left' in alignment:
            newPos[0] = pos[0]
        elif 'right' in alignment:
            newPos[0] -= size[0]
        else:
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
    elif alignment == 'top' or alignment == 'center' or alignment == 'bottom':
        label.setAlignment(Qt.AlignHCenter)
    elif 'right' in alignment:
        label.setAlignment(Qt.AlignRight)
    label.move(pos[0], pos[1])
    label.show()
    return label

def createImage(window, settings):
    # Retrieve settings
    path = settings['path'] if 'path' in settings else ''
    pos = settings['pos'] if 'pos' in settings else [0, 0]
    size = settings['size'] if 'size' in settings else [50, 50]
    alignment = settings['alignment'] if 'alignment' in settings else 'center'
    # Create components
    path = os.path.dirname(sys.argv[0])+'/Resources/'+path
    pos = getPosFromAlignment(pos, size, alignment)
    extension = path[(path.rfind('.')+1):]
    elem = None
    if extension == 'svg':
        elem = QSvgWidget(path, window)
        elem.setGeometry(pos[0], pos[1], size[0], size[1])
        elem.show()
    return elem
