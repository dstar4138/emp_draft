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

__version__="pre-alpha..."
__description__ = """
The EMP-Daemon is responsible for alerts, updates and other plug-in
communications. However, any interaction should go through smtg rather
than empd. This is so logging and proper error handling can be
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
from empbase.event.eventmanager import EventManager
from empbase.attach.management import AttachmentManager
from empbase.config.logger import setup_logging
from empbase.comm.command import Command, CommandList
from empbase.config.empconfigparser import EmpConfigParser

from empbase.daemon.RDaemon import RDaemon
from empbase.daemon.daemonipc import DaemonServerSocket
from empbase.comm.routing import MessageRouter
from empbase.comm.messages import makeCommandMsg

def notimplemented(*args):
    raise Exception("This command has not be implemented yet, sorry!")

def parsesubs(substr):
    """ Parses the subscription strings."""
    tmp = substr.split(".")
    if len(tmp) >= 2:
        return tmp[0],tmp[1],tmp[1:]
    elif len(tmp) == 1:
        return tmp[0], None, []
    else: return substr, None, []
         

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
        """ Startup the daemon if there is a variable called boot-launch and 
        it's True.
        """
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

    
    def get_commands(self):
        if not hasattr(self, "_commands"):
            self.__setup_commands()
            
        return self._commands
    
    def __setup_commands(self):
        """ Sets up the daemon's commands. """
        self._commands = [Command("var",    trigger=self.__cmd_var, help="returns all internal variables and their values"),
                          Command("cvar",   trigger=self.__cmd_cvar, help="given a variable name and a value, it will change it to the given value."),
                          Command("trigger",trigger=self.__cmd_trigger, help="hand trigger an event given an id or event string"),
                          Command("status", trigger=self.__cmd_status, help="get the daemon status, or the status of a plugin/alert given the id."),
                          Command("events", trigger=self.__cmd_events, help="get a list of all the events that a given plug has"),
                          Command("alerts", trigger=self.__cmd_alerts, help="get a list of all the alerts that a given alarm has"),
                          Command("plugs",  trigger=self.__cmd_plugs, help="get a list of plug-ins ids to names."),
                          Command("cmds",   trigger=self.__cmd_cmds, help="get the daemon command list."),
                          Command("alarms", trigger=self.__cmd_alarms, help="get a list of alarms ids to names."),
                          Command("id",     trigger=self.__cmd_id, help="given an attachments name, it will return the ID"),
                          Command("idsearch",      trigger=self.__cmd_idsearch, help="returns whether a given id or name exists, returns a boolean"),
                          Command("curtriggered",  trigger=self.__cmd_curtriggered, help="the currently triggered events"),
                          Command("attachments",   trigger=self.__cmd_attachments, help="get a list of all attachments"),
                          Command("help",          trigger=self.__cmd_help, help="returns a help screen for the daemon, alerters, or a plug, or even all of the above."),
                          Command("activate",      trigger=self.__cmd_activate, help="activates an attachment given an id or target name"),
                          Command("deactivate",    trigger=self.__cmd_deactivate, help="deactivates an attachment given an id or target name"),
                          Command("subscribe",     trigger=self.__cmd_subscribe, help="subscribes a given alarm name/id to a given plug-in name/id or event id."),
                          Command("subscriptions", trigger=self.__cmd_subscriptions, help="get a list of target subscriptions"),
                          Command("unsubscribe",   trigger=self.__cmd_unsubscribe, help="unsubscribes a given alarm name/id to a given plug-in name/id or event id.")]


    def __cmd_status(self, *args):
        return "SMTG-D Running since: "+self.fm_start_time
    
    def __cmd_cmds(self, *args):
        cmdlst = CommandList(self.get_commands())
        return cmdlst.getNames()
    
    def __cmd_plugs(self, *args): 
        return self.aman.getPlugNames()
    
    def __cmd_alarms(self, *args):
        return self.aman.getAlarmNames()
    
    def __cmd_id(self, *args): 
        if len(args) > 0:
            return self.registry.getAttachId(args[0])
        else: raise Exception("Id command needs a target name.")
        
    def __cmd_idsearch(self, *args):
        if len(args) > 0:
            return self.registry.isRegistered(args[0])
        else: 
            raise Exception("idsearch command needs a target name or id.")
        
    def __cmd_var(self, *args):
        vars = {}
        for var in self.config.options("Daemon"):
            vars[var] = self.config.get("Daemon", var)
        for var in self.config.options("Logging"):
            vars[var] = self.config.get("Logging", var)
        return vars
    
    def __cmd_activate(self, *args):
        if len(args) > 0:
            attach = self.aman.getAttachment(args[0])
            if attach is None: raise Exception("Target name or id does not exist.")
            if attach.is_activated: raise Exception("Target already active!")
            attach.activate()
            return "Activated"
        else: raise Exception("activate command needs a target name or id.") 
    def __cmd_deactivate(self, *args):
        if len(args) > 0:
            attach = self.aman.getAttachment(args[0])
            if attach is None: raise Exception("Target name or id does not exist.")
            if not attach.is_activated: raise Exception("Target already inactive!")
            attach.deactivate()
            return "De-activated"
        else: raise Exception("deactivate command needs a target name or id.")
        
        
    def __cmd_subscribe(self, *args): return notimplemented()
    def __cmd_subscriptions(self, *args): return notimplemented()
    def __cmd_unsubscribe(self, *args): return notimplemented()
        
        
    def __cmd_trigger(self, *args): return notimplemented()
    def __cmd_cvar(self, *args): return notimplemented()        
    def __cmd_events(self, *args): return notimplemented()
    def __cmd_alerts(self, *args): return notimplemented()
    def __cmd_curtriggered(self, *args): return notimplemented()
    def __cmd_attachments(self, *args): return notimplemented()
                
    def __cmd_help(self, *args):
        if len(args) <= 0: #cant be less but i like being complete.
            cmds = CommandList(self.get_commands())
            return cmds.getHelpDict()
        else:
            if args[0] == "all":
                cmds = CommandList(self.get_commands())
                all = {"Daemon":cmds.getHelpDict()}
                try:
                    for attach in self.aman.getAllPlugins():
                        cmds = CommandList(attach.plugin_object.get_commands())
                        all[attach.name] = cmds.getHelpDict()
                except:pass
                return all
            else: # its a plug or an alert id.
                if args[0] == "daemon":
                    cmds = CommandList(self.get_commands())
                    return cmds.getHelpDict()
                elif self.registry.isRegistered(args[0]):
                    attach = self.aman.getAttachment(args[0])
                    if attach is None: raise Exception("Could not get target's commands.")
                    cmds = CommandList(attach.get_commands())
                    return cmds.getHelpDict()
                else:
                    raise Exception("Invalid target")
                    
  
    def _run(self):
        """ 
            Here is a quick outline of what each of the three threads are and 
        do, for a more in-depth look, look at the consecutive method calls:
        
            - Thread 1: the current one, this is the pull loop. It updates the
                LoopPlugins every time interval. This time interval is set by 
                the configuration file.
                
            - Thread 2: this is the MessageRouter.startRouter() method. It 
                handles all inter-thread communication. See CommReader for 
                more info.
                
            - Thread 3: this is _t2(), it handles incoming communication to the
                port that the SmtgDaemon listens to for Interfaces. See the
                interface API for more information on how to talk to the 
                daemon. 
        """
        try:
            # Load the registry from last time if it exists
            self.registry = Registry(self.config.getRegistryFile())
            self.ID       = self.registry.daemonId() 
            
            # load the attachment manager now and search for the user's 
            # attachments. It will only load them if they pass inspection.
            self.aman = AttachmentManager( self.config, 
                                           self.registry,
                                           EventManager(self.config, 
                                                        self.registry, 
                                                        self.isRunning))
            self.aman.collectPlugins()
            
            # Set up the router using the loaded registry
            self.router   = MessageRouter(self.registry, 
                                          self, self.aman)
            
            #activates the attachments based on user cfg file. 
            # if the attachment was a SignalPlugin, it will throw the plug's
            # run() function into a new thread.
            self.aman.activateAttachments()
    
            # starts the comm router running to send messages!!
            Thread(target=self.router.startRouter,
                   kwargs={"triggermethod":self.isRunning}).start()
            
            # start the interface server thread
            Thread(target=self.__t2).start()
    
            # start the pull loop.
            logging.debug("pull-loop thread started")
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
            self.registry.save()
            logging.debug("pull-loop thread is dead")

        except Exception as e:
            logging.error("Pull-loop thread was killed by: %s" % str(e))
            logging.exception(e)
        
            
    def __t2(self):
        """ Interface Server method, this runs in a new thread when the 
        daemon starts. See _run() method for more information.
        """
        
        logging.debug("communication-thread started")
        # Create socket and bind to address
        whitelist = self.config.getlist("Daemon", "whitelisted-ips")
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
                interface = Interface(self.router, client_socket)
                self.registry.registerInterface(interface) #gives the interface its ID
                self.router.addInterface(interface)
            
                # since there are abilities that this person can perform throw
                # to new thread by way of the interface class
                self.router.sendMsg(makeCommandMsg("proceed", self.ID, dest=interface.ID))
                Thread(target=interface.receiver).start()
            except timeout:pass #catches a timeout and allows for daemon status checking
            except Exception as e: logging.exception(e)
        isocket.close()
        logging.debug("communication-thread is dead")

