import os
import gevent
import asyncio
import discord

from Utils.Singleton import Singleton
from Network.RyderClient import RyderClient

class DiscordNotifier(discord.Client, metaclass=Singleton):
    _instantiated = False
    _running = False
    _notification = None

    def create(self, path):
        if not self._instantiated:
            self._instantiated = True
            self._cache = path + '/cache/'
            if not os.path.exists(self._cache):
                os.makedirs(self._cache)
            # Discord Client
            intents = discord.Intents.none()
            discord.Client.__init__(self, intents=intents)
            # Bind EndPoints
            RyderClient().addEndPoint('on_connect', self._run)
            RyderClient().addEndPoint('discordLogin', self._discordLoginData)
       
    def setupNotificationHandlerHook(self, notification):
        self._notification = notification

    def _run(self):
        # Start Login Sequence
        if not self._running:
            self._running = True
            self.loop.create_task(self._loop())
            if os.path.exists(self._cache + 'discord.txt'):
                f = open(self._cache + 'discord.txt', 'r')
                data = f.readlines()
                f.close()
                gevent.spawn_later(2, discord.Client.run, self, data[0])
            else:
                if self._notification != None:
                    self._notification('Discord', 'Login', 'Requesting Login Data')
                RyderClient().send("[\"discordLogin\"]")

    async def _loop(self):
        try:
            while True:
                # Process UI events
                gevent.sleep(0.25)
                # Process Discord Events
                await asyncio.sleep(0.001)
        except:
            return

    def _discordLoginData(self, data):
        f = open(self._cache + 'discord.txt', 'w')
        f.write(data[1])
        f.close()
        gevent.spawn(discord.Client.run, self, data[1])

    async def on_ready(self):
        if self._notification != None:
            self._notification('Discord', self.user.name, "Logged in")

    async def on_message(self, message):
        if message.author == self.user:
            return
        if self._notification != None:
            self._notification('Discord', message.author.name, message.content)
