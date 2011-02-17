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


__version__ = "0.5.1"
__description__ = """
The SMTG-Daemon is responsible for alerts, updates and other plug-in
communications. However, any interaction should go through smtg rather
than smtgd. This is so logging and proper error handling can be
provided as that is the user interface and not a background server. 
Please note that the daemon controls are also provided in the smtg 
interface for your use.

The Daemon assumes that the installation went correctly as directory 
settings and default subprocess/threading control is pulled from
the configuration files.
"""

import time
import logging
from threading import Thread

from smtg.plugin.SmtgPluginManager import SmtgPluginManager
from smtg.config.defaults import default_plugin_dirs
from smtg.config.logger import setup_logging
from smtg.config.SmtgConfigParser import SmtgConfigParser

from smtg.daemon.RDaemon import RDaemon
from smtg.daemon.comm.interface import Interface
from smtg.daemon.comm.CommRouter import CommRouter
from smtg.daemon.daemonipc import DaemonServerSocket, DaemonClientSocket
from smtg.daemon.comm.messages import makeErrorMsg, makeCommandMsg, makeAlertMsg,  \
                                      makeMsg, strToMessage, COMMAND_MSG_TYPE 


class SmtgDaemon(RDaemon):
    """ The Daemon for SMTG, all communication to this daemon goes through smtgd.py
    or the comm port via a DaemonClientSocket. To connect, get the port number and
    then connect either with a regular UDP-8 encoded TCP socket or the 
    DaemonClientSocket.

    The daemon handles the feed and connection loops along with all configuration
    validation. It does not handle interface registration, which should be done 
    through the registration steps handled by smtgd.py. Please look there if you
    want to know how to register your interface with the local smtg daemon.
    """
    
    def __init__(self, configfile=None, dprg="smtgd.py"):
        """Load the configuration files, create the CommRouter, and then create 
        the daemon. 
        """
        # get yourself a counter!
        self.start_time=time.time() 

        # now set up the internal configuration via a config file.
        self.config=SmtgConfigParser(configfile)
        self.config.validateInternals()
        setup_logging(self.config)

        # create the comm router for internal thread communication.
        self._commrouter = CommRouter(self)

        # adjust by the configurations....
        RDaemon.__init__(self, self.config.get("Daemon", "pid-file"),
                              "SmtgDaemon", 
                              self._commrouter,
                              pchannel=self.config.getint("Daemon", "port"),
                              dprog=dprg,
                              dargs=configfile)
         
    def stop(self):
        """ Stops the local Smtg daemon by killing both threads. """
        try:   
            # kill thread 3 (e.g. _t2) with a quick blast from a socket
            daemon=DaemonClientSocket(self.getComPort())
            daemon.connect()
            daemon.send(makeCommandMsg("killmenow", self.ID, kill=True))
            daemon.close()
        except Exception as e:
            logging.exception(e)
            raise e
        
        finally:# then say we're dead regardless.
            RDaemon.stop(self)

    def restart(self):
        """ Restarts the daemon by killing both threads, and making sure their
        both down before trying to run the daemon again.
        """
        try: 
            self.stop()
            time.sleep(6)
        except: pass
        self.start()
           
  
    def _handle_msg(self, msg):
        """ Handles the incoming messages passed to it from the CommReader. """
        logging.debug("daemon received: %s" % msg)
        action = strToMessage(msg)
        logging.debug("daemon running with action")
        if action is None or action.getType() != COMMAND_MSG_TYPE:
            logging.debug("daemon thinks action is bad...")
            self._commrouter.sendMsg(makeErrorMsg("invalid action",
                                                  action.getSource()))
            return
            
        logging.debug("Message accepted by daemon, trying to run it now.")
        if action.get("kill"):
            if action.getValue() == "killmenow":
                self._commrouter.sendMsg(makeAlertMsg("daemon closing connection", self.ID))
            elif action.getValue() == "status":
                self._commrouter.sendMsg(makeMsg(self.NAME,"SMTG-D Running since: "+str(self.start_time)))
            else:
                logging.warning("Action %s is not a valid single ability." % action.getValue())
                self._commrouter.sendMsg(makeErrorMsg("invalid action",
                                                  action.getSource()))
            self._commrouter.deregister(action.getSource())
        else:
            # TODO: handle other actions
            pass
  

    def _run(self):
        """ Starts the three threads that make up the internals of the daemon
        and creates both the AlertManager and the PluginManager for them to pull
        the Alerters and Plug-ins for the daemons use.
        
            Here is a quick outline of what each of the three threads are and 
        do, for a more in-depth look, look at the consecutive method calls:
        
            - Thread 1: the current one, this is the pull loop. It updates the
                LoopPlugins every time interval. This time interval is set by 
                the configuration file.
                
            - Thread 2: this is the CommReader._run() method. It handles all
                inter-thread communication. See CommReader for more info.
                
            - Thread 3: this is _t2(), it handles incoming communication to the
                port that the SmtgDaemon listens to for Interfaces. See the
                interface API for more information on how to talk to the 
                daemon. 
        """
        try:
            # load the plug-in manager now and search for the plug-ins.
            self.pman = SmtgPluginManager(default_plugin_dirs, 
                                          self.config, 
                                          self._commrouter)
            self.pman.collectPlugins()
            self.pman.activatePlugins()
    
    
            #TODO: start AlertManager and collect/activate alerters
    
    
            # starts the comm router running to send messages!!
            Thread(target=self._commrouter._run).start()
            
            # start the interface thread
            Thread(target=self.__t2).start()
    
            # start the pull loop.
            logging.debug("pull-thread started")
            while self.isRunning():
                
                # get all active feed plug-ins
                activeFeeds = self.pman.getLoopPlugins()
                if activeFeeds:
                    for feed in activeFeeds:
                        if feed.is_activated:
                            # for each active feed run the update function with no
                            # arguments. The only time arguments are needed 
                            # is if the plug-in was force updated by a command.
                            logging.debug("pulling feed %s" % feed.name)
                            feed.plugin_object._update()
                
                try: # sleep, and every five seconds check if still alive
                    count=0
                    sleep_time = self.config.getfloat("Daemon","update-speed") * 60.0
                    while(count<sleep_time):
                        count+=5
                        time.sleep(5)#every 5 seconds check state
                        if not self.isRunning(): break;
                except: pass
                
            self._commrouter.flush()
            self.config.save()
            logging.debug("pull-thread is dead")

        except Exception as e:
            logging.error("Pull-thread was killed by: %s" % str(e))
            logging.exception(e)
        
            
    def __t2(self):
        """ Interface Server method, this runs in a new thread when the 
        daemon starts. See _run() method for more information.
        """
        
        logging.debug("communication-thread started")
        # Create socket and bind to address
        TCPSock = DaemonServerSocket(portNum=self.getComPort())
        
        while self.isRunning(): # keep listening forever
            try:
                client_socket = TCPSock.accept()
        
                # create an interface out of the socket
                # LATER: authentication can go here, before they connect. (eg logging in)
                interface = Interface(client_socket)
                identifier = self._commrouter.register("interface", interface)
            
                # since there are abilities that this person can perform
                # ask for first action, if its not uber-important, throw
                # to new thread, otherwise execute it.
                self._commrouter.sendMsg(makeCommandMsg("proceed","",dest=identifier))
            except: pass #catches a timeout and allows for daemon status checking
            
        TCPSock.close()
        logging.debug("communication-thread is dead")

