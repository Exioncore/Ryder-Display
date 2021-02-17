import os
import threading
import gevent
from steam.client import SteamClient
from steam.enums import EChatEntryType
from Network.Server import Server
from Network.Client import Client

class SteamNotifier(threading.Thread):
    def __init__(self, client:Client, server:Server, steam_notification, path):
        super(SteamNotifier, self).__init__(name='Steam Notifier Thread')

        self._cache = path + '/cache/'
        if not os.path.exists(self._cache):
            os.makedirs(self._cache)
       
        self._client = client
        self._steam_notification = steam_notification
        # Bind Server
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
        # Start Login Sequence
        self._steamClient.set_credential_location(self._cache)
        self._client.querySteamLogin()
        self._steam_notification('Steam', 'Login', 'Requesting Login Data')
        while True:
            gevent.sleep(0.25)

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

    def login_secured(self):
        print("Login secured")
        if self._steamClient.relogin_available:
            self._steamClient.relogin()

    def login_error(self, data):
        print("Login error")
        print(data)

    def auth_code_prompt(self, is2fa, code_mismatch):
        print("Steam2FA Required")
        self._steam_notification('Steam', 'Login', 'Requesting 2 Factor Authentication')
        self._client.querySteam2FA()

    def handle_message(self, msg):
        if msg.body.chat_entry_type == EChatEntryType.ChatMsg and not msg.body.local_echo:
            user = self._steamClient.get_user(msg.body.steamid_friend)
            text = msg.body.message
            self._steam_notification('Steam', user.name, text)

    def login_success(self):
        print("Login successfull")
        self._steam_notification('Steam', self._steamClient.username, 'Logged in!')