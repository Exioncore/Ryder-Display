import os
import sys
import math
import json
import gevent

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget

from UIModules.Utils import *
from UIModules.Graph import Graph
from Network.Monitor import Monitor
from Pages.AudioMenu import AudioMenu
from Pages.PopupMenu import PopupMenu
from Network.Hyperion import Hyperion
from UIModules.AppDrawer import AppDrawer
from Pages.HyperionMenu import HyperionMenu
from Network.RyderClient import RyderClient
from UIModules.MenuButton import MenuButton
from Pages.PowerPlanMenu import PowerPlanMenu
from UIModules.ProgressBar import ProgressBar
from UIModules.DynamicLabel import DynamicLabel
from Utils.InternalMetrics import InternalMetrics
from UIModules.DynamicLabelBool import DynamicLabelBool
from UIModules.RoundProgressBar import RoundProgressBar
from UIModules.CornerProgressBar import CornerProgressBar
from UIModules.ForegroundProcess import ForegroundProcess
from UIModules.Notifications.NotificationsHandler import NotificationsHandler

class ConfigurationParser(object):
    def prepare(path: str, ui_file: str = None, preloadedSettings = None):
        # Open settings and ui files
        if preloadedSettings == None:
            file = open(path + '/settings.json', 'r')
            settings = json.loads(file.read())
            file.close()
        else:
            settings = preloadedSettings
        if ui_file == None:
            ui_file = settings['ui']['initial_page'] if 'initial_page' in settings['ui'] else 'ui.json'
        file = open(path + '/' + ui_file, 'r')
        ui = json.loads(file.read())
        file.close()
        # Fill in variables in ui file
        ## UI section
        pos = ui['ui'][0]['geometry'][0:2].copy()
        new_pos = pos.copy()
        for entry in ui['ui']:
            # Positioning
            if 'geometry' in entry:
                update_pos = [True, True]
                for i in range(2):
                    if isinstance(entry['geometry'][i], str):
                        if entry['geometry'][i][0] != "d":
                            new_pos[i] = pos[i] + int(entry['geometry'][i])
                        else:
                            update_pos[i] = False
                            if len(entry['geometry'][i]) > 1:
                                new_pos[i] = pos[i] + int(entry['geometry'][i][1:])
                            else:
                                new_pos[i] = pos[i]
                    else:
                        new_pos[i] = entry['geometry'][i]
                entry['geometry'][0:2] = new_pos.copy()

                if update_pos[0]:
                    pos[0] = new_pos[0]
                if update_pos[1]:
                    pos[1] = new_pos[1]
            # Fill in variables
            if entry['type'] == 'StaticLabel':
                # Check if label message is tied to variable in settings
                entry['text'] = ConfigurationParser._concatTextWithVariables(entry['text'], settings['ui']['variables'])
            elif (entry['type'] == 'DynamicLabel' or entry['type'] == 'ProgressBar' or 
                  entry['type'] == 'RoundProgressBar' or entry['type'] == 'CornerProgressBar'):
                # Ensure element has bounds entry (This is optional for DynamicLabel)
                if 'bounds' in entry['metric']:
                    for i in range(2):
                        entry['metric']['bounds'][i] = ConfigurationParser._fillFieldFormula(
                            entry['metric']['bounds'][i], settings['ui']['variables'])
            elif entry['type'] == 'Graph':
                if 'bounds' in entry['metric']:
                    for i in range(2):
                        # Check if bound is a list (if it is it means we have a dynamic bound with a limit)
                        if isinstance(entry['metric']['bounds'][i], list):
                            entry['metric']['bounds'][i][1] = ConfigurationParser._fillFieldFormula(
                                entry['metric']['bounds'][i][1], settings['ui']['variables'])
                        # Check if bound is a formula
                        elif isinstance(entry['metric']['bounds'][i], str):
                            # Ensure we are looking at a formula and not dynamic bound without a limit
                            if entry['metric']['bounds'][i] != 'dynamic':
                                entry['metric']['bounds'][i] = ConfigurationParser._fillFieldFormula(
                                    entry['metric']['bounds'][i], settings['ui']['variables'])
        ## Unit converters section
        if 'unit_converters' in ui:
            for entry in ui['unit_converters']:
                entry = ui['unit_converters'][entry]
                entry['divisor'] = ConfigurationParser._fillFieldFormula(entry['divisor'], settings['ui']['variables'])
                if isinstance(entry['unit'], list):
                    for index in range(len(entry['unit'])):
                        entry['unit'][index] = ConfigurationParser._concatTextWithVariables(
                            entry['unit'][index], settings['ui']['variables']
                        )
                else:
                    entry['unit'] = ConfigurationParser._concatTextWithVariables(
                        entry['unit'], settings['ui']['variables']
                    )        
        # Initialization
        if preloadedSettings == None:
            if 'additional_metrics' in settings['services']['data_provider']:
                InternalMetrics().setSettings(
                    settings['services']['data_provider']['additional_metrics'], 
                    settings['services']['data_provider']['log_n_samples']
                )
            RyderClient().setup(
                settings['services']['data_provider']['ip'], 
                settings['services']['data_provider']['port'],
                settings['services']['data_provider']['password']
            )
            if 'hyperion' in settings['services']:
                Hyperion().setUrl(settings['services']['hyperion']['ip'], settings['services']['hyperion']['port'])
                Hyperion().getState()
        Monitor()

        return settings['ui']['fps'], ui, settings, ui_file

    def createUI(window, path, ui, settings, loadPage):
        ui_dynamic = []
        ui_static = []

        ts = math.ceil(settings['ui']['fps'] / 2)
        for entry in ui['ui']:
            is_dynamic = True
            elem = None
            # DEBUG
            if 'pos' in entry:
                print(entry['title'] + ", " + str(entry['pos'][0]) + ", " + str(entry['pos'][1]))
            elif 'geometry' in entry:
                print(entry['title'] + ", " + str(entry['geometry'][0]) + ", " + str(entry['geometry'][1]))
            else:
                print(entry['title'])
            # Parse Element
            if entry['type'] == 'ForegroundProcessIcon':
                elem = ForegroundProcess(window, entry, path)
            elif entry['type'] == 'Graph':
                if not isinstance(entry['unit'], dict):
                    if entry['unit'][0] == '*':
                        entry['unit'] = ui['unit_converters'][entry['unit'][1:]]
                elem = Graph(window, entry)
            elif entry['type'] == 'RoundProgressBar':
                elem = RoundProgressBar(window, ts, entry)
            elif entry['type'] == 'CornerProgressBar':
                elem = CornerProgressBar(window, ts, entry)
            elif entry['type'] == 'ProgressBar':
                elem = ProgressBar(window, ts, entry)
            elif entry['type'] == 'StaticLabel':
                elem = createLabel(window, entry)
                is_dynamic = False
            elif entry['type'] == 'Shape':
                elem = createShape(window, entry)
                is_dynamic = False
            elif entry['type'] == 'DynamicLabel':
                if not isinstance(entry['unit'], dict):
                    if entry['unit'][0] == '*':
                        entry['unit'] = ui['unit_converters'][entry['unit'][1:]]
                elem = DynamicLabel(window, entry)
            elif entry['type'] == 'DynamicLabelBool':
                elem = DynamicLabelBool(window, entry)
            elif entry['type'] == 'Image':
                elem = createImage(window, entry, path)
                is_dynamic = False
            elif entry['type'] == 'NotificationsHandler':
                if 'notifications_handler' in settings['services']:
                    elem = NotificationsHandler()
                    NotificationsHandler().setup(
                        window, settings['ui']['fps'], settings['services']['notifications_handler'], 
                        entry, path
                    )
            elif entry['type'] == 'PowerMenu':
                if 'power_plans' in settings['services']:
                    popup = PowerPlanMenu()
                    popup.createUI(path, settings['services']['power_plans'])
                    elem = MenuButton(window, entry['geometry'], path, '/Resources/Power/Power.png', popup)
                    is_dynamic = False
                else:
                    continue
            elif entry['type'] == 'HyperionMenu':
                if 'hyperion' in settings['services']:
                    popup = HyperionMenu()
                    popup.createUI(path)
                    elem = MenuButton(window, entry['geometry'], path, '/Resources/Hyperion/Logo.png', popup)
                    is_dynamic = False
                else:
                    continue
            elif entry['type'] == 'AudioMenu':
                if 'audio_presets' in settings['services']:
                    popup = AudioMenu()
                    popup.createUI(path, settings['services']['audio_presets'])
                    elem = MenuButton(window, entry['geometry'], path, '/Resources/Audio/Audio.png', popup)
                    is_dynamic = False
                else:
                    continue
            elif entry['type'] == 'PageLoader':
                elem = createPageLoader(window, entry, path)
                is_dynamic = False
            elif entry['type'] == 'PopupAppDrawer':
                # Popup
                popup = PopupMenu("App Drawer")
                # App Drawer
                appDrawer = AppDrawer(popup, entry['popup'], path, True)
                # Button
                elem = MenuButton(window, entry['geometry'], path, '/Resources/app-drawer.png', popup, [appDrawer])
                is_dynamic = False
            elif entry['type'] == 'AppDrawer':
                elem = AppDrawer(window, entry, path)
                is_dynamic = False

            if is_dynamic:
                ui_dynamic.append(elem)
            else:
                ui_static.append(elem)

        return ui_dynamic, ui_static

    def _concatTextWithVariables(entry, variables):
        if isinstance(entry, list):
            result = ""
            for elem in entry:
                if elem[0] == "*" and elem[1:] in variables:
                    result += str(variables[elem[1:]])
                else:
                    result += elem
            return result
        else:
            if len(entry) > 0 and entry[0] == "*" and entry[1:] in variables:
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
                    elif elements[i - 1] == "/":
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