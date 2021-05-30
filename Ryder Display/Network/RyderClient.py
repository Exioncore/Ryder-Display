import time
import json
import socket
import gevent
import threading

from Utils.Singleton import Singleton

class RyderClient(object, metaclass=Singleton):
    _s : socket.socket = None
    _endpoints = {}
    # Flag representing connection status
    connected = False
    # Flag to stop running client
    stop = False

    # Setup connection ip and port
    def setup(self, ip, port):
        self._ip = ip
        self._port = port

    # Clear all stored endpoints
    def clearEndPoints(self):
        self._endpoints = {}

    # Add endpoint trigger and function to call
    def addEndPoint(self, cmd: str, func):
        if cmd in self._endpoints:
            self._endpoints[cmd].append(func)
        else:
            self._endpoints[cmd] = []
            self._endpoints[cmd].append(func)

    # Send data to host (May fail if connection is not set)
    # Return True if transmission was succesfull, False otherwise
    def send(self, data:str):
        try:
            self._s.sendall((data+"\n").encode('utf-8'))
            return True
        except:
            print("Could not send: " + data)
            return False

    # Handle connection to host as well as automatic re-connection
    # Handle receival of data from host
    # Function is blocking and must run in its own thread or asynchronously from the main thread
    def run(self):
        data = ''
        last_update = -9999
        buff_size = 9
        step = 1
        self.connected = False
        self.stop = False
        
        while not self._stop:
            # Attempt connection to Ryder Engine
            try:
                print("Connecting to Ryder Engine...")
                if self._s is not None:
                    self._s.close()
                self._s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                self._s.settimeout(2.5)
                self._s.connect((self._ip, self._port))
                self._s.settimeout(2.5)
                # Setup Variables
                last_update = time.time()
                buff_size = 9
                step = 1
                self.connected= True
                # Call functions that are meant to run when connection is established
                if 'on_connect' in self._endpoints:
                    print("Endpoint: on_connect")
                    for endpoint in self._endpoints['on_connect']:
                        endpoint()
            except:
                pass
            
            # Loop to receive messages
            while not self._stop and self.connected:
                try:
                    data = self._s.recv(buff_size).decode('utf-8')
                    # Check if timeout occurred 
                    if len(data) == 0:
                        self.connected = False
                        break
                    else:
                        if step == 1:
                            # Retrieve size of upcoming message
                            buff_size = int(data)
                            step = 2
                        else:
                            # Process Message
                            msg = json.loads(data)
                            # Call appropriate endpoints
                            if msg[0] in self._endpoints:
                                print("Endpoint: " + msg[0])
                                for endpoint in self._endpoints[msg[0]]:
                                    endpoint(msg)
                            # Reset step
                            buff_size = 9
                            step = 1
                        last_update = time.time()       
                except:
                    self.connected = False
                gevent.sleep(0.025)
            gevent.sleep(0.025)
        # Close socket
        self._s.close()
        self.connected = False
