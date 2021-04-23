import os
import discord
import asyncio
import gevent
from threading import Thread
from Network.RyderClient import RyderClient

class DiscordNotifier(discord.Client):
    """description of class"""
    def __init__(self, notification, path):
        discord.Client.__init__(self)
        self._cache = path + '/cache/'
        if not os.path.exists(self._cache):
            os.makedirs(self._cache)
       
        self._notification = notification
        # Bind Server
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
        print("Message")
        if message.author == self.user:
            return
        self._notification('Discord', message.author.name, message.content)
