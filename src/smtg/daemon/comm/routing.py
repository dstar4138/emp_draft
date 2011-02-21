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
from smtg.daemon.comm.messages import strToMessage, makeMsg, ALERT_MSG_TYPE


_msg_queue = queue.Queue()
_registration = {}
        
def register(name, ref):
    """ Registers you with the router, and any messages that are directed
    at you will be forwarded to you. You MUST be of the type Routee. """
    
    while 1:
        id = "%s" % str(random.random())[2:12]
        if id in list(_registration.keys()): 
            continue
        else:
            _registration[id] = (name,ref)
            return id

def isRegisteredByID(id):
    """ Checks if the id is registered in the Router, returns a boolean."""
    return (id in list(_registration.keys()))
        

def isRegisteredByName(name):
    """ Checks if the name is registered, returns the id or False if otherwise 
    not registered.
    """
    for n,_ in list(_registration.values()):
        if name == n: return True
    return False

def getReferenceByID(id):
    """ Get the reference to the routee given the id."""
    _,ref = _registration.get(id, (None,None))
    return ref  

def getReferenceByName(name):
    """ Get the reference to the routee given the name."""
    for n,ref in list(_registration.values()):
        if name == n: return ref
    return None

def getIDByName(name):
    for id in list(_registration.keys()):
        n,_ = _registration.get(id, (None,None))
        logging.debug("n=%s, name=%s" %(n,name))
        if n == name: return id
    return None

def deregister(id):
    """ Removes a Routee from the registry. """
    if id is not None:
        routee = _registration.pop(id, None)
        if isinstance(routee, Interface): routee.close()
        logging.debug("deregistered: %s"%id)

def sendMsg(msg):
    """ Adds a message to the message queue so it can be sent. """
    _msg_queue.put(msg) #blocks until open slot... SHOULDN'T HAPPEN!
    logging.debug("added message to send queue: %s" % msg)

def flush():
    """ Make sure all messages get where they are going before shutdown."""
    #FIXME: Push all messages were they need to go. Right now just purging.
    try:
        while not _msg_queue.empty(): 
            _msg_queue.get()
    except:pass
    finally:#deregister everyone, makes sure all interface threads are dead
        while len(_registration) > 0:
            id,(_,routee) = _registration.popitem()
            if isinstance(routee, Interface):
                logging.debug("found interface that im deregistering") 
                routee._handle_msg(makeMsg("shutting-down",None,id))
                routee.close()
            logging.debug("deregistered: %s"%id)

def startRouter(base=None, triggermethod=lambda:False):
    """ This is the thread that runs and pushes messages everywhere. """
    logging.debug("ComRouter thread has started")
    while triggermethod():
        try:
            if _msg_queue.empty():raise queue.Empty
            msg = _msg_queue.get() #remove and return a message
            
            if isinstance(msg, str): msg = strToMessage(msg)
            elif msg is None: continue
            
            # If the destination is registered, then send it
            logging.debug("registered: %s"%str(list(_registration.keys())))
            logging.debug("destination: %s"%msg.getDestination())
            if msg.getDestination() in list(_registration.keys()):
                #ok to send since its been registered
                _,ref = _registration.get(msg.getDestination())
                logging.debug("sending message: %s" % msg)
                Thread(target=ref._handle_msg, args=(msg,)).start()
                
            # if the destination is not "registered" but its a known type
            elif msg.getDestination() == "" or msg.getDestination() == None:
                
                # Check if the message type is an alert, if it is, then send it
                # to EVERYONE! 
                if msg.getType() == ALERT_MSG_TYPE:
                    for id in list( _registration.keys()):
                        logging.debug("sending message to %s: %s"% (id, msg))
                        _,ref = _registration.get(id)
                        Thread(target=ref._handle_msg, args=(msg,)).start()
                        
                # if not send it to the daemon to handle.
                else:
                    if base is not None:
                        logging.debug("sending message to daemon: %s" % msg) 
                        Thread(target=base._handle_msg,args=(msg,)).start()
                    else:
                        logging.debug("should have sent the message to the base handler")
                        
            # if we dont know how to handle the message, log and discard it. oh well.
            else:
                logging.warning("I don't know who %s is, msg=%s" % 
                                (msg.getDestination(), str(msg.getValue())))
                
        except queue.Empty: pass
        except Exception as e:
            logging.exception(e)

        ## then we sleep for a while. This is randomized because we don't really know
        ## the speed at which messages are being sent. We could write a method to adapt
        ## to the internal rate, later. But currently randomizing provides a better 
        ## compensation than a constant time factor.
        if not _msg_queue.empty(): continue
        try: time.sleep(random.random()) # TODO: efficient? 
        except: pass
        
    #when closing, it doesn't need to clean anything, just die and 
    #log about it
    logging.debug("ComRouter thread has died")
    


class Routee():
    """ Base object for every internal possibility for communication 
    Within SMTG,"""
    def __init__(self, name):
        """ Create the Routee object and register it with a Router."""
        self.ID = register(name, self)
        self.NAME = name
        
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
    def __init__(self, socket):
        """ Create an Interface using a socket. Assumes that it is of the
        type DaemonServerSocket.
        """
        Routee.__init__(self, "interface")
        self._socket = socket
        
    def _handle_msg(self, msg):
        """ Interfaces "handle the message" by sending it to the 
        interface on the other end of the socket.
        """
        self._socket.send(msg)
        
    def _run(self):
        """ Runs the receiving portion of the interface. """
        logging.debug("starting interface comm")
        self._socket.setblocking(True)
        try:
            while 1:
                msg = self._socket.recv()
                if not msg: break
                else: sendMsg(strToMessage(msg))
        except Exception as e: 
            logging.error("interface died because: %s"%e)
        finally:
            logging.debug("ending interface comm")
            deregister(self.ID)
            
    def close(self):
        """ Closes the communication to the Interface. """
        self._socket.shutdown()

    