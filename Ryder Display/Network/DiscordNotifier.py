import os
import discord
import asyncio
import gevent
from threading import Thread
from Network.Server import Server
from Network.Client import Client

class DiscordNotifier(discord.Client):
    """description of class"""
    def __init__(self, server:Server, notification, path):
        discord.Client.__init__(self)
        self._cache = path + '/cache/'
        if not os.path.exists(self._cache):
            os.makedirs(self._cache)
       
        self._notification = notification
        # Bind Server
        server._discord = self
        server.add_endpoint('/discordLogin', 'discordLogin', self._discordLoginData)

    def run(self):
        self.loop.create_task(self._loop())
        if os.path.exists(self._cache + 'discord.txt'):
            f = open(self._cache + 'discord.txt', 'r')
            data = f.readlines()
            f.close()
            gevent.spawn(discord.Client.run, self, data[0], bot = False)
        else:
            Client().queryDiscordLogin()
            self._notification('Discord', 'Login', 'Requesting Login Data')

    async def _loop(self):
        try:
            while True:
                # Process UI events
                gevent.sleep(0.25)
                # Process Discord Events
                await asyncio.sleep(0.001)
        except:
            return

    def _discordLoginData(self, request):
        login_data = request[0]
        f = open(self._cache + 'discord.txt', 'w')
        f.write(self._login_data)
        f.close()
        gevent.spawn(discord.Client.run, self, login_data, bot = False)

    async def on_ready(self):
        self._notification('Discord', self.user.name, "Logged in")

    async def on_message(self, message):
        print("Message")
        if message.author == self.user:
            return
        self._notification('Discord', message.author.name, message.content)
