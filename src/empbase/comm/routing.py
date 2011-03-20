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

from empbase.comm.routee import Routee
from empbase.daemon.RDaemon import RDaemon
from empbase.comm.interface import Interface
from empbase.attach.attachments import EmpAlarm, EmpPlug
from empbase.comm.messages import strToMessage, makeMsg, makeErrorMsg,  \
                                  ALERT_MSG_TYPE, COMMAND_MSG_TYPE, Message
                                  
class MessageRouter():
    """ Routing is now an object, this is so if we needed two instances of the
    Router with different registry information we can. Honestly, I can't think
    of a valid case when we would need to though.
    """
    def __init__(self,registry):
        self._routees = {} #the registered receivers of messages (Routee objects)
        self._msg_queue = queue.Queue()#thread-safe message queue
        self._cmd_map = {} # internal map of commands.
        self._registry = registry # the object all attachments and events are registered
        self._daemon = ("",None)
            
    def register(self, name, module, ref):
        """ Registers the attachment/Daemon/Routee with the router. This is 
        used in conjunction with the Registry object that the Router has 
        internally. Once you register a Plug, Alarm, or Daemon the ID will
        persist even after closing EMP."""
        
        if isinstance(ref, Interface):
            id = self._registry.registerInterface(name, ref)
            # keep the ref so we can kill the connection on our side when
            # we stop emp. See self.flush() for more details.
            self._routees[id] = ref
        
        ## We are keeping capability to distinguish between routees and other
        ## attachments in case we want to add a Routee of a different type.
        elif isinstance(ref, Routee):
            id = self._registry.registerUnkown(name, ref)
            self._routees[id] = ref 

        ## All attachments are utilized differently, they have commands to speed
        ## up message passing.
        elif isinstance(ref, EmpAlarm):
            id = self._registry.registerAlarm(name, module, ref)
            self._cmd_map[id] = ref.get_commands()
            
        elif isinstance(ref, EmpPlug):
            id = self._registry.registerPlug(name, module, ref)
            self._cmd_map[id] = ref.get_commands()
            
        ## The daemon is handled specially... 
        #TODO:?? Should daemon get to use Command?
        elif isinstance(ref, RDaemon):
            id = self._registry.daemonId()
            self._daemon = (id,ref)   
            
        # If we dont know what type of object it is, we can't register it.
        else: raise Exception("Not valid object to register!")
    
    
    def isRegistered(self, cid):
        """ Checks the internal registry if the id or name is registered. """
        return self._registry.isRegistered(cid)
    
    def deregister(self, id):
        """ Removes a Routee from the registry. """
        if not self._registry.deregister(id):
            #it must be a Routee or something else so
            # try the _routees variable.
            if not self._routees.pop(id, False):
                #then it didnt exist. sorry
                return False
        return True
        
        
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
                
    
    def _cmdrun(self, *args, cmd=None, dest=None, source=None):
        """ Runs as a separate thread for taking care of commands."""
        try:
            if cmd == None: return
            value = cmd.run(args)
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
                
                if self.isRegistered(msg.getDestination()) and msg.getType() == COMMAND_MSG_TYPE:
                    # if its registered, it could be a routee or an attachment.
                    cmds = self._cmd_map(msg.getDestination(),None)
                    if cmds is not None:
                        #we can run the command and send the result.
                        for cmd in cmds:
                            if cmd == msg.getValue():
                                Thread(target=self._cmdrun, 
                                       args=tuple(msg.get("args")),
                                       kwargs={"cmd":cmd,
                                               "dest":msg.getSource(),
                                               "source":msg.getDestination()}).start()
                    else:
                        #ok to send since its been registered, but is a routee
                        ref = self._routees.get(msg.getDestination(),None)
                        if ref is not None:
                            logging.debug("sending message: %s" % msg)
                            Thread(target=ref.handle_msg, args=(msg,)).start()
                        else: #send to daemon.
                            _,base=self._daemon
                            if base is not None:
                                logging.debug("sending message to daemon: %s" % msg) 
                                Thread(target=base.handle_msg,args=(msg,)).start()
                            else: logging.debug("should have sent the message to the base handler")
                            
                # if the destination is not "registered" but its a known type
                elif msg.getDestination() == "" or msg.getDestination() == None:
                    
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
                        _,base = self._daemon
                        if base is not None:
                            logging.debug("sending message to daemon: %s" % msg) 
                            Thread(target=base.handle_msg,args=(msg,)).start()
                        else: logging.debug("should have sent the message to the base handler")
                            
                
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
        
    
    
        