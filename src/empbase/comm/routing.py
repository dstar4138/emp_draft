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
import time
import queue
import random
import logging
from threading import Thread

#import smtg.comm.registry as registry
from empbase.comm.messages import strToMessage, makeMsg, ALERT_MSG_TYPE
from empbase.comm.interface import Interface
from empbase.attach.attachments import EmpAlarm

## Routing protocol:
##   The following are the functions that should be used for
##  sending messages within the system.

_msg_queue = queue.Queue() #thread-safe message queue
_routees = {} #the registered receivers of messages (Routee objects)
#_registry = registry.load() # the registry xml file
        
def register(name, ref):
    """ Registers you with the router, and any messages that are directed
    at you will be forwarded to you. You MUST be of the type Routee. """
    
    #TODO: adjust the registration process to compensate for the registry.
    
    while 1:
        id = "%s" % str(random.random())[2:12]
        if id in list(_routees.keys()): 
            continue
        else:
            _routees[id] = (name,ref)
            ref.ID = id
            logging.debug("registered: %s=%s"%(id,name))
            break

def isRegisteredByID(id):
    """ Checks if the id is registered in the Router, returns a boolean."""
    return (id in list(_routees.keys()))
        

def isRegisteredByName(name):
    """ Checks if the name is registered, returns the id or False if otherwise 
    not registered.
    """
    for n,_ in list(_routees.values()):
        if name == n: return True
    return False

def getReferenceByID(id):
    """ Get the reference to the routee given the id."""
    _,ref = _routees.get(id, (None,None))
    return ref  

def getReferenceByName(name):
    """ Get the reference to the routee given the name."""
    for n,ref in list(_routees.values()):
        if name == n: return ref
    return None

def getIDByName(name):
    for id in list(_routees.keys()):
        n,_ = _routees.get(id, (None,None))
        logging.debug("n=%s, name=%s" %(n,name))
        if n == name: return id
    return None

def deregister(id):
    """ Removes a Routee from the registry. """
    if id is not None:
        routee = _routees.pop(id, None)
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
        while len(_routees) > 0:
            id,(_,routee) = _routees.popitem()
            if isinstance(routee, Interface):
                logging.debug("found interface that im deregistering") 
                routee.handle_msg(makeMsg("shutting-down",None,id))
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
            logging.debug("registered: %s"%str(list(_routees.keys())))
            logging.debug("destination: %s"%msg.getDestination())
            if isRegisteredByID(msg.getDestination()):
                #ok to send since its been registered
                _,ref = _routees.get(msg.getDestination())
                logging.debug("sending message: %s" % msg)
                Thread(target=ref.handle_msg, args=(msg,)).start()
                
            # if the destination is not "registered" but its a known type
            elif msg.getDestination() == "" or msg.getDestination() == None:
                
                # Check if the message type is an alert, if it is, then send it
                # to all interfaces and alerters
                if msg.getType() == ALERT_MSG_TYPE:
                    for id in list( _routees.keys()):
                        logging.debug("sending message to %s: %s"% (id, msg))
                        _,ref = _routees.get(id)
                        if isinstance(ref, Interface) or isinstance(ref, EmpAlarm):
                            Thread(target=ref.handle_msg, args=(msg,)).start()
                        
                # if not send it to the daemon to handle.
                else:
                    if base is not None:
                        logging.debug("sending message to daemon: %s" % msg) 
                        Thread(target=base.handle_msg,args=(msg,)).start()
                    else:
                        logging.debug("should have sent the message to the base handler")
                        
            elif isRegisteredByName(msg.getDestination()):
                #they messed up and passed it to the name, rather than the id. so we'll try to
                # get the id and send it.
                ref = getReferenceByName(msg.getDestination())
                logging.debug("sending message: %s" % msg)
                Thread(target=ref.handle_msg, args=(msg,)).start()
            
            # if we don't know how to handle the message, log and discard it. oh well.
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
        try: time.sleep(random.random()) # XXX: efficient? 
        except: pass
        
    #when closing, it doesn't need to clean anything, just die and 
    #log about it
    logging.debug("ComRouter thread has died")
    


    