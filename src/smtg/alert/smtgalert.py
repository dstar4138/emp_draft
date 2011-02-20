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
    
    def __init__(self, conf, name):
        """ Create the foundation of an alert with a dictionary of internal 
        variables, passed to it via the daemon/AlertManager.
        """
        SmtgPlugin.__init__(self, conf, name)
    
    def _handle_msg(self, msg):
        """ Inherited from Routee, this is what runs when the Plug-in gets
        a message from somewhere.
        """
        raise NotImplementedError("_handle_msg() not implemented")
    
    
    def _alert(self, args):
        """ Runs the alert process. This is the core of an alert. """
        raise NotImplementedError("_alert() not implemented")