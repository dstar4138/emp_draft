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
import time
import queue
import random
import logging
from threading import Thread
from smtg.daemon.comm.messages import strToMessage, ALERT_MSG_TYPE

class Routee():
    """ Base object for every internal possibility for communication 
    Within SMTG,"""
    def __init__(self, commrouter, name="blank"):#FIXME: find another way of getting name? Do we even need it?
        """ Create the Routee object and register it with a Router."""
        self.msg_handler = commrouter
        self.ID = self.msg_handler.register(name, self)
        
    def _handle_msg(self, msg):
        """Called by the router, this is what handles the message directed at 
        this object. WARNING: This method should be thread safe, since its 
        pushed to a new one upon getting called.
        """
        raise NotImplementedError("_handle_msg() not implemented")
        
class Interface(Routee):
    """ This is just so the internal references can handle interfaces as 
    Routees. 
    """
    def __init__(self, commrouter, socket):
        """ Create an Interface using a socket. Assumes that it is of the
        type DaemonServerSocket.
        """
        Routee.__init__(self, commrouter)
        self._socket = socket
        self.kill=False
        
    def _handle_msg(self, msg):
        """ Interfaces "handle the message" by sending it to the 
        interface on the other end of the socket.
        """
        self._socket.send(msg)
        if self.kill:
            self.msg_handler.deregister(self.ID)
            self.close()
        
    def _run(self):
        """ Runs the receiving portion of the interface. """
        logging.debug("starting interface comm")
        #self._socket.setblocking(True)
        try:
            while 1:
                msg = self._socket.recv()
                if not msg: break
                else:
                    tmp=strToMessage(msg)
                    self.kill=tmp.get("kill",False)
                    self.msg_handler.sendMsg(tmp)
        except Exception as e: 
            logging.error("interface died because: %s"%e)
        finally:
            logging.debug("ending interface comm")
            self.msg_handler.deregister(self.ID)
            
    def close(self):
        """ Closes the communication to the Interface. """
        self._socket.close()


class CommRouter():# FIXME: make into a singleton? it would make the need for all the references go away...
    """The CommRouter internally handles inter-thread communication and
    message passing. SMTG uses this to handle incoming Interface and Plug-in
    messages and route them to the right Plug-in, Interface, Alert, or internal
    handler. 
    
    In order to utilize the router, the objects must be registered and an id 
    must be given to it. This id must be used as the source/destination in the
    Message.
    """
    def __init__(self):
        """ Create the internal thread-safe queue object for holding messages! """
        self._msg_queue = queue.Queue()
        self._registration = {}
        
    def register(self, name, ref):
        """ Registers you with the router, and any messages that are directed
        at you will be forwarded to you. You MUST be of the type Routee. """
        if name is "daemon": self._daemon=ref
        while 1:
            id = "%s" % str(random.random())[2:12]
            if id in list(self._registration.keys()): 
                continue
            else:
                self._registration[id] = (name,ref)
                return id
        
        
    
    def isRegisteredByID(self, id):
        """ Checks if the id is registered in the Router, returns a boolean."""
        return (id in list(self._registration.keys()))
            
    
    def isRegisteredByName(self, name): #remove?
        """ Checks if the name is registered, returns the id or False if otherwise 
        not registered.
        """
        for n,_ in list(self._registration.values()):
            if name == n: return True
        return False

    def deregister(self, id):
        """ Removes a Routee from the registry. """
        if id is not None:
            routee = self._registration.pop(id, None)
            if isinstance(routee, Interface): routee.close()
            logging.debug("deregistered: %s"%id)
    
    def sendMsg(self, msg):
        """ Adds a message to the message queue so it can be sent. """
        self._msg_queue.put(msg) #blocks until open slot... SHOULDN'T HAPPEN!
        logging.debug("added message to send queue: %s" % msg)
    
    def flush(self):
        """ Make sure all messages get where they are going before shutdown."""
        #FIXME: Push all messages were they need to go. Right now just purging.
        try:
            while not self._msg_queue.empty(): 
                self._msg_queue.get()
        except:pass
        finally:#deregister everyone, makes sure all interface threads are dead
            while len(self._registration) > 0:
                _,routee = self._registration.popitem()
                if isinstance(routee, Interface): routee.close()
    
    def _run(self, triggermethod=lambda:False):
        """ This is the thread that runs and pushes messages everywhere. """
        logging.debug("ComRouter thread has started")
        while triggermethod():
            try:
                if self._msg_queue.empty():raise queue.Empty
                msg = self._msg_queue.get() #remove and return a message
                
                # If the destination is registered, then send it
                logging.debug("registered: %s"%str(list(self._registration.keys())))
                logging.debug("destination: %s"%msg.getDestination())
                if msg.getDestination() in list(self._registration.keys()):
                    #ok to send since its been registered
                    _,ref = self._registration.get(msg.getDestination())
                    Thread(target=ref._handle_msg, args=(msg,)).start()
                    logging.debug("sent message: %s" % msg)
                    
                # if the destination is not "registered" but its a known type
                elif msg.getDestination() == "" or msg.getDestination() == None:
                    
                    # Check if the message type is an alert, if it is, then send it
                    # to EVERYONE! 
                    if msg.getType() == ALERT_MSG_TYPE:
                        for name, routee in self._registration.values():
                            Thread(target=routee._handle_msg, args=(msg,)).start()
                            logging.debug("sent message to %s: %s"% (name, msg))
                            
                    # if not send it to the daemon to handle.
                    else:
                        logging.debug("sent message to daemon: %s" % msg)
                        Thread(target=self._daemon._handle_msg,args=(msg,)).start()
                        
                # if we dont know how to handle the message, log and discard it. oh well.
                else:
                    logging.warning("The message trying to send,"+
                            "was not registered. I don't know who %s is." % 
                            msg.getDestination())
                    
            except queue.Empty: pass
            except Exception as e:
                logging.exception(e)
    
            ## then we sleep for a while. This is randomized because we don't really know
            ## the speed at which messages are being sent. We could write a method to adapt
            ## to the internal rate, later. But currently randomizing provides a better 
            ## compensation than a constant time factor.
            try: time.sleep(random.randint(1,3)) # TODO: efficient? 
            #LATER: clean out the registration array... if the objects don't exist anymore? 
            except: pass
            
        #when closing, it doesn't need to clean anything, just die and 
        #log about it
        logging.debug("ComRouter thread has died")
        
        