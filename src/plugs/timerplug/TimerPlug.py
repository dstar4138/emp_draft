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
from plugs.timerplug.mytimer import MyTimer

from empbase.event.events import Event
from empbase.comm.command import Command
from empbase.attach.attachments import SignalPlug
from empbase.daemon.daemonipc import DaemonServerSocket, timeout

DEFAULT_PORT = 8081
DEFAULT_MAXRAND = 360
DEFAULT_MINRAND = 20

LOWEST_RAND = 1

class TimerPlug(SignalPlug):
    """The Timer plug-in will be the most simplistic SignalPlugin. It will
    create a timer in accordance with the time you need, and then send an 
    alert once the timer is finished. You can ask for a port number from 
    this plug-in if you want the alert to bypass the daemon all together and
    ping some other program.
    """
    def __init__(self, conf):
        SignalPlug.__init__(self,conf, autostart=False) #force no autostart
        self._timers = []
        self._connections = []
        self.running = False

        self._port = self.config.getint("port", DEFAULT_PORT)
        self._maxrand = max(self.config.getint("maxrand", DEFAULT_MAXRAND), LOWEST_RAND)
        self._minrand = max(self.config.getint("minrand", DEFAULT_MINRAND), LOWEST_RAND)
        
        if self._maxrand < self._minrand:
            self._maxrand , self._minrand = self._minrand, self._maxrand 
            
        self._socket = DaemonServerSocket(port=self._port)
        #TODO: get these other settings working.
        #                                 ip_whitelist=whitelist,
        #                                 externalBlock=self.config.getboolean("Daemon","local-only"),
        #                                 allowAll=self.config.getboolean("Daemon", "allow-all"))
        
        # See the readme for more information on these commands.
        self._commands = [ #TODO: fix all triggers
                Command("status",   trigger=self.getstatus, help="Returns the status of a given timer, or all of them."),
                Command("timers",   trigger=self.gettimers, help="Return a printout of the timers' status."),
                Command("kill",     trigger=self.deactivate, help="Stops all timers/connections"),
                Command("stopall",  trigger=self.killtimers, help="Stops all timers!"),
                Command("closeall", trigger=self.killconnections, help="Closes all open connections."),
                Command("rm",       trigger=self.removetimer, help="Remove a timer by its index"),
                Command("arand",    trigger=self.arand, help="Add a timer for a random amount of time between two numbers."),
                Command("port",     trigger=self.getport, help="Get the port to connect to on the current host that the alert msg will signal down."),
                Command("add",      trigger=self.add, help="Add with three variables, first is seconds, second is minutes, third is hours.")]
        
        self.EVENT_timer = Event(self, "timer", "Timer went off!")
        self._events = [self.EVENT_timer]
        

    def save(self):
        """ Save my internal configuration."""
        SignalPlug.save(self)
        self.config.set("port", self._port)
        self.config.set("maxrand", self._maxrand)
        self.config.set("minrand", self._minrand)
        
    def get_commands(self):
        """ Returns the command dictionary! """
        return self._commands
    
    def get_events(self):
        #just to make sure everything is registered first.
        for e in self._events: e.register() 
        return self._events

    def getport(self):
        return self._port
    
    def getstatus(self):
        return "There are "+str(len(self._timers))+" timers running."

    def gettimers(self):
        timers = []
        for timer in self._timers:
            timers.append({"Created":timer.getTimeCreated(),
                           "Ends":timer.getTimeToEnd()})
        return timers
            
    def add(self, *args):
        seconds = 0
        if len(args) == 3: #hours
            seconds += int(args[2])*3600
                    
        if len(args) >= 2:#minutes
            seconds += int(args[1])*60
            
        if len(args) >= 1: #seconds  
            seconds += int(args[0])
            
        if len(args) > 0:
            self.addtimer(seconds)
        else:
            raise Exception("Add needs 1-3 arguments.")
        
    def arand(self, *args):
        if len(args) == 1: #set min=args
            min = int(args[0])
            if min < 1:
                raise Exception("Value given for arand must be larger than 1.")
            else:
                return self.addtimer(random.randint(min, self._maxrand))
        elif len(args) == 2: #set both max and min
            min = int(args[0])
            max = int(args[1])
            if min <= LOWEST_RAND or max <= LOWEST_RAND:
                raise Exception("Value given for arand must be larger than "+str(LOWEST_RAND))
                        
            #if max and min are switched, then swap them before testing.
            elif max < min: max, min = min, max
            return self.addtimer(random.randint(min, max))
        else: #use the variables from the config file 
            return self.addtimer(random.randint(self._minrand, self._maxrand))
            
    def addtimer(self, seconds):
        """ Adds a timer, and starts the SingalPlugin if needed."""
        try:
            t = MyTimer(seconds, self.sendSignal)
            t.start()
            self._timers.append(t)
            self.activate() #starts the run thread if its not already running
            
            return "Started timer for "+str(seconds)+" seconds!"
        except Exception as e:
            logging.exception(e)
            raise Exception("Couldn't add timer!")
            
    def removetimer(self, index):
        """ Removes a timer. The _run method will notice if nothings there. """
        try:
            t = self._timers.pop(index)
            t.cancel()
            return "Successfully removed timer!"
        except:
            raise Exception("Couldn't removed timer!")
    
    def sendSignal(self, timer):
        for conn in self._connections:
            try:conn.send(self.EVENT_timer)
            except:pass
        self.EVENT_timer.trigger()
        self._timers = list(filter(lambda a: not a.isFinished(), self._timers))
            
    def killconnections(self):
        """ Close all open connections. """
        for conn in self._connections:
            try:conn.close()
            except:pass
        self._connections=[]

    def killtimers(self):
        """ Cancels all running timers! """
        for timer in self._timers: timer.cancel()
        self._timers = []
            
    def deactivate(self):
        """ stops all connections and the server. """
        SignalPlug.deactivate(self)
        self.killconnections()
        self.killtimers()
                 
       
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
