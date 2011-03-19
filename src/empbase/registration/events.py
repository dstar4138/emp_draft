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
from xml.etree.ElementTree import Element
from empbase.comm.messages import makeAlertMsg

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

    def toXMLNode(self):
        me = Element("event")
        me.attrib = {"pid": self.pid,
                     "id": self.ID,
                     "name": self.name}
        #TODO: subscriptions!!
        return me

    def __str__(self):
        """ When it wants to turn itself into a string it uses the 
        AlertMessage protocol."""
        return str(makeAlertMsg(self.msg, self.pid, title=self.name))


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
        _theEManager_ = self
        self.registry = registry
        self.attachments = attachMan
        
        self.eventmap = {}
        self.subscriptionmap = {}
        self.alarmrefs = {}
        
    
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
        
    def addAlarm(self, ref):
        if hasattr(ref, "ID"):
            self.alarmrefs[ref.ID] = ref
            logging.debug("Added alarm '%s' to EventManager"%ref.ID)
        else: logging.error("ALARM WASN'T REGISTERED BEFORE LOADING IN EVENT MANAGER!!")
        