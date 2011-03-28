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
import empbase.event.events as empevents
import empbase.event.alerts as empalerts
import empbase.attach.attachments as attach

# RegAttach Types
PLUG = "plug"
ALARM = "alarm"
INTERFACE = "interface"


class RegAttach():
    """ This is just a representation of an Attachment in the registry
    system. It is held here to be quickly pushed into the registry file 
    when closing.
    """
    def __init__(self, cmd, module, id, type=PLUG):
        self.cmd = cmd
        self.module = module
        self.id = id
        self.type = type
        
    def getAttrib(self):
        """Returns the attributes of the attachment."""
        return { "cmd": str(self.cmd),
                 "module": str(self.module),
                 "id": str(self.id) }
    
    def __eq__(self, other):
        """ Compares IDs of two RegItems or of a id string. """
        if type(other) is str:
            return other == self.id
        elif type(other) is RegAttach:
            return other.id == self.id
        elif type(other) is attach.EmpAttachment:
            if type(other) is attach.EmpPlug and self.type==PLUG:
                return self.id == other.ID
            elif type(other) is attach.EmpAlarm and self.type==ALARM:
                return self.id == other.ID
            else: return False
        else: return False
    

class RegEvent():
    """ This is just represents an event in the registry system."""
    def __init__(self, id, pid, name):
        self.ID = id
        self.pid = pid
        self.name = name
    
    def getAttrib(self):
        """ Returns a dictionary representing this object, this makes it
        easier to push it to XML in the Registry.
        """
        return {"pid": str(self.pid),
                "id": str(self.ID),
                "name": str(self.name)}
    
    def __eq__(self, other):
        if type(other) is str:
            return self.ID == other
        elif type(other) is tuple:
            return other == (self.name, self.pid)
        elif type(other) is RegEvent:
            return self.ID == other.ID and \
                   self.name == other.name and \
                   self.pid == other.pid
        elif type(other) is empevents.Event:
            return self.ID == other.ID and \
                   self.name == other.name and \
                   self.pid == other.pid
        else: return False


class RegAlert():
    """ This just represents an alert in the registry system."""        
    def __init__(self, id, aid, name):
        self.ID = id
        self.aid = aid
        self.name = name
            
    def getAttrib(self):
        """ Returns a dictionary representing this object, this makes it
        easier to push it to XML in the Registry.
        """
        return {"aid":str(self.aid),
                "id":str(self.ID),
                "name":str(self.name)}
        
    def __eq__(self, other):
        if type(other) is str:
            return self.ID == other
        elif type(other) is tuple:
            return other == (self.name, self.aid)
        elif type(other) is RegAlert:
            return self.ID == other.ID and \
                   self.name == other.name and \
                   self.aid == other.aid
        elif type(other) is empalerts.Alert:
            return self.ID == other.ID and \
                   self.name == other.name and \
                   self.aid == other.aid
        else: return False
        
        
class RegSubscription():
    """ """        
    def __init__(self, id, eid, lid):
        self.ID = id
        self.eid = eid
        self.lid = lid
            
    def getAttrib(self):
        return {"eid":str(self.eid),
                "lid":str(self.lid),
                "id":str(self.ID)}
    
    def asTuple(self):
        return (self.lid, self.eid)    
        
    def __eq__(self, other):
        if type(other) is str:
            return self.ID == other
        elif type(other) is tuple:
            return other == (self.lid, self.eid)
        elif type(other) is RegSubscription:
            return self.ID == other.ID and \
                   self.lid == other.lid and \
                   self.eid == other.eid
        else: return False
        