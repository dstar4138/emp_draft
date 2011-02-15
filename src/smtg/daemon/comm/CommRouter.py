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

class Routee():
    """ Base object for every internal possibility for communication 
    Within SMTG,"""
    def __init__(self, name, commrouter):
        """ Create the Routee object and register it with a Router."""
        self.msg_handler = commrouter
        self.ID = self.msg_handler.register(name, self)
        
    def _handle_msg(self, msg):
        """Called by the router, this is what handles the message
        directed at this object.
        """
        raise NotImplementedError("_handle_msg() not implemented")
        

class CommRouter():
    """The CommRouter internally handles inter-thread communication and
    message passing. SMTG uses this to handle incoming Interface and Plug-in
    messages and route them to the right Plug-in, Interface, Alert, or internal
    handler. 
    
    In order to utilize the router, the objects must be registered and an id 
    must be given to it. This id must be used as the source/destination in the
    Message.
    """
    def __init__(self):
        pass
    
    def register(self, name, ref):
        """ Registers you with the router, and any messages that are directed
        at you must"""
        pass
    
    def isRegisteredByID(self, id):
        pass
    
    def isRegisteredByName(self, name):
        pass
    