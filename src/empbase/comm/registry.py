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

#XXX: Create a registry object that reads from an XML.
"""

Registry obj reads and saves to an xml.

Needed methods:
    * register(cmd, module) -> id number
    * deregister(id) -> bool
    * deregister(cmd) -> bool
    * daemonId() -> id number
    * isRegistered(id) -> bool
    * isRegistered(cmd) -> bool
    * getCmd(id) -> str
    * getId(cmd) -> id number
    * setCmd(id, newcmd) -> bool
    * setCmd(oldcmd, newcmd) -> bool
    * getCmds() -> [str]
    * getIds() -> [id numbers]


the xml structure is thus:
<daemon>
    <id>...</id>
</daemon>
<attachments>
    <plug>
        <cmd>...</cmd>
        <id>...</id>
        <module>...</module>
        <nointerfaces>1</nointerfaces> #optional!!
    </plug>
    <alarm>
        <cmd>...</cmd>
        <id>...</id>
        <module>...</module>
        <subscriptions>
            <id>...</id>
            <id>...</id>
            <id>...</id>
        </subscriptions>
    </alarm>
</attachments>

"""

# RegItem Types
PLUG = 0
ALARM = 1
INTERFACE = 2
DAEMON = 3


class RegItem():
    """ This is the object kept in the registry list and can easily be pushed 
    into an XML file.
    """
    def __init__(self, cmd, module, id, type=PLUG):
        self.cmd = cmd
        self.module = module
        self.id = id
        self.type = type
    
    

class Registry():
    """ This is the list of destinations for messages. Can be queried against 
    through the daemon, and is saved to base-dir/save/registry.xml where 
    base-dir is the variable thats in the configuration file.
    """
    def __init__(self, filepath):
        self._file = filepath
        self._did = "%s" % str(random.random())[2:12]
        self._list = {}
        self.load()
        
    def load(self): 
        """ Loads the registry list into this Registry object for use in the 
        routing protocol.
        """
        #TODO: write the XML parser
        pass
        
    def save(self): 
        """ Saves this Registry to the registry file in the base directory. """
        #TODO: write the XML writer
        pass
    
    def allowInterfaces(self, pid, allow=True):
        """ Toggle whether the plug id allows interfaces to listen to it. """ 
        pass #LATER: implement interface listen toggle
    
    def subscribe(self, aid, pid): 
        """ Make a given alarm id listen to a given plug id. """
        pass #TODO: implement subscribe

    def desubscribe(self, aid, pid): 
        """ Remove a specified plug id from a given alarm id. """
        pass #TODO: implement desubscription process
    
    def subscribedTo(self, pid): 
        """ Returns a list of all the ids that are subscribed to the given id.
        If the id allows interfaces, this will return all the registered 
        interface ids too.
        """
        pass #TODO: implement subscription call to plugin
    
    def subscriptions(self, alarm): 
        """ Gets all the ids of the alarm id given. """
        pass #TODO: implement subscriptions method
    
    
    def register(self, cmd, module, type):
        """ Base registration method, returns the registry ID, """
        newid = self.__genNewId()
        self._list[newid] = RegItem( cmd, module, newid, type )
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
            try:    self._list.pop(id)
            except: return False
        return True
        
    def daemonId(self):
        """ Returns the daemon's routing id. """
        return self._did
    
    def isRegistered(self, cid):
        """ Checks if an id or command name is registered. """
        return (self.__getIDFromCID(cid) is not None)
    
    def getCmd(self, id):
        """ Gets an ID's command name, or None if it doesn't exist or is an 
        Interface.
        """
        try: return self._list[id].cmd
        except: return None 
    
    def getCmds(self):
        cmds = []
        for val in self._list.values():
            if val.cmd is not None:
                cmds.append(val.cmd)
        return cmds
    
    def getId(self, cmd):
        return self.__getIDFromCID(cmd)
    
    def getIds(self):
        return self._list.keys()
    
    def setCmd(self, cid, newcmd):
        id = self.__getIDFromCID(cid)
        if id is not None:
            self._list[id].cmd = newcmd
            return True
        else:
            return False
    
    def __getIDFromCID(self, cid):
        if cid in self._list:
            return cid
        
        for k,v in self._list.items():
            if cid == v.cmd: return k
    
        return None
    
    
    