import gevent
from threading import Lock
from UIModules.Notifications.Notification import Notification
from Network.SteamNotifier import SteamNotifier
from Utils.Transitioner import Transitioner
from Network.Server import Server
from Network.Client import Client

class NotificationsHandler(object):
    _mutex : Lock
    _queue = []
    _timer = 0
    _onGoing = False
    
    def __init__(self,
                 window, client:Client, server:Server, timeout_frames, transition_frames, 
                 stylesheet=["","",""], img_margin = 5, pos='bottom', height=20, path=''
        ):
        self._mutex = Lock()
        self._transition_frames = transition_frames
        self._timeout_frames = timeout_frames

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
        self._steam = SteamNotifier(client, server, self.newNotification, path)
        gevent.spawn_later(2, self._steam.run)

        # Bind Server
        server.add_endpoint('/notification', 'notification', self._newNotification)

    def update(self, status=None):
        if not self._onGoing:
            if len(self._queue) > 0:
                self._mutex.acquire()
                entry = self._queue.pop(0)
                self._mutex.release()
                self._notification.setText(entry[0], entry[1], entry[2])
                self._notification.move(0, self._notification_t.start)
                self._notification_t.transitionFromStart(self._ofst, self._transition_frames)
                self._notification.show()
                self._onGoing = True

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
