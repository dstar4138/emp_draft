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
__version__="0.5"


from yapsy.IPlugin import IPlugin

# Importance changes its location in the list of updates.
#   Higher the importance means the sooner it updates when
#   its their time.
LOW_IMPORTANCE  = 0
MID_IMPORTANCE  = 1
HIGH_IMPORTANCE = 2


class SmtgPlugin(IPlugin):
    """The base of all plug-ins for the SMTG platform. Please do not use
    this as your interface. Use either FeedPlugin, or AlertPlugin as your
    interface for your new plug-in since SMTG separates it's internals
    based on those. In ALL plug-ins you must override any method with a
    '_' in front of it. Such as the ones listed below.
    """
    def __init__(self):
        IPlugin.__init__(self)
        
    def _check_status(self):
        """Checks the status of the plug-in. This may mean to check if a 
        web-site is down, or if the connection is lost. Either way this 
        method, returns a string.
        """
        raise NotImplementedError("_check_status() not implemented")  
        
    def _get_commands(self):
        """Returns a JSON object of the commands, their descriptions, any
        arguments that the commands require, and some more. Please check the
        SMTG Plugin API.
        """
        raise NotImplementedError("_get_commands() not implemented")

    def _run_command(self, msg):
        """Runs one or more of the commands from the _get_commands() method.
        The message object passed to this method is a JSON object. Please
        check the SMTG Plugin API. 
        """
        raise NotImplementedError("_run_command() not implemented")
    


class FeedPlugin(SmtgPlugin):
    """Of the two arch-types of plug-ins this is the most commonly used.
    The FeedPlugin is a plug-in who pulls or pushes its information to a 
    feed at a regular interval. Used for RSS, blogs, and slowly updated 
    page alerts, or even internal log scans on your own computer. These
    plug-ins don't require special attention from the Daemon other than
    knowing the feed's update frequency and its importance (both 
    preferably user-set). 
    """
    
    def __init__(self, importance=MID_IMPORTANCE):
        SmtgPlugin.__init__(self)
        self.update_importance=importance

    def change_importance(self, importance):
        if importance <= HIGH_IMPORTANCE or importance >= LOW_IMPORTANCE:  
            self.update_importance = importance
       
    def _update(self, args=[]):
        """This is the method that gets run every pull loop. Any updating
        processes that need to get done, need to get run in this method.
        """
        raise NotImplementedError("_update() not implemented") 

            
class AlertPlugin(SmtgPlugin):
    """The AlertPlugin type waits for a message rather than pulling on 
    an interval like the FeedPlugin. These are necessary for high 
    'importance' items, such as for alert systems such as un-authorized 
    room entrance system or even a simplistic chat system.
    
    Please use this method of plug-ins sparingly. Since it creates its
    own thread, it adds more work on the clients computer than needed.
    If you NEED this method for your plug-in, at least make it benign
    until it's hand-launched by the user. To do this: set auto_start
    to False.
    """
    
    def __init__(self,auto_start=True):
        SmtgPlugin.__init__(self)
        self.start=auto_start


    def _run(self,args=[]):
        """Alert Plug-ins get their own threads! This is the method that
        gets run when the plug-in is loaded into the daemon. When this 
        method returns the Plug-in is put into a waiting area until 
        hand-triggered.
        """
        raise NotImplementedError("_run() not implemented")


    def _comm(self):
        """If ever the Alert plug-in needs to send an alert this method 
        returns the port number for the DaemonClientSocket or standard socket
        to connect on.
        """
        raise NotImplementedError("_comm() not implemented")



