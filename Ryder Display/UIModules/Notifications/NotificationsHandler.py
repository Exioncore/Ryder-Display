import math
import gevent
from threading import Lock

from PyQt5.QtWidgets import QWidget

from Network.Hyperion import Hyperion
from Utils.Transitioner import Transitioner
from Network.RyderClient import RyderClient
from Network.SteamNotifier import SteamNotifier
from Network.DiscordNotifier import DiscordNotifier
from UIModules.Notifications.Notification import Notification

class NotificationsHandler(object):
    _mutex : Lock
    _mutexUpdate : Lock
    _live_queue = []
    _queue = []
    _free_notifications = []
    _slot = 0
    _timer = 0
    _onGoing = False
    
    def __init__(self, window, fps, settings, notificationStyle, path=''):
        stylesheet = notificationStyle['stylesheet']
        img_margin = notificationStyle['img_margin']
        top_margin = notificationStyle['top_margin']
        pos = notificationStyle['location']
        height = notificationStyle['height']

        self._mutexUpdate = Lock()
        self._mutex = Lock()
        self._timeout_frames = math.floor(fps * settings['timeout_seconds'])
        self._transition_frames = math.floor(fps * settings['transition_seconds'])
        if 'max_n_notifications' in settings:
            max_stack = settings['max_n_notifications']
        else:
            max_stack = 1

        if pos == 'top':
            self._ofst = height
            self._init_pos = [0, 0]
        else:
            self._ofst = -height
            self._init_pos = [0, window.height() + self._ofst]
        self._size = [window.width(), height]

        # Notifications UI
        ### Create container (This is necessary in order to have z-order of each notification indipendent
        ### from the rest of ui elements
        container = QWidget(window)
        container.setGeometry(self._init_pos[0], self._init_pos[1], self._size[0], self._size[1] * max_stack)
        ### Create notifications
        for i in range(max_stack):
            self._free_notifications.append(
                Notification(container, stylesheet, img_margin, top_margin, self._init_pos, self._size, path)
        )

        # Steam
        if settings['steam']['enabled']:
            if 'ui_notify' in settings['steam']:
                self._steam_ui_notify = settings['steam']['ui_notify']
            else:
                self._steam_ui_notify = True
            if 'hyperion_effect' in settings['steam']:
                self._steam_hyperion_effect = settings['steam']['hyperion_effect']
            else:
                self._steam_hyperion_effect = False
            SteamNotifier().create(path)
            SteamNotifier().setupHooks(self.newNotification)
        else:
            self._steam_ui_notify = self._steam_hyperion_effect = False
        # Discord
        if settings['discord']['enabled']:
            if 'ui_notify' in settings['discord']:
                self._discord_ui_notify = settings['discord']['ui_notify']
            else:
                self._discord_ui_notify = True
            if 'hyperion_effect' in settings['discord']:
                self._discord_hyperion_effect = settings['discord']['hyperion_effect']
            else:
                self._discord_hyperion_effect = False
            DiscordNotifier().setupHooks(self.newNotification)
            if not DiscordNotifier().instantiated:
                DiscordNotifier().create(path)
                DiscordNotifier().run()
        else:
            self._discord_ui_notify = self._discord_hyperion_effect = False

    def update(self, status=None):
        self._mutexUpdate.acquire()
        # Process transitioner updates
        for item in self._live_queue:
            # Perform update if necessary
            if not item['transitioner'].isDone():
                item['notification'].moveY(item['transitioner'].update())
                item['notification'].update()

        # Process current live notifications
        i = 0
        while i < len(self._live_queue):
            item = self._live_queue[i]
            if item['stackPos'] != i and item['transitioner'].isDone():
                item['transitioner'] = Transitioner(
                    item['notification']._pos[1], self._transition_frames
                )
                item['transitioner'].transitionFromStart(-self._ofst, self._transition_frames)
                item['stackPos'] = i
                item['notification']._background.raise_()
            elif self._timer - item['timeOfCreation'] >= self._timeout_frames and item['stackPos'] == 0 and item['transitioner'].isDone():
                # Delete notification
                item['notification'].hide()
                self._free_notifications.append(self._live_queue.pop(0)['notification'])
                self._slot = self._slot - 1
                continue
            i = i + 1

        # Check if there are new notifications to display
        while len(self._queue) > 0 and len(self._free_notifications) > 0:
            slot = self._slot
            self._slot = self._slot + 1
            # Transition from the right side of the screen
            if slot > 0:
                startPosY = self._live_queue[len(self._live_queue) - 1]['notification']._pos[1]
                delta = self._ofst * slot - startPosY
            else:
                startPosY = self._init_pos[1] - self._ofst
                delta = self._ofst * (slot + 1)
            notification_t = Transitioner(startPosY, self._transition_frames)
            notification_t.transitionFromStart(delta, self._transition_frames)
            # Initialize notification
            self._mutex.acquire()
            data = self._queue.pop(0)
            self._mutex.release()
            notification = self._free_notifications.pop(0)
            notification.setText(data[0], data[1], data[2])
            notification.move(self._init_pos[0], startPosY)
            notification.update()
            notification.bringToBack()
            notification.show()
            # Add to live queue Notification, Notification Transitioner, position in stack, creation time
            self._live_queue.append({
                'notification': notification,
                'transitioner': notification_t,
                'stackPos': slot,
                'timeOfCreation': self._timer
            })
            # Hyperion Notification
            if Hyperion().ledState and Hyperion().notifications:
                if data[0] == 'Steam'  and self._steam_hyperion_effect != False:
                    Hyperion().setEffect(self._steam_hyperion_effect, 1, 0)
                elif data[0] == 'Discord' and self._discord_hyperion_effect != False:
                    Hyperion().setEffect(self._discord_hyperion_effect, 1, 0)

        self._timer = self._timer + 1
        self._mutexUpdate.release()

    def newNotification(self, app, title, message):
        self._mutex.acquire()
        self._queue.append([app, title, message])
        self._mutex.release()
