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
import random
import logging
from xml.dom.minidom import Element,Document,parse

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
        
    def toXMLNode(self):
        me = Element(self.type)
        """
        cmd = Element("cmd")
        tmp1 = Text()
        tmp1.data = self.cmd
        cmd.appendChild(tmp1)
        me.appendChild(cmd)
        
        mod = Element( "module")    
        tmp2 = Text()
        tmp2.data = self.module
        mod.appendChild(tmp2)
        me.appendChild(mod)
        
        id = Element("id")
        tmp3 = Text()
        tmp3.data = self.id
        id.appendChild(tmp3)
        me.appendChild(id)
        """
        
        me.setAttribute("cmd", self.cmd)
        me.setAttribute("module", self.module)
        me.setAttribute("id", self.id)
        return me
    
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
        self._did = self.__genNewAttachId()
        self._attachments = {}
        self._events = {}
        self.load()
        
    def load(self): 
        """ Loads the registry list into this Registry object for use in the 
        routing protocol.
        """
        this = parse(self._file)
        attachments = this.getElementsByTagName("attachments")
        for node in attachments.childNodes:
            if node.nodeName in [ALARM, PLUG]:
                cmd = node.getAttribute("cmd")
                mod = node.getAttribute("mod")
                id = node.getAttribute("id")
                self._attachments(RegAttach(cmd, mod, id, node.nodeName))
            
        daemon = this.getElementsByTagName("daemon")
        if daemon.hasAttributes():
            self._did = node.getAttribute("id")
            self.checkDaemonID()
        
        events = this.getElementsByTagName("events")
        #TODO: parse and load events into registry.
         
    def save(self): 
        """ Saves this Registry to the registry file in the base directory. """
        try:
            this = Document()
            attachments = this.createElement("attachments")
            for v in self._attachments.values():
                if v.type is PLUG or v.type is ALARM:
                    attachments.appendChild(v.toXMLNode())
            this.appendChild(attachments)
                
            daemon = this.createElement("daemon")
            daemon.setAttribute("id", self._did)
            this.appendChild(daemon)
            
            events = this.createElement("events")
            for v in self._events.values():
                events.appendChild(v.toXMLNode())
            this.appendChild(events)
            #TODO: verify this is how events will be saved.
            
            with open(self._file, "w") as savefile:
                savefile.write(this.toxml())
            return True
        except Exception as e:
            logging.exception(e)
            return False
 
    
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

    
    def register(self, cmd, module, type):
        """ Base registration method, returns the registry ID, """
        newid = self.__genNewAttachId()
        self._attachments[newid] = RegAttach( cmd, module, newid, type )
        return newid   
    
    def registerInterface(self):
        """ Registers an interface temporarly with the registry. """
        return self.register(None, None, INTERFACE)
        
    def registerPlug(self, cmd, module):
        """ Registers a Plug with the Registry. This will persist even when
        the daemon shuts down.
        """
        return self.register(cmd, module, PLUG)

    def registerAlarm(self, cmd, module):
        """ Registers an Alarm with the Registry. This will persist even when
        the daemon shuts down.
        """
        return self.register(cmd, module, ALARM)

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
    