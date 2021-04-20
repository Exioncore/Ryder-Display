import time
import socket
import gevent
import asyncio
from gevent.pool import Pool
from gevent.pywsgi import WSGIServer
from flask import Flask, Response, request

class EndpointAction(object):
    def __init__(self, action):
        self.action = action
        self.response = Response(status=200, headers={})

    def __call__(self, *args):
        self.action(request.get_json())
        return self.response

class Server(object):
    def __init__(self, name):
        self.app = Flask(name)
        self._steam = None
        self._discord = None

    def run(self, port=9520):
        print("Server started")
        if self._steam is not None:
           gevent.spawn(self._steam.run)
        if self._discord is not None:
           gevent.spawn(self._discord.run)

        WSGIServer(('0.0.0.0', port), self.app).serve_forever()

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        print("Endpoint \"" + endpoint_name + "\" added")
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=['POST'])
