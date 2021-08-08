import os
import gevent
import threading
from steam.client import SteamClient
from steam.enums import EChatEntryType, EResult, EPersonaState

from Utils.Singleton import Singleton
from Network.RyderClient import RyderClient

class SteamNotifier(object, metaclass=Singleton):
    _instantiated = False
    _running = False
    _notification = None

    def create(self, path):
        if not self._instantiated:
            self._instantiated = True
            self._cache = path + '/cache/'
            if not os.path.exists(self._cache):
                os.makedirs(self._cache)
            # Steam Client
            self._steamClient = SteamClient()
            # Hook Steam Client Events
            self._steamClient.on(SteamClient.EVENT_AUTH_CODE_REQUIRED, self.auth_code_prompt)
            self._steamClient.on("FriendMessagesClient.IncomingMessage#1", self.handle_message)
            self._steamClient.on(SteamClient.EVENT_LOGGED_ON, self.login_success)
            self._steamClient.on(SteamClient.EVENT_CHANNEL_SECURED, self.login_secured)
            self._steamClient.on(SteamClient.EVENT_ERROR, self.login_error)
            self._steamClient.on(SteamClient.EVENT_CONNECTED, self.connected)
            self._steamClient.on(SteamClient.EVENT_DISCONNECTED, self.disconnected)
            self._steamClient.on(SteamClient.EVENT_NEW_LOGIN_KEY, self.new_login_key)
            # Bind EndPoints
            RyderClient().addEndPoint('on_connect', self._run)
            RyderClient().addEndPoint('steamLogin', self._steamLoginData)
            RyderClient().addEndPoint('steam2fa',self._steam2faData)

    def setupNotificationHandlerHook(self, notification):
        self._notification = notification

    def _run(self):
        # Start Login Sequence
        if not self._running:
            self._running = True
            self._steamClient.set_credential_location(self._cache)
            if os.path.exists(self._cache + 'steam.txt'):
                f = open(self._cache + 'steam.txt', 'r')
                data = f.readlines()
                f.close()
                gevent.spawn_later(2, SteamClient.login, self._steamClient, username=data[0].replace('\n',''), login_key=data[1])
            else:
                if self._notification != None:
                    self._notification('Steam', 'Login', 'Requesting Login Data')
                RyderClient().send("[\"steamLogin\"]")

    def _steamLoginData(self, data):
        print('Steam login data received')
        self._login_data = [data[1], data[2]]
        self._steamClient.login(username=self._login_data[0], password=self._login_data[1])

    def _steam2faData(self, data):
        print("Steam 2FA data received")
        self._steamClient.login(two_factor_code=data[1], username=self._login_data[0], password=self._login_data[1])

    # Handle SteamClient events
    def connected(self):
        print("Connected")

    def disconnected(self):
        print("Disconnected")
        if self._steamClient.relogin_available:
            if self._notification != None:
                self._notification('Steam', self._steamClient.username, 'Connection lost! Re-trying...')
            self._steamClient.reconnect(maxdelay=30)

    def login_secured(self):
        print("Login secured")
        if self._steamClient.relogin_available:
            self._steamClient.relogin()

    def login_error(self, data):
        print("Login error")
        print(data)
        if data == EResult.InvalidPassword:
            if self._notification != None:
                self._notification('Steam', 'Login', 'Requesting Login Data')
            RyderClient().send("[\"steamLogin\"]")

    def auth_code_prompt(self, is2fa, code_mismatch):
        print("Steam2FA Required")
        if self._notification != None:
            self._notification('Steam', 'Login', 'Requesting 2 Factor Authentication')
        RyderClient().send("[\"steam2fa\"]")

    def handle_message(self, msg):
        if msg.body.chat_entry_type == EChatEntryType.ChatMsg and not msg.body.local_echo:
            user = self._steamClient.get_user(msg.body.steamid_friend)
            text = msg.body.message
            if self._notification != None:
                self._notification('Steam', user.name, text)

    def login_success(self):
        print("Login successfull")
        self._steamClient.change_status(persona_state = EPersonaState.Invisible)
        if self._notification != None:
            self._notification('Steam', self._steamClient.username, 'Logged in!')

    def new_login_key(self):
        print("New login key")
        f = open(self._cache + 'steam.txt', 'w')
        f.write(self._steamClient.username + '\n' + self._steamClient.login_key)
        f.close()
