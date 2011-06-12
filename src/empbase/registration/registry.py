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
import os
import time
import random
import logging
from string import ascii_lowercase, digits
import xml.etree.ElementTree as ET
from empbase.registration.regobj import RegAttach, RegEvent, RegAlert, \
                                        RegSubscription, PLUG, ALARM, INTERFACE,  \
                                        parseAttribToSub, SubscriptionType
"""
the registry xml structure is like this, it may change
when we want to house more cache related items for the attachments.
Or if the daemon needs to house things in the cache, but for now it
is fairly simple: 

<registry>
    <daemon id=''/>
    <attachments>
        <plug cmd='' id='' module='' />
        <alarm cmd='' id='' module='' />
        ...
    </attachments>
    <events>
        <event pid='' id='' name='' />
        ...
    </events>
    <alerts>
        <alert aid='' id='' name='' />
        ...
    </alerts>
    <subscriptions>
        <sub id='' eid='' lid='' eparent='' lparent=''/>   <--event=alert
        <sub id='' eid='' aid='' eparent=''/>              <--event=all alarm's alerts
        <sub id='' pid='' lid='' lparent=''/>              <--any plug event = alert
        <sub id='' pid='' aid=''/>            <--any plug event = all alarm's alerts
        ...
    </subscriptions>
</registry>
"""

# Size of the IDs generated items in the registry.
AID_SIZE = 5  # attachment ids
EID_SIZE = 10 # event ids
LID_SIZE = 10 # alert ids
SID_SIZE = 15 # subscription ids
ID_LETTERS = digits + ascii_lowercase
# For completeness sake, CID's are either a target's cmd or id. The registry
# will try to figure out which it is.
__WARNING_TEXT__ ="DO NOT EDIT THIS FILE OR ELSE ATTACHMENTS WILL LOOSE THEIR SUBSCRIPTIONS! "+ \
                  "IF YOU WANT TO CHANGE ANY VALUES, USE EMP! "


