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
from empbase.event.eventmanager import registerAlert, deregisterAlert

UNKNOWN = "<UNKNOWNOMGZ>"

class Alert():
    """ """
    def __init__(self, name, aid, description=""):
        self.aid = aid
        self.name = name
        self.description = description
        self.ID = UNKNOWN

    def register(self):
        """ Register this alert with the event manager. You NEED to run this if 
        the alert was created during runtime. Also, make sure you add this alert
        to the list that gets returned when the daemon calls get_alerts().
        """
        registerAlert( self )
    
    def deregister(self):
        """ Removes this alert from the subscription lists and the event 
        manager. You NEED to call this if you are destroying alerts at runtime. 
        Also, make sure you remove it from the list of alerts that get returned
        when the daemon calls get_alerts.
        """
        deregisterAlert( self )
    
    def run(self, eventobj):
        raise NotImplementedError("Alert.run() not implemented")
