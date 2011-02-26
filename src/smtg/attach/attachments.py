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

#
# These are the interfaces that all plug-ins will need to implement. if
#  you want to write the plug-in in a different language you will need
#  to still use one of the interfaces, but you can very easily extend
#  your program. Please consult this page for more information:
#    http://wiki.python.org/moin/IntegratingPythonWithOtherLanguages
#
__version__="0.8"

from threading import Thread
from yapsy.IPlugin import IPlugin
from smtg.comm.routing import Routee

# Importance changes its location in the list of updates.
#   The lower the number the closer to the beginning it is. You can
# get fancy with the importance levels, or just use one of the ones
# provided. 
LOW_IMPORTANCE  = 100
MID_IMPORTANCE  = 50
HIGH_IMPORTANCE = 0

class SmtgPlugin(IPlugin, Routee):
    """The base of all plug-ins for the SMTG platform. Please do not use
    this as your interface. Use either LoopPlugin, or SignalPlugin as your
    interface for your new plug-in since SMTG separates it's internals
    based on those.
    """
    def __init__(self, conf):
        self.config = conf
        IPlugin.__init__(self)
        self.makeactive = self.config.getboolean("makeactive",True)
        
    def handle_msg(self, msg):
        """ Inherited from Routee, this is what runs when the Plug-in gets
        a message from somewhere. This is here just to remind you that you
        NEED to implement it.
        """
        raise NotImplementedError("handle_msg() not implemented") 
        
    def get_commands(self):
        """Returns a dict object of the commands, the name to the description.
        This is used by SMTG to update its help screen, it can also be asked
        for by sending a command to the daemon for all possible commands.
        """
        raise NotImplementedError("get_commands() not implemented")

    def save(self):
        """ When closing, SMTG will grab SmtgPlugin.config and push it back 
        to the user's configuration file. So before that point it will call 
        this function so the plug-in/alerter can wrap things up and save what
        it needs to in the self.config variable.
        """
        self.config.set("makeactive", self.makeactive)


class LoopPlugin(SmtgPlugin):
    """Of the two arch-types of plug-ins this is the most commonly used.
    The LoopPlugin is a plug-in who pulls information from a source on 
    a regular interval. The importance of the LoopPlugin decides when it
    gets to be pulled in the list of other LoopPlugins.
    """
    def __init__(self, conf, importance=MID_IMPORTANCE):
        SmtgPlugin.__init__(self, conf)
        self.update_importance=self.config.getint("importance",importance)

    def change_importance(self, importance):
        if importance <= HIGH_IMPORTANCE and importance >= LOW_IMPORTANCE:  
            self.update_importance = importance
       
    def update(self, *args):
        """This is the method that gets run every pull loop. Any updating
        processes that need to get done, need to get run in this method.
        """
        raise NotImplementedError("update() not implemented") 


class SignalPlugin(SmtgPlugin): 
    """The SignalPlugin type waits for a message rather than pulling on 
    an interval like the LoopPlugin. These are necessary for high 
    'importance' items, such as for alert systems such as un-authorized 
    room entrance system or even a simplistic chat system.
    
    Please use this method of plug-ins sparingly. Since it creates its
    own thread, it adds more work on the clients computer than needed.
    If you NEED this method for your plug-in, at least make it benign
    until it's hand-launched by the user. 
    """
    def __init__(self, conf, autostart=None):
        SmtgPlugin.__init__(self, conf)
        if autostart is not None and autostart:
            self.makeactive = autostart
    
    def activate(self):
        """ When the SignalPlugins are activated, they throw the run function
        into a new thread.
        """
        if not self.is_activated:
            self.is_activated = True
            Thread(target=self.run).start()
    
    def run(self):
        """Signal Plug-ins get their own threads! This is the function that 
        needs to be overwritten by the subclass.
        """
        raise NotImplementedError("run() not implemented")


class Alerter(SmtgPlugin):
    """This is the base method of alerting. """
    
    def __init__(self, conf):
        """ Create the foundation of an alert with a dictionary of internal 
        variables, passed to it via the daemon/AlertManager.
        """
        SmtgPlugin.__init__(self, conf)
    
    def alert(self, *args):
        """ Runs the alert process. This is the core of an alert. """
        raise NotImplementedError("alert() not implemented")
    