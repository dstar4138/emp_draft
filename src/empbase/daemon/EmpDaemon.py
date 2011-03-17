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


__version__ = "0.7.1"
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
from socket import timeout
from threading import Thread


from empbase.comm.interface import Interface
from empbase.registration.registry import Registry
from empbase.attach.management import AttachmentManager
from empbase.config.logger import setup_logging
from empbase.config.empconfigparser import EmpConfigParser

from empbase.daemon.RDaemon import RDaemon
from empbase.daemon.daemonipc import DaemonServerSocket
from empbase.comm.routing import MessageRouter
from empbase.comm.messages import makeErrorMsg, makeCommandMsg,  \
                                      makeMsg, strToMessage, COMMAND_MSG_TYPE,  \
                                      ERROR_MSG_TYPE 

def checkEmpStatus():#XXX: Violates config vars...
    """ Checks whether the SmtgDaemon is currently running or not."""
    import os
    import empbase.config.defaults as empconf
    return os.path.exists(empconf.default_configs["Daemon"]["pid-file"])



class EmpDaemon(RDaemon):
    """ The Daemon for SMTG, all communication to this daemon goes through smtgd.py
    or the comm port via a DaemonClientSocket. To connect, get the port number and
    then connect either with a regular UDP-8 encoded TCP socket or the 
    DaemonClientSocket.

    The daemon handles the feed and connection loops along with all configuration
    validation. It does not handle interface registration, which should be done 
    through the registration steps handled by smtgd.py. Please look there if you
    want to know how to register your interface with the local smtg daemon.
    """
    
    def __init__(self, configfile=None, dprg="empd.py"):
        """Load the configuration files, create the CommRouter, and then create 
        the daemon. 
        """
        # get yourself a timer!
        self.start_time=time.time() 
        self.fm_start_time = time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime(self.start_time))

        # presets!
        self.registry = None #Registry object!!
        self.aman     = None #AttachmentManager
        self.router   = None #message router

        # now set up the internal configuration via a config file.
        self.config=EmpConfigParser(configfile)
        self.config.validateInternals()
        setup_logging(self.config)

        # adjust by the configurations....
        RDaemon.__init__(self, self.config.get("Daemon", "pid-file"),
                              pchannel=self.config.getint("Daemon", "port"),
                              dprog=dprg,
                              dargs=configfile)
         
    def startup(self):     
        if self.config.getboolean("Daemon", "boot-launch"):
            RDaemon.start(self)
         
         
    def stop(self):
        """ Stops the daemon but then waits a while to make sure all the threads are done. """
        try: 
            RDaemon.stop(self)
            time.sleep(3)#dont worry about the magic number
        except: pass
         
    def restart(self):
        """ Restarts the daemon by killing both threads, and making sure their
        both down before trying to run the daemon again.
        """
        try:
            self.stop()
            time.sleep(2)#dont worry about the magic number
        except:pass
        self.start()

    
    def handle_msg(self, msg):#FIXME: OMG EVERYTHING IS BROKEN
        """ Handles the incoming messages passed to it from the CommReader. """
        logging.debug("daemon received: %s" % msg)
        action = strToMessage(msg)
        if action is None:pass # the action is invalid, just skip
        elif action.getType() == COMMAND_MSG_TYPE:
            logging.debug("Daemon trying to run command now.")
            source = self.ID # this can either be self.ID or None since its the daemon.
            dest = action.getSource() # the destination is the person we got the msg from
            if action.getValue() == "status":
                routing.sendMsg(makeMsg("SMTG-D Running since: "+self.fm_start_time,source,dest))
            elif action.getValue() == "cmds":
                routing.sendMsg(makeMsg(["status","plugins","cmds","attachments", "activate","deactivate",
                                         "alarms","plugid","alertid","var","cvar","help"],
                                source,dest))
            elif action.getValue() == "plugins":
                routing.sendMsg(makeMsg(self.aman.getAllNames(),source,dest))
            elif action.getValue() == "plugins":
                routing.sendMsg(makeMsg(self.aman.getPlugNames(),source,dest))
            elif action.getValue() == "alarms":
                routing.sendMsg(makeMsg(self.aman.getAlarmNames(),source,dest))
            elif action.getValue() == "id":
                try:
                    result = self.aman.getAttachmentID(action.get("args")[0])
                    if result is not None:
                        routing.sendMsg(makeErrorMsg("name does not exist.",None,dest))
                    else:routing.sendMsg(makeMsg(result,source,dest))
                except:
                    routing.sendMsg(makeErrorMsg("id needs an argument.",None,dest))
            elif action.getValue() == "idsearch": notimplemented(dest) #TODO: implement idsearch command to search for an id
            elif action.getValue() == "var":notimplemented(dest) #TODO: implement var command to get internal variables
            elif action.getValue() == "cvar":notimplemented(dest) #TODO: implement cvar to change variables
            elif action.getValue() == "help": 
                self.__help(dest, msg.get("args"))
            
            elif action.getValue() == "activate":
                notimplemented(dest) #TODO: implement activate command to activate inactive plugins/alerters
            elif action.getValue() == "deactivate":
                notimplemented(dest) #TODO: implement deactivate command to deactivate active plugins/alerters
            # the command does not exist.
            else: routing.sendMsg(makeErrorMsg("invalid action",source,dest))
        elif action.getType() == ERROR_MSG_TYPE:
            # the daemon will log your error for you!
            logging.error("error from %s: %s" % (action.getSource(), action.getValue()))
        # the message is invalid, send the error back.
        else: routing.sendMsg(makeErrorMsg("invalid message", None, action.getSource()))
  
  
    def __help(self, dest, args):#FIXME: OMG EVERYTHING IS BROKEN
        """ Generates a dictionary for you to print out for a help screen. As arguments
        to this function, you can have:
            - blank : this will cause the daemon to print out a help screen just for 
                    the daemon
            - a plug-ins id/name : this will give back a help screen for a given plugin
            - an alerts id/name : this will give back a help screen for a given alerter
            - the word "all" : a complete help screen
        """
        cmds = {"status":"get the daemon status, or the status of a plugin/alert given the id.",
                "plugins": "get a list of plug-ins ids to names.",
                "cmds": "get the daemon command list.",
                "alarms": "get a list of alarms ids to names.",
                "id": "given an attachments name, it will return the ID",
                "idsearch": "returns whether a given id exists",
                "var": "returns all internal variables and their values",
                "cvar": "given a variable name and a value, it will change it to the given value.",
                "help": "returns a help screen for the daemon, alerters, or a plugin, or even all of the above."}
        try:
            if len(args) >0:
                if args[0] == "all":
                    all = {"Daemon":cmds}
                    try:
                        for attach in self.aman.getAllPlugins():
                            all[attach.name] = attach.plugin_object.get_commands()
                    except: pass
                    routing.sendMsg(makeMsg(all,None,dest))    
                else: # its a plugin or an alert id.
                    if args[0] == "daemon":
                        routing.sendMsg(makeMsg(cmds, None, dest))
                    elif routing.isRegisteredByID(args[0]):
                        routing.sendMsg(makeMsg(
                                    routing.getReferenceByID(args[0]).get_commands(), args[0], dest))
                    elif routing.isRegisteredByName(args[0]):
                        routing.sendMsg(makeMsg(
                                    routing.getReferenceByName(args[0]).get_commands(), args[0], dest))
                    else:
                        routing.sendMsg(makeErrorMsg("invalid ID or Name",None,dest))
            else:#just the daemon ones.
                routing.sendMsg(makeMsg(cmds,None,dest))
                
        except Exception as e:
            logging.exception(e)
            routing.sendMsg(makeErrorMsg("error getting help", None, dest))
            
  
  
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
            self.registry = Registry(self.config.getRegistryFile())
            self.router   = MessageRouter(self.registry)
            
            # load the plug-in manager now and search for the plug-ins.
            self.aman = AttachmentManager(self.config.getAttachmentDirs(), 
                                          self.config,
                                          self.router,
                                          self.registry)
            self.aman.collectPlugins()
            
            #activates the attachments based on user cfg file. 
            # if the attachment was a SignalPlugin, it will throw the plug-ins
            # run() function into a new thread.
            self.aman.activateAttachments()
    
            # starts the comm router running to send messages!!
            Thread(target=self.router.startRouter,
                   kwargs={"triggermethod":self.isRunning}).start()
            
            # start the interface thread
            Thread(target=self.__t2).start()
    
            # start the pull loop.
            logging.debug("pull-thread started")
            while self.isRunning():
                
                # get all active loop plug-ins
                activePlugins = self.aman.getLoopPlugs()
                if activePlugins:
                    for plugin in activePlugins:
                        if plugin.plugin_object.is_activated:
                            # for each active feed run the update function with no
                            # arguments. The only time arguments are needed 
                            # is if the plug-in was force updated by a command.
                            logging.debug("pulling LoopPlugin: %s" % plugin.name)
                            try: plugin.plugin_object.update()
                            except Exception as e:
                                logging.error("%s failed to update: %s" % (plugin.name, e))    
                
                try: # sleep, and every five seconds check if still alive
                    count=0
                    sleep_time = self.config.getfloat("Daemon","update-speed") * 60.0
                    while(count<sleep_time):
                        count+=5
                        time.sleep(5)#every 5 seconds check state
                        if not self.isRunning(): break;
                except: pass
                
            #Stop all signal threads
            for signal in self.aman.getSignalPlugs():
                signal.plugin_object.deactivate()    
            
            #flush the router, and save all configurations.
            self.router.flush()
            self.config.save( self.aman.getAllPlugins() )
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
        whitelist = str(self.config.get("Daemon", "whitelisted-ips")).split(",")
        isocket = DaemonServerSocket(port=self.getComPort(),
                                     ip_whitelist=whitelist,
                                     externalBlock=self.config.getboolean("Daemon","local-only"),
                                     allowAll=self.config.getboolean("Daemon", "allow-all"))
        
        while self.isRunning(): # keep listening forever
            try:
                client_socket = isocket.accept()
                logging.debug("incoming message from interface.")
        
                # create an interface out of the socket
                # LATER: authentication can go here, before they connect. (eg logging in)
                interface = Interface(client_socket)
                logging.debug("identifier: %s"% interface.ID)
            
                # since there are abilities that this person can perform throw
                # to new thread by way of the interface class
                self.router.sendMsg(makeCommandMsg("proceed",self.ID, dest=interface.ID))
                Thread(target=interface.receiver).start()
                logging.debug("pushed interface to new thread.")
            except timeout:pass #catches a timeout and allows for daemon status checking
            except Exception as e: logging.exception(e)
        isocket.close()
        logging.debug("communication-thread is dead")

