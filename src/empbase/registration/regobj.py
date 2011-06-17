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
            return other == self.id or other == self.cmd
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
            return self.ID == other or self.name == other
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
            return self.ID == other or self.name == other
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
        
        
class SubscriptionType:
    """ Each subscription has a type, these classify how the id's 
    held in the subscription are connected and how to reference 
    them. (ie aid,lid,eid,pid).
    """
    Unknown, EventAlert, EventAlarm, PlugAlert, PlugAlarm = range(5)
        
        
        
def parseAttribToSub( attrib ):        
    """Parses the attributes into a subscription. It will throw an
    Exception if this isn't possible.
    """
    #I know its gross but it has to be done.
    sub = None
    if "id" in attrib: sub = RegSubscription(attrib["id"])
    else:return None
    if "eid" in attrib:
        if "lid" in attrib:
            sub.setEventAlertSub(attrib["eid"], attrib["lid"])
        elif "aid" in attrib:
            sub.setEventAlarmSub(attrib["eid"], attrib["aid"])
        else: return None
    elif "pid" in attrib:
        if "lid" in attrib:
            sub.setPlugAlertSub(attrib["pid"], attrib["lid"])
        elif "aid" in attrib:
            sub.setPlugAlarmSub(attrib["pid"], attrib["aid"])
        else: return None
    else: return None
    
    sub.eparent = attrib.get("eparent", None)
    sub.lparent = attrib.get("lparent", None)
    return sub

class RegSubscription():
    """ A subscription can be a connection between event and alert, 
    but also between alarms and events, alarms and plugs, and also 
    plug and alert. 
            (eid,lid), (eid,aid), (pid,lid), (pid,aid)
    """
            
    def __init__(self, id):
        self.ID = id
        self.subs = (None,None)
        self.type = SubscriptionType.Unknown
        self.eparent = None
        self.lparent = None
     
    def isValid(self):
        """Check if the subscription has a valid linking."""
        logging.debug("Validity of Subscription: sub(%s, %s)=%d"%(self.subs[0],self.subs[1],self.type))
        return self.subs[0] is not None and  \
               self.subs[1] is not None and  \
               self.type is not SubscriptionType.Unknown
            
    def getAttrib(self):
        """Returns all of the attributes for this subscription as a 
        map for easy parsing an pushing into a XML node. (Done in 
        the registry.) 
        If the current subscription is invalid then an Exception will
        be raised.
        """
        lst = {"id":str(self.ID)}
        if not self.isValid(): 
            raise TypeError("The Subscription isn't valid.")
        
        if self.type==SubscriptionType.EventAlert:
            lst["eid"], lst["lid"] = self.subs
        elif self.type==SubscriptionType.EventAlarm:
            lst["eid"], lst["aid"] = self.subs
        elif self.type==SubscriptionType.PlugAlert:
            lst["pid"], lst["lid"] = self.subs
        elif self.type==SubscriptionType.PlugAlarm:
            lst["pid"], lst["aid"] = self.subs
            
        if self.eparent is not None: 
            lst["eparent"] = self.eparent
        if self.lparent is not None:
            lst["lparent"] = self.lparent
            
        return lst
    
    def asTuple(self): 
        """Returns the subscription as a tuple with two IDs."""
        return self.subs 
    
    def setEventAlertSub(self, eid, lid):
        """Set the subscription between an event and an alert. This
        means that whenever the event fires the alert will trigger.
        """
        self.__set(SubscriptionType.EventAlert, eid, lid)
        
    def setEventAlarmSub(self, eid, aid):
        """Set the subscription between an event and an alarm. This
        means that whenever the event fires all of the alerts for the
        given alarm will trigger.
        """
        self.__set(SubscriptionType.EventAlarm, eid, aid)
        
    def setPlugAlertSub(self, pid, lid):
        """ Set the subscription between a plug and an alert. This
        means that whenever any event from the given plug fires, the
        alert will trigger. 
        """
        self.__set(SubscriptionType.PlugAlert, pid, lid)
        
    def setPlugAlarmSub(self, pid, aid):
        """ Set the subscription between a plug and an alarm. This
        means that whenever any event from the given plug fires, all
        of the alerts for the given alarm will trigger. 
        """
        self.__set(SubscriptionType.PlugAlarm, pid, aid)
        
        
    def contains(self, id):
        """ Checks if this subscription is for the given id. """
        if id == self.subs[0]: return self.subs[1]
        elif id == self.subs[1]: return self.subs[0]
        else: return False
        
    def hasParent(self, id):
        """ If the ID is a parent of this subscription. (ie if the
        id is of an alarm and its alert is part of this subscription).
        """
        return self.eparent == id or \
               self.lparent == id
        
    def __set(self, type, first, second):
        """Set the internals of the subscription. It makes the list of 
        setters make a little more sense.
        """
        self.type = type
        self.subs = (first, second)    
        
    def __eq__(self, other):
        """ Check if this subscription is equal to something else. When 
        'other' is a string it compares it with the subscriptions unique ID,
        if its a tuple it compares it to the ids of the subscription links.
        """
        # Used to compare two tuples as groups without order.
        def swapcmp(x,y): return x==y or x==(y[1],y[0])
        
        if type(other) is str:
            return self.ID == other
        elif type(other) is tuple:
            return swapcmp(other, self.subs)
        elif type(other) is RegSubscription:
            return self.ID == other.ID and \
                   swapcmp(self.subs, other.subs)
        else: return False
        