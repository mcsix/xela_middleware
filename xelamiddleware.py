#!/usr/bin/env python3.8
#import grpc
import time
import websocket
import websockets
import asyncio
import json
import threading
import importlib

#console printing related
import subprocess
subprocess.call('', shell=True)

""""
XELA Middleware Library

Contains
--------

* threader - for threading operations
* Bit - for boolean operations
* XELA_Settings - for settings management
* XELA_Server - for server functionality
* XELA_Client - for client functionality
"""



websocket.setdefaulttimeout(1) #you should avoid increasing it.
#set up argument parser
def threader(target, args=False, **targs):
    """
    Threader

    Usage
    -----
    >>> my_thread = threader(my_function,name="My Special Function")

    Parameters
    ----------
    
    * target - function to run in a thread
    * name - Name for the thread (optional)
    """
    if args:
        targs["args"]=(args,)
    thr = threading.Thread(target=target, **targs, daemon=True)
    thr.start()
    return thr
class Bit(object):
    """
    Bit object with global usage and toggle functionality

    Usage
    -----
    >>> my_bit = Bit(True)
    >>> my_bit.toggle()
    >>> if my_bit:
    ...     print("Bit is True")
    >>> else:
    ...     print("Bit is False")
    Bit is False

    Parameters
    ----------
    
    * value - value to set it to, default is False (optional)
    """
    def __init__(self,value:bool=False) -> None:
        self.__value = value
    def toggle(self) -> None:
        self.__value = not self.__value
    def on(self) -> None:
        self.__value = True
    def off(self) -> None:
        self.__value = False
    def __bool__(self) -> bool:
        return self.__value

class XELA_Settings(object):
    """
    XELA Settings container

    Usage
    -----
    >>> settings = XELA_Settings()
    >>> settings.iamserver()
    >>> server = XELA_Server(settings) #to send to XELA_Server:

    Parameters
    ----------
    
    * client_ip - Client IP, if not localhost (127.0.0.1) or not self via iamclient() method (optional)
    * server_ip - Server IP, if not localhost (127.0.0.1) or not self via iamserver() method (optional)
    * client_port - Client port, if not 5000 (optional)
    * server_port - Server port, if not 5001 (optional)
    """
    def __init__(self, client_ip="127.0.0.1", server_ip="127.0.0.1", client_port=5000, server_port=5001):
        self.__client_ip = client_ip
        self.__server_ip = server_ip
        self.__client_port = client_port
        self.__server_port = server_port
    def get_client(self):
        return (self.__client_ip,self.__client_port)
    def get_server(self):
        return (self.__server_ip,self.__server_port)
    def __get_ip(self, setIP=None):
        socket = importlib.import_module("socket")
        s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try:
            s.connect(('1.2.3.4', 1))
            IP = s.getsockname()
        except Exception:
            IP = ['127.0.0.1']
        finally:
            s.close()
        return IP[0]
    def iamclient(self):
        self.__client_ip = self.__get_ip()
    def iamserver(self):
        self.__server_ip = self.__get_ip()

class XELA_Server(object):
    """
    Main Server System

    Usage
    -----
    >>> def my_datafunction():
    ...     return {"data": "something"}
    >>> settings = XELA_Settings()
    >>> XELA_Server(settings,my_datafunction)

    Parameters
    ----------
    
    * settings - XELA_Settings object containing IP and port settings (optional)
    * runfunction - function to run to get data for broadcasting (optional)
    * printer - function to print errors if they occur, default is Python print() (optional)
    """
    def __init__(self, settings=None,datafunction=None,printer=print):
        self.printer = printer
        self.settings = settings if settings is not None else XELA_Settings()
        self.data = datafunction if datafunction is not None else self.emptyfunc
        self.main()
    def emptyfunc(self):
        return {}
    def close(self):
        try:
            self.loop.stop()
            self.loop.stop()
            self.loop.close()
        except Exception:
            pass
    def getID(self,data):
        try:
            if isinstance(data,dict):
                return data["Sec-WebSocket-Accept"].strip()
            else:
                for i in data:
                    x = list(i)
                    a,b = x[0],x[1]
                    if "Sec-WebSocket-Accept" in a:
                        return b.strip()
        except Exception:
            pass
        return "No ID"
    async def connection(self, websocket, path):
        wsname = self.getID(websocket.response_headers.raw_items())
        self.printer("\033[32m{}\033[0m connected".format(wsname))
        try:
            while int(websocket.state) == 1:
                await websocket.send(json.dumps(self.data()))
                await asyncio.sleep(0.0005)
        except Exception as e:
            self.printer("EXP: {}: {}".format(type(e).__name__,e))
        finally:
            self.printer("\033[31m{}\033[0m disconnected".format(wsname))
    def server_loop(self):
        self.printer("Server started")
        self.loop.run_until_complete(self.server)
        self.printer("Server midpoint")
        self.loop.run_forever()

        self.printer("Server ended")
    def main(self):
        self.loop = asyncio.new_event_loop()
        asyncio.set_event_loop(self.loop)
        self.server = websockets.serve(self.connection, *self.settings.get_server())
        threader(self.server_loop,name="Server_Thread")

class XELA_Client(object):
    """
    Main Client System

    Usage
    -----
    >>> def my_func():
    ...     #do something
    ...     pass
    >>> settings = XELA_Settings()
    >>> XELA_Client(settings,my_func)

    Parameters
    ----------

    * settings - XELA_Settings object containing IP and port settings (optional)
    * runfunction - function to run when data is received (optional)
    * printer - function to print errors if they occur, default is Python print() (optional)
    * runner - Bit object stating if rest of the program is still running (optional)
    * errordata - object to use if connection is lost for getData() method, default is {"message": "error","data": []} (optional)
    """
    def __init__(self, settings=None,runfunction=None,printer=print,runner=None,errordata=None):
        self.printer = printer
        self.settings = settings if settings is not None else XELA_Settings()
        self.runfunc = runfunction if runfunction is not None else self.emptyfunc
        self.__data = {}
        if isinstance(runner,Bit):
            self.running = runner
        else:
            self.running = Bit(True)
        if errordata is not None:
            self.onerror = errordata
        else:
            self.onerror = {"message": "error","data": []}
        self.main()
    def emptyfunc(self,data):
        _ = data
    def on_message(self,wsapp, message):
        try:
            data = json.loads(message)
        except Exception:
            pass
        else:
            try:
                if data["message"] == "Welcome":
                    self.printer(data)
                else:
                    self.__data = data
                    self.runfunc(data)
            except Exception:
                pass
    def getData(self):
        return self.__data
    def send(self,data):
        try:
            self.client.send(json.dumps(data))
        except Exception:
            pass
    def close(self):
        self.printer("Trying to close Client")
        try:
            self.client.close()
        except Exception:
            pass
    def looper(self):
        while self.running:
            self.printer("Starting connection on {}:{}".format(*self.settings.get_client()))
            self.client.run_forever() #Run until connection dies
            self.__data = self.onerror.copy()
            time.sleep(2) #wait 2 seconds before trying again
    def main(self):
        try:
            self.client = websocket.WebSocketApp("ws://{}:{}".format(*self.settings.get_client()), on_message=self.on_message)
        except Exception:
            pass
        self.client_thread = threader(self.looper,name="Client_Thread")

 