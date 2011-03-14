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
import logging
from threading import Thread

#This is the id of an unknown event.
UNKNOWN = "<UNKNOWNOMG>"


class Event():
    """ This is the base type of event that can happen within EMP,
    these are what Alarms subscribe to. These are created and saved
    by Plugs and are used by the EventManager to know who to send to.
    """
    
    def __init__(self, pid, name, msg=""):
        """ All events have a string message that is sent to the alarm,
        the alarm can choose to use it if it wants to.
        """
        self.pid = pid
        self.name = name
        self.msg = msg
        self.ID = UNKNOWN
        
    def register(self, ID):
        """Gives the event its ID. Should only get called by the Event
        Manager.
        """
        self.ID = ID    
    
    def trigger(self, msg=None):
        """This is the method you must call when you want to trigger
        this Event.
        """
        if msg is not None: 
            self.msg = msg
        triggerEvent(self.ID, msg)


def triggerEvent(eid, msg):
    """ Handles contacting the EventManager and running all the subscribers
    quickly so the Event doesn't see any slow-down.
    """    
    if _theEManager_ is not None:
        Thread(target=_theEManager_.runEventSubscribers, args=[eid, msg,]).start()
    else: # or eid == UNKNOWN
        logging.debug("Event(%s) was triggered before EM was initialized." % eid)
        
        
""" The event manager is a singleton, this is it."""
_theEManager_ = None

class EventManager():
    """ """
    
    def __init(self, registry, attachMan):
        #TODO: parse the event list and subscription map. 
        _theEManager_ = self
        self.registry = registry
        self.attachments = attachMan
        
        self.eventmap = {}
        self.subscriptionmap = {}
    
    
    def loadEvents(self, eventlist):
        for event in eventlist:
            eid = self.registry.loadEvent(event.name, event.pid)
            
            event.register(eid)
            self.eventmap[eid] = event
            self.subscriptionmap[eid] = self.registry.subscribedTo(eid)
    
    def getInstance(self):
        """Returns the EventManager, make sure it was initialized first."""
        return _theEManager_
    
    def subscribe(self, aid, eid): 
        self.registry.subscribe(aid, eid)
    
    def unsubscribe(self, aid, eid):
        self.registry.unsubscribe(aid, eid)
    
    def runEventSubscribers(self, eid, msg):
        for aid in self.subscriptionmap[eid]:
            Thread(target=self.attachments.getAlarmByID(aid).alert, args=[msg,]).start()
        
        