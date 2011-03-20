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
import xml.etree.ElementTree as ET
from empbase.registration.regobj import RegAttach, RegEvent, \
                                        PLUG, ALARM, INTERFACE

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
        <event pid='' eid='' name=''>
            <subscribers>
                <id>...</id>
                <id>...</id>
                <id>...</id>
            </subscribers>
        </event>
        ...
    </events>
</registry>
"""

# Size of the IDs generated for Attachments, and Events.
AID_SIZE = 5
EID_SIZE = 10


class Registry():
    """ This is the list of destinations for messages. Can be queried against 
    through the daemon, and is saved to base-dir/save/registry.xml where 
    base-dir is the variable thats in the configuration file.
    """
   
    def __init__(self, filepath):
        """ Sets up a new registry in case the loading fails. If the loading 
        is a success, then the Daemon ID will always be constant and the 
        attachments and events will all keep their ids and command names.
        """
        self._file = filepath
        self._attachments = {}
        self._events      = {}
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
                                  node.attrib["name"])
                subs = node.find("subscribers")
                for sub in subs.getchildren():
                    event.addSubscriber(sub.attrib["id"])
                self._events[event.ID] = event

        except IOError: pass # no such file? who cares...
        except Exception as e: logging.error(e)
         
    def save(self): 
        """ Saves this Registry to the registry file in the base directory. """
        try:
            root = ET.Element("registry", attrib={"save":str(time.time())})
            
            # Make sure we have the daemon's ID for next time we load!
            ET.SubElement(root, "daemon", attrib={"id":self._did})
            
            #Add attachments to the registry!
            attachments = ET.Element("attachments")
            for attach in self._attachments.values():
                ET.SubElement(attachments, attach.type, attrib=attach.getAttrib())
            root.append(attachments)
            
            #Add all the events and their subscribers!
            events = ET.Element("events")
            for event in self._events.values():
                e = ET.Element("event", attrib=event.getAttrib())
                subs = ET.Element("subscribers")
                for sub in self.subscribedTo(event.ID):
                    ET.SubElement(subs, "sub", attrib={"id":sub.ID})
                e.append(subs)
                events.append(e)
            root.append(events)
            
            # Save everything to the file that we were given on startup.
            logging.debug("Saving registry to %s"%self._file)
            if self.__try_setup_path(self._file):
                tree = ET.ElementTree(root)
                with open(self._file, "wb") as savefile: 
                    tree.write(savefile)
                logging.debug("Registry Saved!")
                return True
            else: return False
        except Exception as e:
            logging.exception(e)
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

    
    def subscribe(self, aid, eid): 
        """ Make a given Alarm id listen to a given event id. """
        try: 
            self._events[eid].addSubscriber(aid)
            return True
        except: return False    

    def unsubscribe(self, aid, eid): 
        """ Remove a specified event id from a given alarm id. """
        try: return self._events[eid].removeSubscriber(aid)
        except: return False    
    
    def subscribedTo(self, eid): 
        """ Returns a list of all the ids that are subscribed to the given 
        event id. If the id allows interfaces, this will return all the 
        registered interface id's too.
        """
        try: return self._events[eid].subscribers()
        except: return None
    
    def subscriptions(self, aid): 
        """ Gets all the event IDs that an alarm is subscribed to."""
        subs = []
        for event in self._events.values():
            if event.subscribes(aid):
                subs.append(event.ID)
        return subs
        
    
    def __register(self, cmd, module, ref, type):
        """ Base registration method, returns the registry ID, """
        newid = self.__genNewAttachId()
        if cmd is not None or module is not None:
            #check if the 
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
        logging.debug("--Registered a Plug(%s)" % id)
        return id 

    def registerAlarm(self, cmd, module, ref):
        """ Registers an Alarm with the Registry. This will persist even when
        the daemon shuts down.
        """
        id = self.__register(cmd, module, ref, ALARM)
        logging.debug("--Registered an Alarm(%s)" % id)
        return id 

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
    
    def getCmd(self, id):
        """ Gets an ID's command name, or None if it doesn't exist or is an 
        Interface.
        """
        try: return self._attachments[id].cmd
        except: return None 
    
    def getCmds(self):
        """ Returns a list of all of the command names for each attachment. """
        cmds = []
        for val in self._attachments.values():
            if val.cmd is not None:
                cmds.append(val.cmd)
        return cmds
    
    def getId(self, cmd):
        """ Quickly gets the ID for a command name. """
        return self.__getIDFromCID(cmd)
    
    def getIds(self):
        """ Quickly gets a list of all the attachment IDs. """
        return self._attachments.keys()
    
    def setCmd(self, cid, newcmd):
        """ Resets the attachment's target name, the first parameter can be 
        the target's ID or its previous command string.
        """
        id = self.__getIDFromCID(cid)
        if id is not None:
            self._attachments[id].cmd = newcmd
            return True
        else:
            return False


    def loadEvents(self, eventlist):
        """ Loads all the events into the registry, and then gives them its
        new eid that was generated.
        """
        for event in eventlist:
            event.ID = self.loadEvent(event.name, event.pid)

    def loadEvent(self, name, pid ):
        """ Saves an event to the registry if it doesn't exist, if it
        does then it returns the ID."""
        if self.isEventLoaded(name):
            for id in self._events.keys():
                if self._events[id].name == name:
                    return id
            #SHOULD NEVER GET HERE BECAUSE IT WAS FOUND IN THE LIST
            raise Exception("Error generating a new ID")
        else:
            eid = self.__genNewEventId()
            self._events[eid] = RegEvent(eid, pid, name)
            return eid
    
    def unloadEvent(self, eid):
        """ Unloads an event from the registry... I dont know if we will
        ever need this one, but I thought I should add it for completeness
        sake.
        """
        try: return self._events.pop(eid, None) is not None
        except: return False
    
    def isEventLoaded(self, name):
        for event in self._events.values():
            if event.name == name:
                return True
        return False
            
    
    def __getIDFromCID(self, cid):
        """ Utility function that returns the id of a given command or id of
        an attachment.
        """
        if cid in self._attachments or cid == self._did:
            return cid
        
        for k,v in self._attachments.items():
            if cid == v.cmd: return k
    
        return None
    
    def __genNewAttachId(self):
        """ Utility function for generating new attachment IDs. """ 
        while 1:
            tmp = "%s" % str(random.random())[2:2+AID_SIZE]
            if tmp in self._attachments:
                continue
            else:
                return tmp
            
    def __genNewEventId(self):
        """ Utility function for generating new event IDs. """
        while 1:
            tmp = "%s" % str(random.random())[2:2+EID_SIZE]
            if tmp in self._events:
                continue
            else:
                return tmp