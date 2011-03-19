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
import random
import logging
from xml.etree.ElementTree import ElementTree, SubElement

"""
the registry xml structure is thus:
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
"""

# RegItem Types
PLUG = "plug"
ALARM = "alarm"
INTERFACE = "interface"
DAEMON = "daemon"


class RegAttach():
    """ This is the object kept in the registry list and can easily be pushed 
    into an XML file.
    """
    def __init__(self, cmd, module, id, type=PLUG):
        self.cmd = cmd
        self.module = module
        self.id = id
        self.type = type
        
    def getAttrib(self):
        """Turns the attachment into an XML node for saving into the 
        registry file.
        """
        return { "cmd": self.cmd,
                      "module": self.module,
                      "id": self.id}
    
    def __eq__(self, other):
        """ Compares IDs of two RegItems or of a id string. """
        if type(other) is str:
            return other == self.id
        elif type(other) is RegAttach:
            return other.id == self.id
        else: return False
    
    

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
        self._events = {}
        self._did = self.__genNewAttachId()
        self.load()
        logging.debug("loaded... theres %d attachments"%int(len(self._attachments)))
        
    def load(self): 
        """ Loads the registry list into this Registry object for use in the 
        routing protocol.
        """
        try:
            this = ElementTree()
            this.parse(self._file)
            attachments = this.find("attachments")
            for node in attachments.childNodes:
                if node.nodeName in [ALARM, PLUG]:
                    cmd = node.attrib["cmd"]
                    mod = node.attrib["mod"]
                    id  = node.attrib["id"]
                    self._attachments[id] = RegAttach(cmd, mod, id, node.nodeName)
                
            daemon = this.find("daemon")
            if daemon.hasAttributes():
                self._did = node.attrib["id"]
                self.checkDaemonID()
            
            events = this.find("events")
            #TODO: parse and load events into registry.
        except IOError:pass# no such file? who cares...
        except Exception as e: logging.error(e)
         
    def save(self): 
        """ Saves this Registry to the registry file in the base directory. """
        try:
            
            #SubElement(this, "daemon", attrib={"id":self._did})
            #events = this.SubElement(this, "events") #TODO: verify this is how events will be saved.
            
            for attach in self._attachments.values():
                SubElement("attachments", attach.type, attrib=attach.getAttrib())
            
            
            
            
            logging.debug("Saving registry...")
            if self.__try_setup_path(self._file):
                with open(self._file, "w") as savefile: 
                    this.write(savefile)
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
        
    def allowInterfaces(self, pid, allow=True):
        """ Toggle whether the plug id allows interfaces to listen to it. """ 
        pass #LATER: implement interface listen toggle
    
    def subscribe(self, aid, eid): 
        """ Make a given Alarm id listen to a given event id. """
        pass #TODO: implement subscribe

    def unsubscribe(self, aid, eid): 
        """ Remove a specified event id from a given alarm id. """
        pass #TODO: implement desubscription process
    
    def subscribedTo(self, eid): 
        """ Returns a list of all the ids that are subscribed to the given 
        event id. If the id allows interfaces, this will return all the 
        registered interface id's too.
        """
        pass #TODO: implement subscription call to plugin
    
    def subscriptions(self, aid): 
        """ Gets all the events that an alarm is subscribed to."""
        pass #TODO: implement subscriptions method

    
    def register(self, cmd, module, ref, type):
        """ Base registration method, returns the registry ID, """
        newid = self.__genNewAttachId()
        self._attachments[newid] = RegAttach( cmd, module, newid, type )
        ref.ID = newid
        return newid   
    
    def registerInterface(self, ref):
        """ Registers an interface temporarly with the registry. """
        logging.debug("--Registered an Interface")
        return self.register(None, None, ref, INTERFACE)
        
    def registerPlug(self, cmd, module, ref):
        """ Registers a Plug with the Registry. This will persist even when
        the daemon shuts down.
        """
        logging.debug("--Registered a Plug")
        return self.register(cmd, module, ref, PLUG)

    def registerAlarm(self, cmd, module, ref):
        """ Registers an Alarm with the Registry. This will persist even when
        the daemon shuts down.
        """
        logging.debug("--Registered an Alarm")
        return self.register(cmd, module, ref, ALARM)

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
        cmds = []
        for val in self._attachments.values():
            if val.cmd is not None:
                cmds.append(val.cmd)
        return cmds
    
    def getId(self, cmd):
        return self.__getIDFromCID(cmd)
    
    def getIds(self):
        return self._attachments.keys()
    
    def setCmd(self, cid, newcmd):
        id = self.__getIDFromCID(cid)
        if id is not None:
            self._attachments[id].cmd = newcmd
            return True
        else:
            return False


    def loadEvent(self, name, pid ):
        #TODO: return eid and save it.
        if self.isEventLoaded(name):
            pass
            #get its eid and return
        else:
            eid = self.__genNewEventId()
            #save
            return eid
    
    def unloadEvent(self, eid):
        pass
    
    def isEventLoaded(self, name):
        return False #TODO: check the registry
    
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
            tmp = "%s" % str(random.random())[2:12]
            if tmp in self._attachments:
                continue
            else:
                return tmp
            
    def __genNewEventId(self):
        """ Utility function for generating new event IDs. """
        pass #TODO: how are events going to differ from attachments?
    