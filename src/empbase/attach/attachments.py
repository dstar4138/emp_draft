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
__version__="0.9.2"

from threading import Thread
from yapsy.IPlugin import IPlugin

# Importance changes its location in the list of updates.
#   The lower the number the closer to the beginning it is. You can
#   get fancy with the importance levels, or just use one of the ones
#   provided. 
LOW_IMPORTANCE  = 0
MID_IMPORTANCE  = 50
HIGH_IMPORTANCE = 100


class EmpAttachment(IPlugin):
    """ The base of all plugs and alarms for the EMP platform. Please do not 
    use this as your interface. Use either LoopPlug, or SignalPlug as your
    interface for your new plug-in since EMP separates it's internals
    based on those. Or if you are building a new Alarm use EmpAlarm.
    """
    def __init__(self, config):
        self.ID = ''
        self.config = config
        IPlugin.__init__(self)
        self.makeactive = self.config.getboolean("makeactive",True) 

    def deactivate(self):
        IPlugin.deactivate(self)
        self.save()
        
    def get_commands(self):
        """ Returns a list object of the Command objs that the attachment has
        made triggers for. This is used by EMP to update its help screen, as
        well as the messaging router to speed up command protocols. 
        """
        raise NotImplementedError("get_commands() not implemented")

    def save(self):
        """ When closing, EMP will grab EmpAttachment.config and push it back 
        to the user's configuration file. So before that point it will call 
        this function so the plug-in/alerter can wrap things up and save what
        it needs to in the self.config variable. When the attachment is 
        deactivated the save method will also be called.
        """
        self.config.set("makeactive", self.makeactive)


class EmpPlug(EmpAttachment):
    def __init__(self, config):
        EmpAttachment.__init__(self, config)
        
    def get_events(self):
        """ This is the list of Event objects that the Plug can cause. Each
        Event will be registered with the EventManager and the daemon, so that
        Alarms can subscribe to them. You as a plug don't have to worry about 
        this, just that you trigger the event's the correct way. See the Event
        object description. 
        """
        raise NotImplementedError("get_events() not implemented")


class EmpAlarm(EmpAttachment):
    """This is the base method of alerting. """
    
    def __init__(self, config):
        """ Create the foundation of an alert with a dictionary of internal 
        variables, passed to it via the daemon/AttachmentManager.
        """
        EmpAttachment.__init__(self, config)
    
    def get_alerts(self):
        """ Gets the possible alerts with this Alarm!"""
        raise NotImplementedError("get_alerts() not implemented")
    

class LoopPlug(EmpPlug):
    """Of the two arch-types of plugs this is the most commonly used.
    The LoopPlug is a plug-in who pulls information from a source on 
    a regular interval. The importance of the LoopPlugin decides when it
    gets to be pulled in the list of other LoopPlugins.
    """
    def __init__(self, config, importance=MID_IMPORTANCE):
        EmpPlug.__init__(self, config)
        self.update_importance=self.config.getint("importance",importance)

    def change_importance(self, importance):
        if importance <= HIGH_IMPORTANCE and importance >= LOW_IMPORTANCE:  
            self.update_importance = importance
       
    def update(self, *args):
        """This is the method that gets run every pull loop. Any updating
        processes that need to get done, need to get run in this method.
        """
        raise NotImplementedError("update() not implemented") 


class SignalPlug(EmpPlug): 
    """The SignalPlug type waits for a message rather than pulling on 
    an interval like the LoopPlug. These are necessary for high 
    'importance' items, such as for alert systems such as un-authorized 
    room entrance system or even a simplistic chat system.
    
    Please use this method of plug-ins sparingly. Since it creates its
    own thread, it adds more work on the clients computer than needed.
    If you NEED this method for your plug-in, at least make it benign
    until it's hand-launched by the user. 
    """
    def __init__(self, config, autostart=None):
        EmpAttachment.__init__(self, config)
        if autostart is not None and autostart:
            self.makeactive = autostart
    
    def activate(self):
        """ When the SignalPlugins are activated, they throw the run function
        into a new thread. This makes self.is_activated equal True. Make sure
        your run function knows when to quit (eg when is_activated == False).
        """
        if not self.is_activated:
            self.is_activated = True
            Thread(target=self.run).start()
    
    def run(self):
        """Signal Plug-ins get their own threads! This is the function that 
        needs to be overwritten by the subclass.
        """
        raise NotImplementedError("run() not implemented")
