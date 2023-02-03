# XELA Middleware Library
## Purpose
The general purpose of this library is to build middleware applications that are compatible with XELA Server software<br>
Available modules in the library:
* XELA Settings manager - object to simplify connection details for both the server and client modules
* XELA Client manager - object to handle connection to the XELA Server software or any other middleware servers
* XELA Server manager - object to handle a new server object to give access to modified or enhanced data to clients and other middleware clients
* threader module - to simplify creation of parallel processes
* Bit object - an object to work as boolean value in global namespace with options to turn on, off or toggle on the go

## Required libraries
The library requires following libraries to be installed via pip:
* websocket-client
* websockets

## Example code
```python
from xelamiddleware import Bit, XELA_Settings, XELA_Client, XELA_Server

#example data container, can be substituted with any function
class Data(object):
    def __init__(self):
        self.__data = {}
    def newdata(self,data):
        self.__data = data
    def getdata(self):
        return self.__data

incoming = Data()
outgoing = Data()

settings = XELA_Settings(client_ip="192.168.0.108", server_ip = "192.168.0.108", client_port= 5000, server_port=5002)

#Server will use the IP of the device as XELA_Server app does not run on localhost
settings.iamserver()
#pass in XELA_Settings object for IP and Port, second function must be the one which returns the dictionary to output 
server = XELA_Server(settings,outgoing.getdata)

#Client will use the IP of the device to be compatible with rest of the software
settings.iamclient()
#pass in XELA_Settings object for IP and Port, second function must be the one which handles incoming data (storage)
client = XELA_Client(settings,incoming.newdata)

while True:#your core method here to keep the app running. Once it ends, the program will close
    try:
        #simulating the data manipulation to make the example functioning
        outgoing.newdata(incoming.getdata())
        time.sleep(0.01)
    except KeyboardInterrupt:
        #break on KeyboardInterrupt
        break

#stop the client and server
client.close()
server.close()

#sleep for 5 seconds to ensure that both the server and client are closed
time.sleep(5)
sys.exit(0)

```

## To do
- [ ] make library packaged for installer
- [ ] make full documentation for the library

## Contributors
| Photo | Contributor | Relation |
|:---:|:---:|:---:|
| [<img src="https://github.com/mcsix.png" width="40">](https://github.com/mcsix) | [@mcsix](https://github.com/mcsix) | XELA Software Engineer |