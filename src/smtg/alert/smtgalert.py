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

from smtg.plugin.smtgplugin import SmtgPlugin

class Alerter(SmtgPlugin):
    """This is the base method of alerting. """
    
    def __init__(self, conf):
        """ Create the foundation of an alert with a dictionary of internal 
        variables, passed to it via the daemon/AlertManager.
        """
        SmtgPlugin.__init__(self, conf)
    
    def _alert(self, args):
        """ Runs the alert process. This is the core of an alert. """
        raise NotImplementedError("_alert() not implemented")
    
    def _handle_msg(self, msg):
        """ Inherited from Routee, this is what runs when the Plug-in gets
        a message from somewhere.
        """
        raise NotImplementedError("_handle_msg() not implemented")
    
    def _check_status(self):
        """Checks the status of the plug-in. This may mean to check if a 
        web-site is down, or if the connection is lost. Should return a 
        boolean. True means that the plug-in means that it is running,
        False if otherwise. 
        """
        raise NotImplementedError("_check_status() not implemented")  
        
    def _get_commands(self):
        """Returns a dict object of the commands, the name to the description.
        This is used by SMTG to update its help screen, it can also be asked
        for by sending a command to the daemon for all possible commands.
        """
        raise NotImplementedError("_get_commands() not implemented")

    def _save(self):
        """ When closing, SMTG will grab SmtgPlugin.config and push it back 
        to the user's configuration file. So before that point it will call 
        this function so the plug-in/alerter can wrap things up and save what
        it needs to in the self.config variable.
        """
        pass