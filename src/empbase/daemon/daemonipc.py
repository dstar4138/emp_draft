__copyright__ = """
Copyright (c) 2010-2011 Alexander Dean (dstar@csh.rit.edu)
Licensed under the Apache License, Version 2.0 (the "License"); 
you may not use this file except in compliance with the License. 
You may obtain a copy of the License at 

http://www.apache.org/licenses/LICENSE-2.0 

Unless required by applicable law or agreed to in writing, software 
distributed under the License is distributed on an "AS IS" BASIS, 
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and 
limitations under the License. 
"""

#
# The Daemon Socket classes are used to connect to a running daemon 
# server with a TCP socket. Everything is non-specialized for SNTG.
# So have some fun with daemons in your own projects.
#
__version__ = "0.7"

from socket import timeout # Imported so others don't have to. 
from socket import socket, AF_INET, SOCK_STREAM, SOL_SOCKET, SO_REUSEADDR, SHUT_RDWR

class DaemonSocketError(Exception):
    """A Daemon Socket Error is an issue caused from issues within the 
    socket connection process. These can arise from either side of the
    connection. This error is not a shell for normal socket errors, but
    for errors caused elsewhere in the process.
        
    Attributes:
        msg  --  the message for the socket error
    """
    def __init__(self, msg):
        self.msg = msg
    def __str__(self):
        return repr(self.msg)



class DaemonServerSocket():
    """A DaemonServerSocket is a welcome socket for a daemon. It can be used
    for both inter-process communication and for normal TCP connections as 
    with normal python ServerSockets. The primary difference is that the daemon
    uses a whitelist to know who to allow to accept. It also automatically
    filters connections from anyone other than the local system (this can be
    turned off of course).
    """

    def __init__(self, port=8080, bufferSize=4096, encoding="utf-8", 
                 altsocket=None, ip_whitelist=[], externalBlock=True, 
                 allowAll=False):
        """ Sets up an internal socket on the server side and auto binds to 
        the given port number.
        """
        self.BUFFER_SIZE = bufferSize
        self.PORT_NUM = port
        self.ENCODING = encoding
        self.WHITE_LIST = ip_whitelist
        self.LOCAL_ONLY = externalBlock
        self.ALLOW_ALL = allowAll
        if altsocket == None:
            self.socket = socket(AF_INET,SOCK_STREAM)
            self.socket.setsockopt(SOL_SOCKET, SO_REUSEADDR, 1)
            self.socket.bind(("localhost",self.PORT_NUM))
            self.socket.listen(3) # standard, change if you want.
            self.socket.settimeout(2) #timeout in 3 seconds...
        else: 
            self.socket = altsocket
        
    def __getattr__(self, name):    
        return getattr(self.socket, name)
        
    def send(self, msg):
        """Sends a string as a byte sequence to a DaemonClientSocket at the
        other end. This acts as a socket.sendall(msg), so there is no worries
        about network buffers or the accidental buffer-overflow.
        """
        try:
            self.socket.sendall(str(msg).encode(self.ENCODING))
        except AttributeError:
            raise TypeError("Parameter given is not a string.")
        except:
            raise DaemonSocketError("There was and issue sending the message.")
        
        
    def recv(self):
        """Receives a string as a byte sequence from a DaemonClientSocket at
        the other end. Commands sent to the DaemonServerSocket can't be more 
        than 4096 bytes at a time. If your conversation needs more than that, 
        create a method for the server to recognize it or change the 
        buffer size if you NEED it. Highly un-recommended.
        """
        msg = b''
        try:
            msg = self.socket.recv(self.BUFFER_SIZE)
        except:pass
        finally:
            return msg.decode(self.ENCODING)
    
    def rebind(self, newPortNum):
        """Rebinds the DaemonServerSocket to a new port number. """
        self.socket.bind(("localhost",newPortNum))
        self.PORT_NUM = newPortNum
    
    def close(self):
        """Closes a current connection, does not un-bind the DaemonServerSocket.
        If a connection is closed, there is not getting it back.
        """
        self.socket.close()

   
    def accept(self):
        """Returns a new connected DaemonServerSocket for communication with a 
        local or white-listed client. If there is a connecting client that is 
        not local, it will either force close the connection or (if user-set) 
        accept it anyways.
        """
        possible_addrs = ['127.0.0.1', 'localhost']
        
        if not self.LOCAL_ONLY:
            possible_addrs += self.WHITE_LIST
        
        while True:
            client_socket, (addr, p) = self.socket.accept()
            
            if self.ALLOW_ALL or addr in possible_addrs:
                return DaemonServerSocket(port=p, 
                                          bufferSize=self.BUFFER_SIZE,
                                          encoding=self.ENCODING,
                                          altsocket=client_socket)
            # otherwise close
            self.socket.close()
            
    def shutdown(self):
        self.socket.shutdown(SHUT_RDWR)
   
        
class DaemonClientSocket():
    """A simple socket for connecting to a DaemonServerSocket. There is nothing
    special here except that it regulates the encoding and decoding of the 
    sent/recv messages for you.
    """
    def __init__(self, port=8080, bufferSize=1024, encoding="utf-8"):
        """ This is the socket for the Client connection. Make sure the server
        socket has the same port number and encoding that the client has.
        """
        self.BUFFER_SIZE = bufferSize
        self.PORT_NUM = port
        self.ENCODING = encoding
        self.RECV_LIMIT = 5 #DO NOT CHANGE!!
        self.socket = socket(AF_INET,SOCK_STREAM)
        self.socket.settimeout(0.5)#intentionally very low. DO NOT CHANGE!!
        
    def __getattr__(self, name):    
        return getattr(self.socket, name)
        
    def connect(self):
        """Connects to a currently running daemon on the local system. Make sure
        the daemon is utilizing a DaemonServerSocket and is the same encoding that
        you are using.
        """
        self.socket.connect(("localhost",self.PORT_NUM))
        
    def send(self,msg):
        """Sends a string as a byte sequence to a DaemonServerSocekt at the 
        other end. This essentially acts as a socket.sendall(msg), but if the 
        message is larger than the buffer-size it will throw an error. 
        """
        msg = str(msg)
        if len(msg) > self.BUFFER_SIZE:
            raise DaemonSocketError("Message given is larger than buffer size!")
        
        try:
            self.socket.sendall(msg.encode(self.ENCODING))
            
        except AttributeError:
            raise TypeError("Parameter given is not a string.")
        except Exception as e:
            raise DaemonSocketError(e)    
        
    def _recv(self):
        """Receives a string as a byte sequence from a DaemonServerSocket at
        the other end. This acts like a loop receiving everything in the network
        buffer before returning. To protect from buffer overflow it has a set
        max limit to the number of receives, but its high enough that it wont 
        matter for most projects.
        """
        msg = b''
        try:
            count = 0
            while count < self.RECV_LIMIT:
                data = self.socket.recv(self.BUFFER_SIZE)
                
                if not data: break
                msg += data
                count+=1
        except: pass        
        finally:
            return msg.decode(self.ENCODING)
        
    def recv(self, block=True,blockout=10):
        """"""
        if not block:
            return self._recv()
        else:
            count=0
            msg = ""
            while count<blockout:
                msg = self._recv()
                if not msg:
                    count+=1
                    continue
                else:break
            return msg
    
    def close(self):
        """Closes the current connection with the Daemon."""
        self.socket.close()
                
