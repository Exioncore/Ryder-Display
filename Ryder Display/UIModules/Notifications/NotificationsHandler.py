import gevent
from threading import Lock
from UIModules.Notifications.Notification import Notification
from Network.SteamNotifier import SteamNotifier
from Network.DiscordNotifier import DiscordNotifier
from Utils.Transitioner import Transitioner
from Network.Server import Server
from Network.Client import Client
from Network.Hyperion import Hyperion

class NotificationsHandler(object):
    _mutex : Lock
    _queue = []
    _timer = 0
    _onGoing = False
    
    def __init__(self,
                 window, server:Server, fps, settings,
                 stylesheet=["","",""], img_margin = 5, pos='bottom', height=20, path='',
        ):
        self._mutex = Lock()
        self._transition_frames = fps * settings['transition_seconds']
        self._timeout_frames = fps * settings['timeout_seconds']

        if pos == 'top':
            pos = [0, -height]
            self._ofst = height
        else:
            pos = [0, window.height()]
            self._ofst = -height
        size = [window.width(), height]

        # Notification UI
        self._notification_t = Transitioner(pos[1], self._transition_frames)
        self._notification = Notification(window, stylesheet, img_margin, pos, size, path)

        # Steam
        if settings['steam']['enabled']:
            self._steam = SteamNotifier(server, self.newNotification, path)
            if 'ui_notify' in settings['steam']:
                self._steam_ui_notify = settings['steam']['ui_notify']
            else:
                self._steam_ui_notify = True
            if 'hyperion_effect' in settings['steam']:
                self._steam_hyperion_effect = settings['steam']['hyperion_effect']
            else:
                self._steam_hyperion_effect = False
        else:
            self._steam_ui_notify = self._steam_hyperion_effect = False
        # Discord
        if settings['discord']['enabled']:
            self._discord = DiscordNotifier(server, self.newNotification, path)
            if 'ui_notify' in settings['discord']:
                self._discord_ui_notify = settings['discord']['ui_notify']
            else:
                self._discord_ui_notify = True
            if 'hyperion_effect' in settings['discord']:
                self._discord_hyperion_effect = settings['discord']['hyperion_effect']
            else:
                self._discord_hyperion_effect = False
        else:
            self._discord_ui_notify = self._discord_hyperion_effect = False

        # Bind Server
        server.add_endpoint('/notification', 'notification', self._newNotification)

    def update(self, status=None):
        # No notifications going thus check for new ones to display
        if not self._onGoing:
            if len(self._queue) > 0:
                self._mutex.acquire()
                entry = self._queue.pop(0)
                self._mutex.release()
                # UI Notification
                if ((entry[0] == 'Steam' and self._steam_ui_notify) or
                    (entry[0] == 'Discord' and self._discord_ui_notify)):
                    self._notification.setText(entry[0], entry[1], entry[2])
                    self._notification.move(0, self._notification_t.start)
                    self._notification_t.transitionFromStart(self._ofst, self._transition_frames)
                    self._notification.show()
                # Hyperion Notification
                if Hyperion().ledState and Hyperion().notifications:
                    if entry[0] == 'Steam'  and self._steam_hyperion_effect != False:
                        Hyperion().setEffect(self._steam_hyperion_effect, 1, 0)
                    elif entry[0] == 'Discord' and self._discord_hyperion_effect != False:
                        Hyperion().setEffect(self._discord_hyperion_effect, 1, 0)
                self._onGoing = True
        # Timer Handling
        if self._onGoing:
            if not self._notification_t.isDone():
                self._notification.move(0, self._notification_t.update())
                self._notification.update()
            else:
                self._timer += 1
            if self._timer >= self._timeout_frames:
                self._notification.hide()
                self._timer = 0
                self._onGoing = False
                self.update()

    def newNotification(self, app, title, message):
        self._mutex.acquire()
        self._queue.append([app, title, message])
        self._mutex.release()
        if not self._onGoing:
            self.update()

    def _newNotification(self, request):
        self._mutex.acquire()
        self._queue.append([request['app'], request['title'], request['message']])
        self._mutex.release()
        if not self._onGoing:
            self.update()
