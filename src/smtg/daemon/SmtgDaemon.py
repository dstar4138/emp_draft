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


__version__ = "0.4.1"
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
import random
import logging
from threading import Thread

from smtg.plugin.SmtgPluginManager import SmtgPluginManager
from smtg.daemon.security.register import isInterfaceRegistered
from smtg.config.defaults import default_plugin_dirs
from smtg.config.logger import setup_logging
from smtg.config.SmtgConfigParser import SmtgConfigParser
from smtg.daemon.daemon import Daemon
from smtg.daemon.daemonipc import DaemonServerSocket, DaemonClientSocket
from smtg.daemon.comm.messages import makeErrorMsg, makeCommandMsg, Message,  \
                                      makeMessage, strToMessage, COMMAND_MSG_TYPE

INVALID_ACTION = makeErrorMsg("invalid action")
INVALID_ACTION_BAD = makeErrorMsg("invalid action", kill=True)
PROCEED_ACTION = makeCommandMsg("proceed")
CLOSING_CONNECTION = makeErrorMsg("daemon closing connection", kill=True)


def getDaemonCommID():
    return 'd0000' #TODO: pull from registration file


class SmtgDaemon(Daemon):
    """The Daemon for SMTG, all communication to this daemon goes through smtgd.py
    or the comm port via a DaemonClientSocket. To connect, ask for your comm id via
    getDaemonCommID() and use the DaemonClientSocket. 

    The daemon handles the feed and connection loops along with all configuration
    validation. It does not handle interface registration, which should be done 
    through the registration steps handled by smtgd.py. Please look there if you
    want to know how to register your interface with the local smtg daemon.
    """
    def __init__(self, configfile=None, dprg="smtgd.py"):
        # the name of the daemon when sending messages.
        self.NAME="smtgd"
        
        # generate a randomized killswitch only the process knows
        self.KILLSWITCH = str(random.random())[2:12]
        
        # the kill-switch is the local communication identifier
        self.COM_ID = 'd'+self.KILLSWITCH 

        # get yourself a counter!
        self.start_time=time.time() 

        # now set up the internal configuration via a config file.
        self.config=SmtgConfigParser(configfile)
        self.config.validateInternals()
        setup_logging(self.config)
        
        # this just simplifies things.
        pid = self.config.get("Daemon", "pid-file")
        self.port = self.config.getint("Daemon", "port")
        self.sleep_time = self.config.getfloat("Daemon","update-speed") * 60.0;


        # adjust by the configurations....
        Daemon.__init__(self, pid,
                        pchannel=self.port,
                        dprog=dprg,
                        dargs=configfile)
         
    def stop(self):
        """Stops the local Smtg daemon by killing both threads."""
        # kill thread 2 with a quick blast from a socket
        try:
            daemon=DaemonClientSocket(self.getComPort())
            daemon.connect(self.COM_ID)
            daemon.send(makeCommandMsg("killmenow", kill=True))
            daemon.close()
        except Exception as e: 
            raise e
        
        finally:# then say we're dead regardless.
            Daemon.stop(self)

    def restart(self):
        """Restarts the daemon by killing both threads, and making sure their
        both down before trying to run the daemon again.
        """
        try: 
            self.stop()
            time.sleep(6)
        except: pass
        self.start()
                
    def _registered(self, id):
        """ Checks if the id is registered with the daemon """
        if self.COM_ID == id:
            return ["killswitch"]
        else:
            return isInterfaceRegistered(id)
    

    def __killall(self,connections):
        """Somewhat-gracefully kills all connections in a list of connections"""
        for connection in connections:
            try: connection.send(makeErrorMsg("Daemon Shutting Down", 
                                              dead=True, kill=True))
            except: pass
            finally:
                try: connection.close()
                except: pass       
  
    def _run(self):
        # push out the daemon threads.
        # -thread 1--this thread, an updating loop, pulls from sites.
        # -thread 2, a server to listen to incoming connections 
        #    from interfaces
        try:
            # start the interface thread
            Thread(target=self.__t2).start()
            
            # load the plug-in manager now and search for the plug-ins.
            self.pman = SmtgPluginManager(default_plugin_dirs)
            self.pman.collectPlugins()
            
            # activate all the plug-ins that need activating
            self.pman.activatePlugins()
    
            # start the pull loop.
            logging.debug("pull-thread started")
            while self.isRunning():
                
                # get all active feed plug-ins
                activeFeeds = self.pman.getFeedPlugins()
                for feed in activeFeeds:
                    # for each feed run the update function with no
                    # arguments. The only time arguments are needed 
                    # is if the plug-in was force updated by a command.
                    logging.debug("pulling feed %s" % feed.name)
                    feed.plugin_object.update()
                
                try:# sleep, and every five seconds check if still alive
                    count=0
                    while(count<self.sleep_time):
                        count+=5
                        time.sleep(5)#every 5 seconds check state
                        if not self.isRunning(): break;
                except: pass
            logging.debug("pull-thread is dead")

        except Exception as e:
            logging.error("Run-tread: %s" % str(e))
            raise e
            
    
    def __t2(self):# interface server, see _run()
        logging.debug("communication-thread started")
        # Create socket and bind to address
        TCPSock = DaemonServerSocket(portNum=self.port)
        interfaces = []
        while self.isRunning(): # keep listening forever
            client_socket = TCPSock.accept()
        
            # determine the person connecting
            identifier = client_socket.recv()
            logging.debug("daemon received id: %s" % identifier)
            abilities = self._registered(identifier)
            if not abilities:
                client_socket.send( CLOSING_CONNECTION )
                client_socket.close()
                continue
            
            # since there are abilities that this person can perform
            # ask for first action, if its not uber-important, throw
            # to new thread, otherwise execute it.
            client_socket.send( PROCEED_ACTION )
            answer = client_socket.recv()
            logging.debug("daemon received: %s" % answer)
            action = strToMessage(answer)
            logging.debug("daemon running with action")
            if action is None or action.getType() != COMMAND_MSG_TYPE:
                logging.debug("daemon thinks action is bad...")
                client_socket.send( INVALID_ACTION_BAD )
                client_socket.close()
                continue
            
            logging.debug("Message accepted by daemon, trying to run it now.")
            if action.get("kill"):
                if "status" in abilities or "killswitch" in abilities:
                    if action.getValue() == "killmenow":
                        break
                    elif action.getValue() == "status":
                        client_socket.send(makeMessage(self.NAME,"SMTG-D Running since: "+str(self.start_time)))
                        client_socket.close()
                        continue
                    else:
                        logging.warning("Action %s is not a valid single ability." % action.getValue())
            else:
                interfaces.append(client_socket)
                Thread(target=self.__irunner, args=(client_socket, action, abilities, identifier)).start()
            
        TCPSock.close()
        self.__killall(interfaces)
        logging.debug("communication-thread is dead")
        
    def __irunner(self, interface, action, abilities, identifier):
        """This method is run via a thread created in __t2. This method handles
        communication between the daemon/plugins and the interface that is 
        connecting to them.
        """
        logging.debug("Interface("+str(identifier)+")-thread started")
        while True:
            try:
                if not action: break
                elif action.getValue() in abilities:
                    if action.getValue() == "status":
                        interface.send(makeMessage("SMTG-D Running since: "+str(self.start_time)+"\n"))
                    else:
                        # TODO: add action response
                        interface.send(makeMessage("dummy-response. sorry commands not functional yet."))
                else:
                    interface.send( INVALID_ACTION )
            except Exception as e:
                logging.error("Interface("+str(identifier)+")-"+str(e))
            action = strToMessage(interface.recv())
        
        # asked to break, thus close interface
        interface.close()
        logging.debug("Interface("+str(identifier)+")-thread closed")

