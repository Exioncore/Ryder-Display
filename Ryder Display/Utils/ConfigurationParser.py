import os
import sys
import math
import json
from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QLabel
from PyQt5.QtSvg import QSvgWidget

from UIModules.Graph import Graph
from Pages.AudioMenu import AudioMenu
from Network.Hyperion import Hyperion
from Pages.HyperionMenu import HyperionMenu
from Network.RyderClient import RyderClient
from UIModules.MenuButton import MenuButton
from Pages.PowerPlanMenu import PowerPlanMenu
from UIModules.ProgressBar import ProgressBar
from UIModules.DynamicText import DynamicText
from Utils.InternalMetrics import InternalMetrics
from UIModules.DynamicTextBool import DynamicTextBool
from UIModules.RoundProgressBar import RoundProgressBar
from UIModules.CornerProgressBar import CornerProgressBar
from UIModules.ForegroundProcess import ForegroundProcess
from UIModules.Notifications.NotificationsHandler import NotificationsHandler

class ConfigurationParser(object):
    def prepare(path: str, preloadedSettings = None):
        # Open ui and settings files
        file = open(path + '/ui.json', 'r')
        ui = json.loads(file.read())
        file.close()
        if preloadedSettings == None:
            file = open(path + '/settings.json', 'r')
            settings = json.loads(file.read())
            file.close()
        else:
            settings = preloadedSettings
        # Fill in variables in ui file
        ## UI section
        pos = ui['ui'][0]['pos'].copy()
        new_pos = pos.copy()
        for entry in ui['ui']:
            # Positioning
            if 'pos' in entry:
                update_pos = [True, True]
                for i in range(2):
                    if isinstance(entry['pos'][i], str):
                        if entry['pos'][i][0] != "d":
                            new_pos[i] = pos[i] + int(entry['pos'][i])
                        else:
                            update_pos[i] = False
                            if len(entry['pos'][i]) > 1:
                                new_pos[i] = pos[i] + int(entry['pos'][i][1:])
                            else:
                                new_pos[i] = pos[i]
                    else:
                        new_pos[i] = entry['pos'][i]
                entry['pos'] = new_pos.copy()

                if update_pos[0]:
                    pos[0] = new_pos[0]
                if update_pos[1]:
                    pos[1] = new_pos[1]
            # Fill in variables
            if entry['type'] == 'StaticText':
                # Check if label message is tied to variable in settings
                if entry['text']['msg'][0] == '*':
                    # Check if variable exists
                    if isinstance(entry['text']['msg'], list):
                        entry['text']['msg'] = ConfigurationParser._concatTextWithVariables(entry['text']['msg'], settings['ui']['variables'])
                    else:
                        if entry['text']['msg'] in settings['ui']['variables']:
                            entry['text']['msg'] = settings['ui']['variables'][entry['text']['msg']]
            elif (entry['type'] == 'DynamicText' or entry['type'] == 'ProgressBar' or 
                  entry['type'] == 'RoundProgressBar' or entry['type'] == 'CornerProgressBar'):
                # Ensure element has bounds entry (This is optional for DynamicText)
                if 'bounds' in entry['metric']:
                    for i in range(2):
                        entry['metric']['bounds'][i] = ConfigurationParser._fillFieldFormula(
                            entry['metric']['bounds'][i], settings['ui']['variables'])
        ## Unit converters section
        for entry in ui['unit_converters']:
            entry = ui['unit_converters'][entry]
            if len(entry) == 2:
                entry[0][0] = ConfigurationParser._fillFieldFormula(entry[0][0], settings['ui']['variables'])
                if isinstance(entry[0][1], list):
                    for index in range(len(entry[0][1])):
                        entry[0][1][index] = ConfigurationParser._concatTextWithVariables(entry[0][1][index], settings['ui']['variables'])
                else:
                    entry[0][1] = ConfigurationParser._concatTextWithVariables(entry[0][1], settings['ui']['variables'])
            elif len(entry) == 3:
                entry[0] = ConfigurationParser._fillFieldFormula(entry[0], settings['ui']['variables'])
                entry[2] = ConfigurationParser._concatTextWithVariables(entry[2], settings['ui']['variables'])
        
        # Initialization
        RyderClient().setup(settings['services']['data_provider']['ip'], settings['services']['data_provider']['port'])
        if 'hyperion' in settings['services']:
            Hyperion().setUrl(settings['services']['hyperion']['ip'], settings['services']['hyperion']['port'])
            Hyperion().getState()

        return ui, settings

    def createUI(window, path, ui, settings):
        ui_dynamic = []
        ui_static = []

        ts = math.ceil(settings['ui']['fps'] / 2)
        InternalMetrics().setSettings(ui['computed_metrics'])
        for entry in ui['ui']:
            is_dynamic = True
            elem = None
            # DEBUG
            if 'pos' in entry:
                print(entry['title'] + ", " + str(entry['pos'][0]) + ", " + str(entry['pos'][1]))
            else:
                print(entry['title'])
            # Parse Element
            if entry['type'] == 'ForegroundProcessIcon':
                elem = ForegroundProcess(window, entry['pos'], entry['size'], path)
            elif entry['type'] == 'Graph':
                unit = entry['unit']
                if len(entry['unit']) > 0:
                    if entry['unit'][0] == '*':
                        unit = ui['unit_converters'][entry['unit'][1:]]
                elem = Graph(
                    window, entry['pos'], entry['size'], entry['color'], entry['thickness'],
                    entry['max_text_length'], entry['stylesheet'], unit, entry['n_values'], entry['metric']
                )
            elif entry['type'] == 'RoundProgressBar':
                elem = RoundProgressBar(
                    window, ts,
                    entry['pos'], entry['size'], entry['angle'], entry['colors'], entry['thickness'],
                    entry['metric']
                )
            elif entry['type'] == 'CornerProgressBar':
                elem = CornerProgressBar(
                    window, ts,
                    entry['pos'], entry['size'], entry['direction'], entry['colors'], entry['thickness'],
                    entry['cornerRadius'], entry['metric']
                )
            elif entry['type'] == 'ProgressBar':
                elem = ProgressBar(
                    window, ts,
                    entry['pos'], entry['size'], entry['direction'], entry['stylesheet'],
                    entry['metric']
                )
            elif entry['type'] == 'StaticText':
                elem = ConfigurationParser._createLabel(
                    window,
                    entry['stylesheet'],
                    entry['text']['msg'],
                    entry['text']['alignment'],
                    entry['pos']
                )
                is_dynamic = False
            elif entry['type'] == 'DynamicText':
                unit = entry['unit']
                if len(entry['unit']) > 0:
                    if entry['unit'][0] == '*':
                        unit = ui['unit_converters'][entry['unit'][1:]]
                elem = DynamicText(
                    window,
                    entry['stylesheet'], entry['max_text_length'], unit, entry['alignment'], entry['pos'], entry['metric']
                )
            elif entry['type'] == 'DynamicTextBool':
                elem = DynamicTextBool(
                    window,
                    entry['stylesheet'], entry['text'], entry['alignment'], entry['pos'], entry['metric']
                )
            elif entry['type'] == 'Image':
                elem = ConfigurationParser._createImage(
                    window, entry['path'], entry['pos'], entry['size']
                )
                is_dynamic = False
            elif entry['type'] == 'NotificationsHandler':
                if 'notifications_handler' in settings['services']:
                    elem = NotificationsHandler(
                        window, settings['ui']['fps'], settings['services']['notifications_handler'], 
                        entry['stylesheet'], entry['img_margin'], entry['location'], entry['height'], path
                    )
                else:
                    continue
            elif entry['type'] == 'PowerMenu':
                if 'power_plans' in settings['services']:
                    popup = PowerPlanMenu()
                    popup.createUI(path, settings['services']['power_plans'])
                    elem = MenuButton(window, entry['pos'], entry['size'], path, '/Resources/Power/Power.png', popup)
                    is_dynamic = False
                else:
                    continue
            elif entry['type'] == 'HyperionMenu':
                if 'hyperion' in settings['services']:
                    popup = HyperionMenu()
                    popup.createUI(path)
                    elem = MenuButton(window, entry['pos'], entry['size'], path, '/Resources/Hyperion/Logo.png', popup)
                    is_dynamic = False
                else:
                    continue
            elif entry['type'] == 'AudioMenu':
                if 'audio_presets' in settings['services']:
                    popup = AudioMenu()
                    popup.createUI(path, settings['services']['audio_presets'])
                    elem = MenuButton(window, entry['pos'], entry['size'], path, '/Resources/Audio/Audio.png', popup)
                    is_dynamic = False
                else:
                    continue

            if is_dynamic:
                ui_dynamic.append(elem)
            else:
                ui_static.append(elem)

        return settings['ui']['fps'], ui_dynamic

    def _createLabel(window, stylesheet, text, alignment, pos):
        label = QLabel(window)
        label.setText(text)
        label.setStyleSheet('QLabel{'+stylesheet+'}')
        label.setAttribute(Qt.WA_TranslucentBackground)
        label.adjustSize()
        if alignment == "left":
            label.setAlignment(Qt.AlignLeft)
            label.move(pos[0],pos[1])
        elif alignment == "center":
            label.setAlignment(Qt.AlignHCenter)
            label.move(pos[0] - label.width() / 2,pos[1])
        elif alignment == "right":
            label.setAlignment(Qt.AlignRight)
            label.move(pos[0] - label.width(),pos[1])
        label.show()
        return label

    def _createImage(window, image, pos, size):
        path = os.path.dirname(sys.argv[0])+'/Resources/'+image
        extension = path[(path.rfind('.')+1):]
        elem = None
        if extension == 'svg':
            elem = QSvgWidget(path, window)
            elem.setGeometry(pos[0], pos[1], size[0], size[1])
            elem.show()
        return elem

    def _concatTextWithVariables(entry, variables):
        result = ""
        if isinstance(entry, list):
            for elem in entry:
                if elem[0] == "*" and elem in variables:
                    result += str(variables[elem])
                else:
                    result += elem
            return result
        else:
            if entry[0] == "*" and entry in variables:
                return str(variables[entry])
        return entry

    def _fillFieldFormula(entry, variables):
        # Fill in field formula if bounds is a string instead of a number
        if isinstance(entry, str):
            elements = entry.split(' ')

            for i in range(0, len(elements), 2):
                if elements[i][0] == '*' or (elements[i][0] == '-' and elements[i][1] == '*'):
                    # Filter out the - if present
                    if elements[i][0] == '*':
                        index = elements[i]
                    else:
                        index = elements[1:]
                    # Retrieve variable value
                    if index in variables:
                        val = variables[index]
                        if elements[i][0] == '-':
                            val *= -1
                else:
                    # Convert value to int unless variable requires float type
                    val = ConfigurationParser._convertStrToIntOrFloat(elements[i])

                # Perform mathemetical operation if not 1st
                if i > 0:
                    if elements[i - 1] == "*":
                        value *= val
                    elif elements[i - 1] == "+":
                        value += val
                    elif elements[i - 1] == "-":
                        value -= val
                    if elements[i - 1] == "/":
                        value /= val
                else:
                    value = val
            # Replace entry formula with the computed formula
            return value
        return entry

    def _convertStrToIntOrFloat(val):
        try:
            a = float(val)
            b = int(val)
        except (TypeError, ValueError):
            return False
        else:
            if a == b:
                return b
            else:
                return a
