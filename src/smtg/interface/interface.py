"""
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
from smtg.daemon.comm.CommRouter import Routee 

class Interface(Routee):
    """ This is just so the internal references can handle interfaces as 
    Routees. 
    """
    def __init__(self, socket):
        """ Create an Interface using a socket. Assumes that it is of the
        type DaemonServerSocket.
        """
        self._socket = socket
        
    def _handle_msg(self, msg):
        """ Interfaces "handle the message" by sending it to the 
        interface on the other end of the socket.
        """
        self._socket.send(msg)