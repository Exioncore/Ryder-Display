import os
import sys
import math
import json
import gevent

from UIModules.Utils import *
from UIModules.Graph import Graph
from Pages.AudioMenu import AudioMenu
from Network.Hyperion import Hyperion
from Pages.HyperionMenu import HyperionMenu
from Network.RyderClient import RyderClient
from UIModules.MenuButton import MenuButton
from Pages.AppDrawerMenu import AppDrawerMenu
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
                        if entry['text']['msg'][1:] in settings['ui']['variables']:
                            entry['text']['msg'] = settings['ui']['variables'][entry['text']['msg'][1:]]
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
        if preloadedSettings == None:
            RyderClient().setup(
                settings['services']['data_provider']['ip'], 
                settings['services']['data_provider']['port'],
                settings['services']['data_provider']['password']
            )
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
                elem = ForegroundProcess(window, entry, path)
            elif entry['type'] == 'Graph':
                if len(entry['unit']) > 0:
                    if entry['unit'][0] == '*':
                         entry['unit'] = ui['unit_converters'][entry['unit'][1:]]
                elem = Graph(window, entry)
            elif entry['type'] == 'RoundProgressBar':
                elem = RoundProgressBar(window, ts, entry)
            elif entry['type'] == 'CornerProgressBar':
                elem = CornerProgressBar(window, ts, entry)
            elif entry['type'] == 'ProgressBar':
                elem = ProgressBar(window, ts, entry)
            elif entry['type'] == 'StaticText':
                elem = createLabel(window, entry)
                is_dynamic = False
            elif entry['type'] == 'DynamicText':
                if len(entry['unit']) > 0:
                    if entry['unit'][0] == '*':
                        entry['unit'] = ui['unit_converters'][entry['unit'][1:]]
                elem = DynamicText(window, entry)
            elif entry['type'] == 'DynamicTextBool':
                elem = DynamicTextBool(window, entry)
            elif entry['type'] == 'Image':
                elem = createImage(window, entry)
                is_dynamic = False
            elif entry['type'] == 'NotificationsHandler':
                if 'notifications_handler' in settings['services']:
                    NotificationsHandler().setup(
                        window, settings['ui']['fps'], settings['services']['notifications_handler'], 
                        entry, path,
                    )
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
            elif entry['type'] == 'AppDrawerMenu':
                popup = AppDrawerMenu()
                popup.createUI(path)
                elem = MenuButton(window, entry['pos'], entry['size'], path, '/Resources/app-drawer.png', popup)
                is_dynamic = False

            if is_dynamic:
                ui_dynamic.append(elem)
            else:
                ui_static.append(elem)

        return settings['ui']['fps'], ui_dynamic

    def _concatTextWithVariables(entry, variables):
        result = ""
        if isinstance(entry, list):
            for elem in entry:
                if elem[0] == "*" and elem in variables:
                    result += str(variables[elem[1:]])
                else:
                    result += elem
            return result
        else:
            if entry[0] == "*" and entry in variables:
                return str(variables[entry[1:]])
        return entry

    def _fillFieldFormula(entry, variables):
        # Fill in field formula if bounds is a string instead of a number
        if isinstance(entry, str):
            elements = entry.split(' ')

            for i in range(0, len(elements), 2):
                if elements[i][0] == '*' or (elements[i][0] == '-' and elements[i][1] == '*'):
                    # Filter out the - if present
                    if elements[i][0] == '*':
                        index = elements[i][1:]
                        val = 1
                    else:
                        index = elements[i][2:]
                        val = -1
                    # Retrieve variable value
                    if index in variables:
                        val *= variables[index]
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