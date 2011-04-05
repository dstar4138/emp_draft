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
import time
import queue
import random
import logging
from threading import Thread
from empbase.event.eventhistory import EventHistory

UNKNOWN = "<UNKNOWNOMGS>"

def triggerEvent(eid):
    """ Handles contacting the EventManager and running all the subscribers
    quickly so the Event doesn't see any slow-down.
    """    
    if _theEManager_ is not None:
        Thread(target=_theEManager_.triggerEvent, args=[eid,]).start()
    else: # or eid == UNKNOWN
        logging.debug("Event(%s) was triggered before EM was initialized." % eid)


def detriggerEvent(eid):    
    """ Handles contacting the EventManager and removing an event from the 
    queue of things to trigger, or list of currently triggered events.
    """    
    if _theEManager_ is not None:
        Thread(target=_theEManager_.detriggerEvent, args=[eid,]).start()
    else: # or eid == UNKNOWN
        logging.debug("Event(%s) was triggered before EM was initialized." % eid)
     
     
     
def registerEvent(event):
    """ Can be used for dynamic runtime creation of Events. Shouldn't throw the 
    loading into a new thread because we don't want accidental race conditions. 
    """
    if _theEManager_ is not None:
        _theEManager_.loadEvent(event)
    else:
        logging.debug("Event tried to be registered before EM was initialized." )
     
def deregisterEvent(event):
    """ Can be used for dynamic runtime destruction of Events. Shouldn't throw  
    the loading into a new thread because we don't want accidental race 
    conditions. 
    """
    if _theEManager_ is not None:
        _theEManager_.unloadEvent(event)
    else:
        logging.debug("Event tried to be deregistered before EM was initialized." )
     
def registerAlert(alert):
    """ Can be used for dynamic runtime creation of Alerts. Shouldn't throw the 
    loading into a new thread because we don't want accidental race conditions. 
    """
    if _theEManager_ is not None:
        _theEManager_.loadAlert(alert)
    else:
        logging.debug("Alert tried to be registered before EM was initialized." )
     
def deregisterAlert(alert):
    """ Can be used for dynamic runtime destruction of Alerts. Shouldn't throw  
    the loading into a new thread because we don't want accidental race 
    conditions. 
    """
    if _theEManager_ is not None:
        _theEManager_.unloadAlert(alert)
    else:
        logging.debug("Alert tried to be deregistered before EM was initialized." )
     

        
        
""" The event manager is a singleton, this is it."""
_theEManager_ = None
MIN_SLEEP = 0.0
MAX_SLEEP = 0.05  #will need testing, might need to be lower to seem instant!

class EventManager():
    """ """
    
    def __init__(self, config, registry, trigger):
        global _theEManager_
        _theEManager_ = self
        self.eventqueue = []
        self.triggered  = []
        self.history = EventHistory(config)
    
        self.registry = registry
        self.trigger = trigger
        
        self.eventmap = {} #eid -> ref
        self.alertmap = {} #lid -> ref
        if self.trigger():
            #Thread(target=self.watchList).start() #FIXME: un-comment when ready!
            Thread(target=self.watchQueue).start()
    
    def getInstance(self):
        """Returns the EventManager, make sure it was initialized first."""
        return _theEManager_        
    
    def loadEvent(self, event):
        eid = self.registry.loadEvent(event.name, event._getPID())
        event.ID = eid
        self.eventmap[eid] = event
    
    def loadEvents(self, eventlist):
        for event in eventlist:
            eid = self.registry.loadEvent(event.name, event._getPID())
            event.ID = eid
            self.eventmap[eid] = event
            
    def unloadEvent(self, event):
        if self.registry.unloadEvent(event.ID):
            if self.eventmap.pop(event.ID):
                event.ID = UNKNOWN
                return True
        return False
        
            
    def loadAlert(self, alert):
        lid = self.registry.loadEvent(alert.name, alert.aid)
        alert.ID = lid
        self.alertmap[lid] = alert
            
    def loadAlerts(self, alertlist):
        for alert in alertlist:
            lid = self.registry.loadEvent(alert.name, alert.aid)
            alert.ID = lid
            self.alertmap[lid] = alert
    
    def unloadAlert(self, alert):
        if self.registry.unloadAlert(alert.ID):
            if self.alertmap.pop(alert.ID):
                alert.ID = UNKNOWN
                return True
        return False
    
    def triggerEvent(self, eid):
        self.eventqueue.append(eid)
        self.history.triggered(eid)
        logging.debug("Event(%s) triggered!"%eid)
        
    def detriggerEvent(self, eid):
        if not self.eventqueue.pop(eid):
            try: self.triggered.remove(eid)
            except: pass
    
    
#### THE FOLLOWING NEEDS TO BE REALLY FRIGGIN FAST! ####    
    def runsubscribers(self, eventobj, lids):
        """ Throws all the alert's run methods into threads to signal 
        the event. 
        """
        logging.debug("running subscribers") #XXX: remove me
        for lid in lids:
            try: Thread(target=self.alertmap[lid].run, args=(eventobj,)).start()
            except Exception as e: logging.error(e)
        logging.debug("running subscribers dead") #XXX: remove me
    
    
    def watchQueue(self):
        """ Watches the queue and if there is an event in there, runs all of 
        the subscribers as quickly as possible. If there is a 
        """
        logging.debug("EventQueue watcher thread started")
        while self.trigger():
            try:
                if len(self.eventqueue) == 0: raise queue.Empty
                
                id = self.eventqueue.pop()
                Thread(target=self.runsubscribers, 
                       args=(self.eventmap[id],
                             self.registry.subscribedTo(id),)).start()
                if self.eventmap[id].halflife > 0: 
                    self.triggered.append(self.eventmap[id]) #TODO: pull out the counter?
                
            except queue.Empty: pass
            except Exception as e: logging.exception(e)
                        
            if len(self.eventqueue) != 0: continue
            # sleep for a very small amount
            try: time.sleep(random.uniform(MIN_SLEEP, MAX_SLEEP))
            except: pass
        logging.debug("EventQueue watcher thread dead")    
    
    def watchList(self):
        """ Watches the list and removes halflifes from all the events! """
        logging.debug("Event list watcher thread started")
        while self.trigger():
            #TODO: every loop through remove a counter 
        
            
            try: time.sleep(1) #FIXME: sleep time adjusts for how long it took to get around loop.
            except: pass
        logging.debug("Event list watcher thread dead")
    
    