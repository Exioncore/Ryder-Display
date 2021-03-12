import os
import threading
import gevent
from steam.client import SteamClient
from steam.enums import EChatEntryType, EResult, EPersonaState
from Network.Server import Server
from Network.Client import Client

class SteamNotifier(object):
    def __init__(self, server:Server, notification, path):
        self._cache = path + '/cache/'
        if not os.path.exists(self._cache):
            os.makedirs(self._cache)
       
        self._notification = notification
        # Bind Server
        server._steam = self
        server.add_endpoint('/steamLogin', 'steamLogin', self._steamLoginData)
        server.add_endpoint('/steam2fa', 'steam2fa',self._steam2faData)   

    def run(self):
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
        # Start Login Sequence
        self._steamClient.set_credential_location(self._cache)
        if os.path.exists(self._cache + 'steam.txt'):
            f = open(self._cache + 'steam.txt', 'r')
            data = f.readlines()
            f.close()
            self._steamClient.login(username=data[0].replace('\n',''), login_key=data[1])
        else:
            Client().querySteamLogin()
            self._notification('Steam', 'Login', 'Requesting Login Data')

    def _steamLoginData(self, request):
        self._login_data = [request[0], request[1]]
        self._steamClient.login(username=self._login_data[0], password=self._login_data[1])
        print('Steam ' + request[0] + ' logging in')

    def _steam2faData(self, request):
        print("Steam 2FA: "+request)
        self._steamClient.login(two_factor_code=request, username=self._login_data[0], password=self._login_data[1])

    # Handle SteamClient events
    def connected(self):
        print("Connected")

    def disconnected(self):
        print("Disconnected")
        if self._steamClient.relogin_available:
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
            Client().querySteamLogin()
            self._notification('Steam', 'Login', 'Requesting Login Data')

    def auth_code_prompt(self, is2fa, code_mismatch):
        print("Steam2FA Required")
        self._notification('Steam', 'Login', 'Requesting 2 Factor Authentication')
        Client().querySteam2FA()

    def handle_message(self, msg):
        if msg.body.chat_entry_type == EChatEntryType.ChatMsg and not msg.body.local_echo:
            user = self._steamClient.get_user(msg.body.steamid_friend)
            text = msg.body.message
            self._notification('Steam', user.name, text)

    def login_success(self):
        print("Login successfull")
        self._steamClient.change_status({'persona_state': EPersonaState.Invisible})
        self._notification('Steam', self._steamClient.username, 'Logged in!')

    def new_login_key(self):
        print("New login key")
        f = open(self._cache + 'steam.txt', 'w')
        f.write(self._steamClient.username + '\n' + self._steamClient.login_key)
        f.close()
