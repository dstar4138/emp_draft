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
    
    def __init__(self, registry, attachMan):
        #TODO: parse the event list and subscription map. 
        global _theEManager_
        _theEManager_ = self
        self.registry = registry
        self.attachments = attachMan
        
        self.eventmap = {}
        self.subscriptionmap = {}
        self.alarmrefs = {}
        
    
    def loadEvents(self, eventlist):
        for event in eventlist:
            eid = self.registry.loadEvent(event.name, event._getPID())
            
            event.ID = eid
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
        logging.debug("Event(%s) triggered: %s"%(eid,msg))
        for aid in self.subscriptionmap[eid]:
            Thread(target=self.attachments.getAlarmByID(aid).alert, args=[msg,]).start()
        
    def addAlarm(self, ref):
        if hasattr(ref, "ID"):
            self.alarmrefs[ref.ID] = ref
            logging.debug("Added alarm '%s' to EventManager"%ref.ID)
        else: logging.error("ALARM WASN'T REGISTERED BEFORE LOADING IN EVENT MANAGER!!")
        