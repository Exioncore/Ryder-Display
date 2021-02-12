import socket
from flask import Flask, Response, request
from gevent.pywsgi import WSGIServer

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

    def run(self, port=9520):
        http_server = WSGIServer(('0.0.0.0', port), self.app)
        http_server.serve_forever()

    def add_endpoint(self, endpoint=None, endpoint_name=None, handler=None):
        self.app.add_url_rule(endpoint, endpoint_name, EndpointAction(handler), methods=['POST'])
