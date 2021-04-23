import time
import json
import socket
import gevent
import threading
from Utils.Singleton import Singleton

class RyderClient(object, metaclass=Singleton):
    _s : socket.socket = None
    _endpoints = {}

    def setup(self, ip, port):
        # Save data
        self._ip = ip
        self._port = port

    def addEndPoint(self, cmd: str, func):
        if cmd in self._endpoints:
            self._endpoints[cmd].append(func)
        else:
            self._endpoints[cmd] = []
            self._endpoints[cmd].append(func)

    def send(self, data:str):
        try:
            self._s.sendall((data+"\n").encode('utf-8'))
            return True
        except:
            print("Ryder Engine not connected")
            return False

    def run(self):
        data = ''
        last_update = -9999
        self._stop = False
        while not self._stop:
            # Attempt reconnection to Ryder Engine after 10 seconds of no data
            if time.time() - last_update >= 10:
                try:
                    print("Attempt Ryder Engine connection")
                    if self._s is not None:
                        self._s.close()
                    self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    self._s.connect((self._ip, self._port))
                    self._s.settimeout(0.001)
                    # Call functions that are meant to run when connection is established
                    if 'on_connect' in self._endpoints:
                        print("Endpoint: on_connect")
                        for endpoint in self._endpoints['on_connect']:
                            endpoint()
                except:
                    pass
                last_update = time.time()
                data = ''
                last_data_size = 0
            # Loop to receive messages
            while not self._s._closed or not self._stop:
                try:
                    data += self._s.recv(2056).decode("utf-8") 
                    # Check for inactivity timeout
                    if last_data_size == len(data) and time.time() - last_update >= 10:
                        break
                    else:
                        last_update = time.time()
                    # Process data
                    index = data.find('\n')
                    if index != -1:
                        # Get Message
                        msg = json.loads(data[0:index])
                        # Call appropriate endpoints
                        if msg[0] in self._endpoints:
                            print("Endpoint: " + msg[0])
                            for endpoint in self._endpoints[msg[0]]:
                                endpoint(msg)
                        # Flush the read message from the buffer
                        data = data[index+1:]
                    last_data_size = len(data)
                except:
                    if time.time() - last_update >= 10:
                        break
            gevent.sleep(0.01)
