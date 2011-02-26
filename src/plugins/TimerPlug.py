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
import random
import logging
from socket import timeout
from threading import Timer

import smtg.comm.routing as routing
from smtg.attach.attachments import SignalPlugin
from smtg.daemon.daemonipc import DaemonServerSocket
from smtg.comm.messages import COMMAND_MSG_TYPE, makeErrorMsg, makeMsg, makeAlertMsg

DEFAULT_PORT = 8081
DEFAULT_MAXRAND = 360
DEFAULT_MINRAND = 20


TIMER = {"status": "Returns the status of a given timer, or all of them.",
         "add"   : "Add a timer for the specified amount of time in seconds.",
         "stop"  : "Stops the running server, and kills all timers/connections",
         "rm"    : "Remove a timer by its id",
         "arand" : "Add a timer for a random amount of time between two numbers.",
         "time"  : "Set a timer to go off at a given time in the form: 'hh:mm pm/am'",
         "port"  : "Get the port to connect to on the current host that the alert msg will signal down."}

class TimerPlug(SignalPlugin):
    """The Timer plug-in will be the most simplistic SignalPlugin. It will
    create a timer in accordance with the time you need, and then send an 
    alert once the timer is finished. You can ask for a port number from 
    this plug-in if you want the alert to bypass the daemon all together and
    ping some other program.
    """
    def __init__(self, conf):
        SignalPlugin.__init__(self,conf, autostart=False) #force no autostart
        self._timers = []
        self._connections = []
        self._port = DEFAULT_PORT
        self.running = False
        if "port" in self.config:
            try: self._port =  int(self.config["port"])
            except: self._port = DEFAULT_PORT
            
        self._maxrand = DEFAULT_MAXRAND 
        if "maxrand" in self.config:
            try: 
                self._maxrand =  int(self.config["maxrand"])
                if self._maxrand < 1: raise
            except: self._maxrand = DEFAULT_MAXRAND
            
        self._minrand = DEFAULT_MINRAND
        if "minrand" in self.config:
            try: 
                self._minrand =  int(self.config["minrand"])
                if self._minrand < 1: raise
            except: self._minrand = DEFAULT_MINRAND
            
        self._socket = DaemonServerSocket(port=self._port)
        #TODO: get these other settings working.
        #                                 ip_whitelist=whitelist,
        #                                 externalBlock=self.config.getboolean("Daemon","local-only"),
        #                                 allowAll=self.config.getboolean("Daemon", "allow-all"))
        

    def save(self):
        """ Save my internal configuration."""
        SignalPlugin.save(self)
        self.config["port"] = self._port
        self.config["maxrand"] = self._maxrand
        self.config["minrand"] = self._minrand
        
        
    def get_commands(self):
        """ Returns the command dictionary! """
        return TIMER

    def handle_msg(self, msg):
        try:
            if msg.get("message") != COMMAND_MSG_TYPE: return
            
            #since its a command, lets handle it.
            dest = msg.getSource()
            if msg.getValue() == "add":
                self.addtimer(int(msg.get("args")[0]), dest)
            elif msg.getValue() == "rm":
                self.removetimer(int(msg.get("args")[0]), dest)
            elif msg.getValue() == "arand":
                if len(msg.get("args")) == 1: #set min=args
                    min = int(msg.get("args")[0])
                    if min < 1:
                        routing.sendMsg(makeErrorMsg("Value given for arand must be larger than 1.", self.ID,dest))
                    else:    
                        self.addtimer(random.randint(min, self._maxrand), dest)
                elif len(msg.get("args")) ==2: #set both max and min
                    min = int(msg.get("args")[0])
                    max = int(msg.get("args")[1])
                    if min < 1 or max <1:
                        routing.sendMsg(makeErrorMsg("Value given for arand must be larger than 1.", self.ID,dest))
                    elif max > min:
                        t=min
                        max=min
                        min=t
                    self.addtimer(random.randint(min, max), dest)
                else: #use the variables from the config file
                    self.addtimer(random.randint(self._minrand, self._maxrand), dest)
            elif msg.getValue() == "status":
                routing.sendMsg(makeMsg("There are "+str(len(self._timers))+" timers running.",self.ID,dest))
            elif msg.getValue() == "port":
                routing.sendMsg(makeMsg(self._port,self.ID,dest))
                
            elif msg.getValue() == "stop": 
                self.stop()
                
            elif msg.getValue() == "time":
                #TODO: add this functionality
                routing.sendMsg(makeErrorMsg("Action not implemented yet. Sorry!", self.ID,dest))
            else:
                routing.sendMsg(makeErrorMsg("Invalid action", self.ID,dest))
            
        except Exception as e:
            try:routing.sendMsg(makeErrorMsg(e,self.ID,msg.getSource()))
            except:pass
    
    def addtimer(self, seconds, dest):
        """ Adds a timer, and starts the SingalPlugin if needed."""
        try:
            t = Timer(seconds,self.sendSignal)
            t.start()
            self._timers.append(t)
            self.activate() #starts the run thread if its not already running
            
            routing.sendMsg(makeMsg("Started timer for "+str(seconds)+" seconds!",self.ID,dest))
        except:
            routing.sendMsg(makeErrorMsg("Couldn't add timer!",self.ID,dest))
            
    def removetimer(self, index, dest):
        """ Removes a timer. The _run method will notice if nothings there. """
        try:
            t = self._timers.pop(index)
            t.cancel()
            routing.sendMsg(makeMsg("Successfully removed timer!",self.ID,dest))
        except:
            routing.sendMsg(makeErrorMsg("Couldn't removed timer!",self.ID,dest))
    
    def sendSignal(self):
        alert = makeAlertMsg("Timer went off!!",self.ID)
        for conn in self._connections:
            try:conn.send(alert)
            except:pass
        routing.sendMsg(alert)
        self._timers = list(filter(lambda a: not a.finished.is_set(), self._timers))
            
    def killconnections(self):
        """ Close all open connections. """
        for conn in self._connections:
            try:conn.close()
            except:pass
        self._connections=[]
                             
    def deactivate(self):
        """ stops all connections and the server. """
        SignalPlugin.deactivate(self)
        self.killconnections()
                 
                
    def run(self):
        """ Runs when there are timers to watch, and then sends a signal when there is need to."""
        try:
            self.is_activated=True
            while self.is_activated:
                try:
                    #make sure all of the connections are saved.
                    connection = self._socket.accept()
                    self._connections.append(connection)
                except timeout: pass
        except Exception as e:
            logging.exception(e)
        finally:
            self.deactivate()