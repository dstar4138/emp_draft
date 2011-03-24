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

from empbase.comm.interface import Interface
from empbase.comm.messages import strToMessage, makeMsg, makeErrorMsg,  \
                                  ERROR_MSG_TYPE, ALERT_MSG_TYPE,       \
                                  COMMAND_MSG_TYPE, Message
                                  
class MessageRouter():
    """ Routing is now an object, this is so if we needed two instances of the
    Router with different registry information we can. Honestly, I can't think
    of a valid case when we would need to though.
    """
    def __init__(self, registry, daemon, attachments):
        self._routees = {} #the registered receivers of messages (Routee objects)
        self._msg_queue = queue.Queue()#thread-safe message queue
        self._registry = registry # the object all attachments and events are registered
        self._attachments = attachments
        self._daemon = (self._registry.daemonId(), daemon)
            
    def addInterface(self, ref):
        """ If this throws an error, it's because the reference isn't 
        registered yet. 
        """
        self._routees[ref.ID] = ref
    
    def isRegistered(self, cid):
        """ Checks the internal registry if the id or name is registered. """
        if self._registry.isRegistered(cid):
            logging.debug("%s is registered"%cid)
            return True
        else:
            logging.debug("%s is NOT registered"%cid)
            return False
    
    def rmInterface(self, id):
        """ Removes an interface from the registry."""
        if self._routees.pop(id, False):
            return self._registry.deregister(id)
        return False
        
        
    def sendMsg(self, msg):
        """ Adds a message to the message queue so it can be sent. """
        self._msg_queue.put(msg) #blocks until open slot... SHOULDN'T HAPPEN!
        logging.debug("added message to send queue: %s" % msg)
    
    def flush(self):
        """ Make sure all messages get where they are going before shutdown."""
        # LATER: Push all messages were they need to go. Right now just purging.
        try:
            while not self._msg_queue.empty(): 
                self._msg_queue.get()
        except:pass
        finally:#deregister all tmps, makes sure all interface threads are dead
            while len(self._routees) > 0:
                id,routee = self._routees.popitem()
                if isinstance(routee, Interface):
                    logging.debug("found interface that im deregistering") 
                    routee.handle_msg(makeMsg("shutting-down",None,id))
                    routee.close()
                logging.debug("deregistered: %s"%id)
                
                
    def __sendToDaemon(self, msg):
        #send to daemon.
        logging.debug("sending to daemon")
        _,base=self._daemon
        if base is not None:
            if msg.getType() == COMMAND_MSG_TYPE:
                found = False
                for cmd in base.get_commands():
                    logging.debug("comparing: %s ?= %s"%(cmd,msg.getValue()))
                    if cmd == msg.getValue():
                        found = True 
                        Thread(target=self._cmdrun, args=msg.get("args"),
                               kwargs={"cmd":cmd, "dest":msg.getSource(),
                                       "source":msg.getDestination()}).start()
                if not found:
                    self.sendMsg(makeErrorMsg("Command does not exist.",msg.getDestination(), msg.getSource() ))
            elif msg.getType() == ERROR_MSG_TYPE:
                logging.error("error from %s: %s" % (msg.getSource(), msg.getValue()))
            else: #alert or base we ignore
                pass
        else: logging.debug("should have sent the message to the base handler")
        
    def _cmdrun(self, *args, cmd=None, dest=None, source=None):
        """ Runs as a separate thread for taking care of commands."""
        try:
            if cmd == None: return
            value = cmd.run(*args)
            self.sendMsg(makeMsg(value,source,dest))
        except Exception as e:
            self.sendMsg(makeErrorMsg(str(e), source, dest))    
           
    def startRouter(self, triggermethod=lambda:False):
        """ This is the thread that runs and pushes messages everywhere. """
        
        logging.debug("ComRouter thread has started")
        while triggermethod():
            try:
                if self._msg_queue.empty():raise queue.Empty
                msg = self._msg_queue.get() #remove and return a message
                
                if isinstance(msg, str): 
                    msg = strToMessage(msg)
                elif msg is None or not isinstance(msg, Message): 
                    continue
                
                logging.debug("destination: %s"%msg.getDestination())
                
                # if the destination is not "registered" but its a known type
                if msg.getDestination() == "" or msg.getDestination() == None:
                    # Check if the message type is an alert, if it is, then send it
                    # to all interfaces and alerters. We keep this functionality for
                    # possible use in Chat programs or quick universal relays. But
                    # actual "Alerts" are now called Events and are managed by the
                    # EventManager.
                    if msg.getType() == ALERT_MSG_TYPE:
                        for id in list( self._routees.keys()):
                            logging.debug("sending alert to %s: %s"% (id, msg))
                            _,ref = self._routees.get(id)
                            if isinstance(ref, Interface):
                                Thread(target=ref.handle_msg, args=(msg,)).start()
                            # Notice, alarms don't get the message.
                            
                    # if not send it to the daemon to handle.
                    else:
                        self.__sendToDaemon(msg)
                            
                
                elif self.isRegistered(msg.getDestination()):
                    if msg.getDestination() == "daemon" or msg.getDestination() == None:
                        self.__sendToDaemon(msg)
                        continue
                    # if its registered, it could be a routee or an attachment.
                    if msg.getType() == COMMAND_MSG_TYPE:
                        cmds = self._attachments.getCommands(msg.getDestination())
                        if cmds is not None:#we can run the command and send the result.
                            found = False
                            for cmd in cmds:
                                if cmd == msg.getValue():
                                    found = True
                                    Thread(target=self._cmdrun, args=msg.get("args"),
                                           kwargs={"cmd":cmd, "dest":msg.getSource(),
                                                   "source":msg.getDestination()}).start()
                            if not found:
                                self.sendMsg(makeErrorMsg("Command does not exist.",msg.getDestination(), msg.getSource() ))
                            continue   
                            
                    #ok to send since its been registered, but is a routee
                    ref = self._routees.get(msg.getDestination(),None)
                    if ref is not None:
                        logging.debug("sending message: %s" % msg)
                        Thread(target=ref.handle_msg, args=(msg,)).start()
                    else: #send to daemon.
                        self.__sendToDaemon(msg)
                
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
            if not self._msg_queue.empty(): continue
            try: time.sleep(random.random())
            except: pass
            
        #when closing, it doesn't need to clean anything, just die and 
        #log about it
        logging.debug("ComRouter thread has died")
        
    
    
        