class Registry():
    """ The registry is EMP's single source of all routing information. That 
    is, what attachments are currently registered, and what subscriptions 
    every alert and event has.
    
    The registry deals only in IDs. It does not have any references for any
    attachment or subscription or alert or event. See the Attachment and 
    Event Managers for that information.  
    """
   
    def __init__(self, filepath):
        """ Sets up a new registry in case the loading fails. If the loading 
        is a success, then the Daemon ID will always be constant and the 
        attachments and events will all keep their ids and command names.
        """
        self._file = filepath
        self._attachments = {}
        self._events      = {}
        self._alerts      = {}
        self._subscriptions = {}
        self._did = self.__genNewAttachId()
        self.load()
        logging.debug("loaded... theres %d attachments"%int(len(self._attachments)))
        
    def load(self): 
        """ Loads the registry list into this Registry object for use in the 
        routing protocol.
        """
        try:
            tree = ET.parse(self._file)
            root = tree.getroot()

            attachments = root.find("attachments")
            for node in attachments.getchildren():
                if node.tag in [ALARM, PLUG]:
                    cmd = node.attrib["cmd"]
                    mod = node.attrib["module"]
                    id  = node.attrib["id"]
                    self._attachments[id] = RegAttach(cmd, mod, id, node.tag)
                
            daemon = root.find("daemon")
            if "id" in daemon.attrib:
                self._did = node.attrib["id"]
                #TODO: verify validity of id
            
            events = root.find("events")
            for node in events.getchildren():
                event = RegEvent( node.attrib["id"],
                                  node.attrib["pid"],
                                  node.attrib["name"] )
                self._events[event.ID] = event

            alerts = root.find("alerts")
            for node in alerts.getchildren():
                alert = RegAlert( node.attrib["id"],
                                  node.attrib["aid"],
                                  node.attrib["name"] )
                self._alerts[alert.ID] = alert
            
            subscriptions = root.find("subscriptions")
            for node in subscriptions.getchildren():
                subscription = parseAttribToSub( node.attrib )
                if subscription is None: continue #couldn't parse
                self._subscriptions[subscription.ID] = subscription
            
        except IOError: pass # no such file? who cares...
        except Exception as e: logging.error(e)
         
    def save(self): 
        """ Saves this Registry to the registry file in the base directory. """
        try:
            root = ET.Element("registry", attrib={"save":str(time.time())})
            root.append(ET.Comment(__WARNING_TEXT__))
            
            # Make sure we have the daemon's ID for next time we load!
            ET.SubElement(root, "daemon", attrib={"id":self._did})
            
            #Add attachments to the registry!
            attachments = ET.Element("attachments")
            for attach in self._attachments.values():
                if attach.type in [PLUG, ALARM]:
                    ET.SubElement(attachments, attach.type, attrib=attach.getAttrib())
            root.append(attachments)
            
            #Add all the events
            events = ET.Element("events")
            for event in self._events.values():
                ET.SubElement(events, "event", attrib=event.getAttrib())
            root.append(events)
            
            #Add all registered alerts
            alerts = ET.Element("alerts")
            for alert in self._alerts.values():
                ET.SubElement(alerts, "alert", attrib=alert.getAttrib())
            root.append(alerts)
            
            #Add all subscriptions
            subscriptions = ET.Element("subscriptions")
            for subscription in self._subscriptions.values():
                ET.SubElement(subscriptions, "sub", attrib=subscription.getAttrib())
            root.append(subscriptions)
            
            # Save everything to the file that we were given on startup.
            logging.debug("Saving registry to %s"%self._file)
            if self.__try_setup_path(self._file):
                self.__makeBackup()
                
                tree = ET.ElementTree(root)
                try: 
                # First try to save via a byte stream, if that doesn't work 
                # utilize the basic string save. which might not work.
                    with open(self._file, "wb") as savefile:
                        tree.write(savefile)
                except:
                    with open(self._file, "w") as savefile:
                        tree.write(savefile)
                # if the second attempt fails it is caught by the function
                # try-catch. Which will restore backups and log the errors.
                logging.debug("Registry Saved!")
                self.__removeBackup()
                return True
            else: return False
        except Exception as e:
            logging.exception(e)
            self.__restoreBackup()
            return False
 
    def __try_setup_path(self,path):
        if os.path.exists(path):
            return os.access(path, os.W_OK)
        else:
            try:
                dirs, _ = os.path.split(path)
                if not os.path.exists(dirs):
                    os.makedirs(os.path.abspath(dirs))
            except: 
                return False
            return True

    def __validSubscription(self, alertAlarm, eventPlug):
        #This looks gross but its faster than calling the parent
        # calls on everything.
        alid, epid = None, None    #used for ids
        alarm, plug = False, False #used for typing
        type = SubscriptionType.Unknown
        for alert in self._alerts.values():
            if alertAlarm == alert.ID:
                alid = alertAlarm
                break
            elif alertAlarm == alert.aid:
                alid = alertAlarm
                alarm = True
                break
            elif eventPlug == alert.ID:
                alid = eventPlug
                break
            elif eventPlug == alert.aid:
                alid = eventPlug
                alarm = True
                break
        for event in self._events.values():
            if alertAlarm == event.ID:
                epid = alertAlarm
                break
            elif alertAlarm == event.pid:
                epid = alertAlarm
                plug = True
                break
            elif eventPlug == event.ID:
                epid = eventPlug
                break
            elif eventPlug == event.pid:
                epid = eventPlug
                plug = True
                break
        if alarm and plug:
            type = SubscriptionType.PlugAlarm
        elif alarm and not plug:
            type = SubscriptionType.EventAlarm
        elif not alarm and plug:
            type = SubscriptionType.PlugAlert
        elif not alarm and not plug:
            type = SubscriptionType.EventAlert
        #return all of this info we found.
        return type, alid, epid
            

    def subscribe(self, alertAlarmID, eventPlugID): 
        """ Make a given Alert/alarm id listen to a given event/plug id. This is 
        slow and should only be done if we have no idea what types of ids they are,
        otherwise lets use a specific subscribe method below.
        """
        type,alid,epid = self.__validSubscription(alertAlarmID, eventPlugID)
        if type is not SubscriptionType.Unknown:
            sub = RegSubscription(self.__getNewSubscriptionId())

            if type is SubscriptionType.PlugAlarm:
                sub.setPlugAlarmSub(epid, alid)
            elif type is SubscriptionType.EventAlarm:
                sub.setEventAlarmSub(epid, alid)
                sub.eparent = self._getEventParent(epid)
            elif type is SubscriptionType.PlugAlert:
                sub.setPlugAlertSub(epid, alid)
                sub.lparent = self._getAlertParent(alid)
            elif type is SubscriptionType.EventAlert:
                sub.setEventAlertSub(epid, alid)
                sub.eparent = self._getEventParent(epid)
                sub.lparent = self._getAlertParent(alid)
            
            self._subscriptions[sub.ID] = sub 
            return True
        else: return False    

    def subscribeEventAlert(self, eid, lid): pass #TODO: write subscription for e-l
    def subscribeEventAlarm(self, eid, aid): pass #TODO: write subscription for e-a
    def subscribePlugAlert(self, pid, lid): pass  #TODO: write subscription for p-l
    def subscribePlugAlarm(self, pid, aid): pass  #TODO: write subscription for p-a

    def unsubscribe(self, first, second): 
        """ Remove a specified event id from a given alert id. """
        for sub in self._subscriptions.values():
            if sub == (first, second):
                self._subscriptions.pop(sub.ID)
                return True
            elif sub.contains(first) and sub.hasParent( second ):
                self._subscriptions.pop(sub.ID)
                return True
            
        return False
    
    def subscribedTo(self, eid): #TODO: needs to check parents
        """ Returns a list of all the alert/alarm ids that are subscribed to 
        the given event id.
        """
        lst = []
        for sub in self._subscriptions.values():
            if sub.eid == eid: lst.append(sub.lid)
        return lst
    
    def subscriptions(self, lid): #TODO: needs to check parents
        """ Gets all the event IDs that an alert is subscribed to."""
        subs = []
        for sub in self._subscriptions.values():
            if sub.lid == lid: subs.append(sub.eid)
        return subs
        
    def alreadySubscribed(self, lid, eid): #TODO: needs to check for parents
        """ Checks if there is already a subscription between an event and an 
        alert. If there is it will return its subscription id, otherwise None.
        """
        for sub in self._subscriptions.values():
            if sub == (lid,eid): return sub.ID
        return None
    
    def getsubscriptions(self):
        """ Returns a dictionary of subscription id to a tuple of alert id and
        event id.
        """
        subs = {}
        for sub in self._subscriptions.values():
            subs[sub.ID] = sub.asTuple()
        return subs
    
    
    def __register(self, cmd, module, ref, type):
        """ Base registration method, returns the registry ID, """
        newid = self.__genNewAttachId()
        if cmd is not None or module is not None:
            for id in self._attachments.keys():
                if module == self._attachments[id].module:
                    newid = id
                    break
        self._attachments[newid] = RegAttach( cmd, module, newid, type )
        ref.ID = newid
        return newid   
    
    def registerInterface(self, ref):
        """ Registers an interface temporarly with the registry. """
        id = self.__register(None, None, ref, INTERFACE)
        logging.debug("--Registered an Interface(%s)" % id)
        return id
        
    def registerPlug(self, cmd, module, ref):
        """ Registers a Plug with the Registry. This will persist even when
        the daemon shuts down.
        """
        id = self.__register(cmd, module, ref, PLUG)
        logging.debug("--Registered a Plug(%s, %s)" % (id, cmd))
        return id 

    def registerAlarm(self, cmd, module, ref):
        """ Registers an Alarm with the Registry. This will persist even when
        the daemon shuts down.
        """
        id = self.__register(cmd, module, ref, ALARM)
        logging.debug("--Registered an Alarm(%s, %s)" % (id, cmd))
        return id 

    def register(self, cmd, module, ref):
        """ Attempts to register the attachment by determining its type. """
        from empbase.attach.attachments import EmpAlarm, EmpPlug
        if isinstance(ref, EmpAlarm):
            self.__register(cmd, module, ref, type=ALARM)
        elif isinstance(ref, EmpPlug):
            self.__register(cmd, module, ref, type=PLUG)
        else: raise Exception("Attempted to register an object thats not an EMP Attachment.")
        
        
    def deregister(self, cid):
        """ Deregisters a Plug/Alarm/Interface given an id or cmd. """
        id = self.__getIDFromCID(cid)
        if id is not None:
            try:    self._attachments.pop(id)
            except: return False
        return True
 
    def isRegistered(self, cid):
        """ Checks if an id or command name is registered. """
        return (self.__getIDFromCID(cid) is not None)
         
    def daemonId(self):
        """ Returns the daemon's routing id. """
        return self._did
    
    def getPlugEventIds(self, pid):
        """Get plug's event's ids that are registered."""
        lst = []
        for event in self._events.values():
            if event.pid == pid: lst.append(event.ID)
        return lst
    
    def getPlugEventId(self, pid, ename):
        """Get the ID of an event given its plug's id and its command name."""
        for event in self._events.values():
            if event.name == ename and event.pid == pid: 
                return event.ID
        return None

    def getAttachId(self, cmd):
        """ Quickly gets the ID for a command name. """
        return self.__getIDFromCID(cmd)
    
    def getAttachIds(self):
        """ Quickly gets a list of all the attachment IDs. """
        return self._attachments.keys()
    
    def getAttachCmd(self, id):
        """ Gets an ID's command name, or None if it doesn't exist or is an 
        Interface.
        """
        try: return self._attachments[id].cmd
        except: return None 
    
    def getAttachCmds(self):
        """ Returns a list of all of the command names for each attachment. """
        cmds = []
        for val in self._attachments.values():
            if val.cmd is not None:
                cmds.append(val.cmd)
        return cmds
    
    def setAttachCmd(self, cid, newcmd):
        """ Resets the attachment's target name, the first parameter can be 
        the target's ID or its previous command string.
        """
        id = self.__getIDFromCID(cid)
        if id is not None:
            self._attachments[id].cmd = newcmd
            return True
        else:
            return False


    def getEventId(self, name):
        for event in self._events.values():
            if name == event.name or name == event.ID:
                return event.ID
        return None


    def loadEvents(self, eventlist):
        """ Loads all the events into the registry, and then gives them its
        new eid that was generated.
        """
        for event in eventlist:
            event.ID = self.loadEvent(event.name, event.pid)

    def loadEvent(self, name, aid):
        """ Saves an event to the registry if it doesn't exist, if it
        does then it returns the ID."""
        id = self.isEventLoaded(name, aid)
        if id is not None: return id
        else:
            eid = self.__genNewEventId()
            self._events[eid] = RegEvent(eid, aid, name)
            return eid
    
    def unloadEvent(self, eid):
        """ Unloads an event from the registry... I dont know if we will
        ever need this one, but I thought I should add it for completeness
        sake.
        """
        try: 
            tmp  = self._subscriptions
            self._subscriptions.clear()
            for k in tmp.keys(): #FIXME: There needs to be a faster way of doing this.
                if tmp[k].eid != eid:
                    self._subscriptions[k] = tmp[k]
            
            return self._events.pop(eid, None) is not None
        except: return False
    
    def isEventLoaded(self, name, aid):
        """ Checks if an event by the given name for the given plug is already 
        registered.
        """
        for event in self._events.values():
            if event == (name, aid): return event.ID
        return None
            
    
    def loadAlerts(self, alertlist):
        for alert in alertlist:
            alert.ID = self.loadAlert(alert.name, alert.aid)
    
    def loadAlert(self, name, aid):
        id = self.isAlertLoaded(name, aid)
        if id is not None: return id
        else:
            lid = self.__genNewAlertId()
            self._alerts[lid] = RegAlert(lid, aid, name)
            return lid
    
    def unloadAlert(self, lid):
        try:
            tmp  = self._subscriptions
            self._subscriptions.clear()
            for k in tmp.keys(): #FIXME: There needs to be a faster way of doing this.
                if tmp[k].lid != lid:
                    self._subscriptions[k] = tmp[k]

            return self._alerts.pop(lid, None) is not None
        except: return False
    
    def isAlertLoaded(self, name, aid):
        for alert in self._alerts.values():
            if alert == (name, aid): return alert.ID
        return None
    
    
    
    def __getIDFromCID(self, cid):
        """ Utility function that returns the id of a given command or id of
        an attachment.
        """
        if cid == "daemon": return self._did
        
        if cid in self._attachments or cid == self._did:
            return cid
        
        for k,v in self._attachments.items():
            if cid == v.cmd: return k
    
        return None
    
    def __genNewAttachId(self):
        """ Utility function for generating new attachment IDs. """ 
        while 1:
            tmp = ''.join(random.choice(ID_LETTERS) for _ in range(AID_SIZE))
            if tmp in self._attachments: continue
            else: return tmp
            
    def __genNewEventId(self):
        """ Utility function for generating new event IDs. """
        while 1:
            tmp = ''.join(random.choice(ID_LETTERS) for _ in range(EID_SIZE))
            if tmp in self._events: continue
            else: return tmp
            
    def __genNewAlertId(self):
        """ Utility function for generating new alert IDs. """
        while 1:
            tmp = ''.join(random.choice(ID_LETTERS) for _ in range(LID_SIZE))
            if tmp in self._alerts: continue
            else: return tmp
    
    def __getNewSubscriptionId(self):
        """ Utility function for generating new subscription IDs. """
        while 1:
            tmp = ''.join(random.choice(ID_LETTERS) for _ in range(SID_SIZE))
            if tmp in self._subscriptions: continue
            else: return tmp
            
    def __makeBackup(self):
        """ Makes a temporary backup of the current registry file in case 
        there is a problem saving to it. We definitely don't want to loose
        all of our subscriptions!"""
        pass #FIXME!!!
    
    def __removeBackup(self):
        """ Removes the temporary backup of the current registry since we
        saved it correctly."""
        pass #FIXME!!
    
    def __restoreBackup(self):
        """ Restore the temporary backup since we failed to save our current
        configurations and subscriptions!! This is very bad to have happened.
        """
        pass #FIXME!!!