import os
import gevent
import asyncio
import discord

from Utils.Singleton import Singleton
from Network.RyderClient import RyderClient

class DiscordNotifier(discord.Client, metaclass=Singleton):
    instantiated = False

    def create(self, path):
        self._cache = path + '/cache/'
        if not os.path.exists(self._cache):
            os.makedirs(self._cache)
        # Discord Client
        intents = discord.Intents.none()
        discord.Client.__init__(self, intents=intents)
        # Done
        self.instantiated = True
       
    def setupHooks(self, notification):
        self._notification = notification
        # Bind EndPoints
        RyderClient().addEndPoint('discordLogin', self._discordLoginData)

    def run(self):
        self.loop.create_task(self._loop())
        if os.path.exists(self._cache + 'discord.txt'):
            f = open(self._cache + 'discord.txt', 'r')
            data = f.readlines()
            f.close()
            gevent.spawn(discord.Client.run, self, data[0], bot = False)
        else:
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
        print('Discord login data received')
        f = open(self._cache + 'discord.txt', 'w')
        f.write(data[1])
        f.close()
        gevent.spawn(discord.Client.run, self, data[1], bot = False)

    async def on_ready(self):
        self._notification('Discord', self.user.name, "Logged in")

    async def on_message(self, message):
        if message.author == self.user:
            return
        print("Discord Message (From: "+message.author.name+", Text: "+message.content+")")
        self._notification('Discord', message.author.name, message.content)
