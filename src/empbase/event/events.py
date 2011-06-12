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
from threading import Lock
from empbase.comm.messages import makeAlertMsg
from empbase.event.eventmanager import triggerEvent, detriggerEvent, \
                                       registerEvent, deregisterEvent


#This is the id of an unknown event.
UNKNOWN = "<UNKNOWNOMG>"
DEFAULT_HALFLIFE = 1 #second

class Event():
    """ This is the base type of event that can happen within EMP,
    these are what Alarms subscribe to. These are created and saved
    by Plugs or on command and are used by the EventManager to know 
    who to send to.
    """
    
    def __init__(self, plug, name, msg="", description=""):
        """ All events have a string message that is sent to the alarm,
        the alarm can choose to use it if it wants to.
        """
        self.plug = plug
        self.name = name
        self.msg  = msg
        self.description = description
        self.ID   = UNKNOWN
        self.halflife = DEFAULT_HALFLIFE
        self.triggered = False
        self.triggering = Lock()
        
        # Group variables will be set and used if this event is part of an
        # event group.
        self.group      = None
        self.is_default = False
    
    def _getPID(self):
        return self.plug.ID
    
    def trigger(self, msg=None):
        """This is the method you must call when you want to trigger
        this Event.
        """
        self.triggering.acquire()
        if self.triggered: return
        
        if msg is not None: 
            self.msg = msg
            
        if self.group is not None:
            self.group.triggerCallback()
        triggerEvent( self.ID )
        
        self.triggered = True
        self.triggering.release()

    def detrigger(self):
        self.triggering.acquire()
        if not self.triggered: 
            self.triggering.release()
            return
        detriggerEvent(self.ID)
        if self.group is not None:
            self.group.detriggerCallback()
        self.triggered = False
        self.triggering.release()    
        
    def register(self):
        """ Register this event with the event manager. You NEED to run this if 
        the event was created during run time. Also, make sure you add this event
        to the list that gets returned when the daemon calls get_events().
        """
        registerEvent( self )
    
    def deregister(self):
        """ Removes this event from the subscription lists and the event 
        manager. You NEED to call this if you are destroying events at runtime. 
        Also, make sure you remove it from the list of events that get returned
        when the daemon calls get_events.
        """
        deregisterEvent( self )

    def __hash__(self):
        return id(self)

    def __eq__(self, other):
        if not isinstance(other, Event): return False
        return (self.name == other.name) and \
               (self.ID   == other.ID)   and \
               (self.plug.ID == other.plug.ID)
    

    def __str__(self):
        """ When it wants to turn itself into a string it uses the 
        AlertMessage protocol."""
        return str(makeAlertMsg(self.msg, self.plug.ID, title=self.name))


EGROUP_LOGIC = 0
EGROUP_RADIO = 1
EGROUP_ALL   = 2
EGROUP_MUST  = 3

class EventGroup():
    def __init__(self, plug, name, type=EGROUP_LOGIC):
        self.type = type
        self.name = name
        self.pref = plug
        self.ID   = UNKNOWN
        self.events  = []
        self.default = None
        self.triggering = False
        
    def addEvent(self, event, default=False):
        self.events.append(event)
        event.group = self
        event.is_default = default
        if default: self.default = len(self.events)-1
    
    def removeEvent(self, event):
        self.events.remove(event)
        event.group = None
        if event.is_default and self.default == event:
            self.default = None
    
    def triggerCallback(self, tevent):
        self.triggering = True #LATER: race condition?? make into a semiphore??
        if self.triggering: return
        
        if self.type == EGROUP_ALL:
            for event in self.events:
                if event == tevent: continue
                event.trigger()
        elif self.type == EGROUP_RADIO:
            for event in self.events():
                if event == tevent: continue
                event.detrigger()
        self.triggering = False
        
    def detriggerCallback(self):
        if self.type == EGROUP_MUST:
            if self.default is not None:
                self.events[self.default].trigger()
            else: raise Exception("Event Group(%s) does not have a default!")
    
"""
Sub event construction idea...

    Essentially what I want to happen is this;
        emp --target=twitter mkevent "mentioned-in-twit"
                                     others-status
                                     @contains ( 'Alex' @or
                                                 'Dean' @or
                                                 'dstar' )

    Maybe not that gross, but I want events to be constructed based on a 
    language that looks similar to regular expressions but be more verbose in 
    how it describes what it is looking for.
                                @[term](args)
                                
    Where args can be another expression as long as its return is of the right 
    type.
    
    I also want the ability to combine two events to create another one, in 
    effect, making an event that is triggered when both are, or when only one
    is, or when one triggers with a certain value the other one can be ignored,
    etc. Here is an example:
        emp --target=calendar mkevent 'stay-inside'
                                       friday, day13
                                       @both( @true )
                                        
    I know that doesn't make complete sense but essentially it would make an 
    event called 'stay-inside' and trigger when the event 'friday' and the 
    event 'day13' both trigger or are capable of being triggered.
    
    **NOTE** Also you may want to address that 'capable of being triggered' 
    at a later time... this may be an interesting concept. Adding latent 
    events, (e.g. Events that have state which can not only trigger but also
    store a value persistantly (ie for a whole day, etc.)) 
        
            
            
    a list of possible terms that should be possible
        terms for event values
            - is, equal, isequal, ==, same
            - isnt, nequal, not, !=, different
            - greater, morethan, >, >=, gt, gtoe
            - less, lessthan, >, >=, lt, ltoe
            - or, either
            - and, both
            - contains
            - neither
            - true
            - false
            - int, str, bool, obj, list (used to check if it is that type)
            - +,-,*,/,%,(,) (math on results e.g. @>(3-&eres1, 9)
    
        terms relating to events themselves
            - recently, cur (when did the event fire?)
            - before, after, concur (events in relation to each other.)
    
    So yeah, here goes a BNF of the language I'm thinking of:  
    
        <expression>  :=  <term> [( <argument> [, <argument> [, <argument> ...]] )] 
        <argument>    := <expression> | <sexpression> 
        <sexpression> := <reference> | <value> 
        <term>        := @<see the list of terms above> | <compound>
        <compound>    := <term>@<term>         #eg. neither@true(&eres1, &eres2)
        
        <value>    := <number> | <number>.<number> | <string> | <bool> | <obj> 
        <number>   := [0-9]+
        <bool>     := True | False
        <string>   := "<cstr>"
        <cstr>     := [a-zA-Z]*
        
        <reference> := &<res>
        <res>  := <eres> | <eref>
        # an event result, eres3 is the result of the third named event 
        <eres> := eres<number>
        #an event reference, checking the actual state of the event
        <eref> := eref<number>
    
    
        <obj>  := <list> | <dict>
        <list> := \[ <sexpression> [, <sexpression> [, <sexpression> ...]] \] 
        <dict> := { <pair> [,<pair> [, <pair> ...]] }
        <pair> := <string> : <sexpression>
        
    And thats it... fairly concise and to the point I think. Once that is 
    working I would be free to add more terms and then run them how I choose.
    
    
Side effects of this idea...

    It means events and the event hierarchy would have to be saved 
    semipermanently. 
    
    It means people would have to learn this new language to begin to craft
    their own event setups... Interfaces may need to be able to build them 
    for you.
    
    It makes the entire event creation general, which could pose issues for
    boundary cases. (eg a return type not one of the possible <value>s.)
     
    It means more work. Both on the part of the user, and the plug developer. 
    
    Events now need to be more developed. More information needs to be 
    maintained and given.
    
        Events need to store time it was last triggered, why it was triggered
        (the msg value??), some ?state? for comparison?, needs to _return_ a 
        <value> type. 
    
    An Event Queue may need to be implemented to check when and where the event
    triggered. Logging on this may be necessary.
    
    It means we are limiting ourselves to only catching types of events 
    depicted by the plug and the event language. 
    
        Is this a bad thing? What exactly are we missing or foregoing by doing 
        it this way? Can we compensate somehow in the language or by force the
        plug developers to do something?
            
            force them to have a specific type and number of events, return a 
            specific type.
            
            add more terms or make it easy to, so that when we find where we 
            are weak we can adjust. *easiest*
            
Implementation thoughts...

    To implement this idea I would need:
        - a parser
        - something that generates the function which looks at the return 
          value (ie generates the event)
          
    Event manager could do it, but would need a queue, and the above 
    mentioned things... 
    
    The registry would need to change. how events are stored, its now a 
    hierarchy so XML is fine still. (is it a hierarchy? how would that work?
    technically i think a tree would be better since a sub-event can utilize 
    the event from one or more other events.) 
    
    what should i call these user defined events? UserEvents? SubEvents?
    GenEvents? CompoundEvent? ConsEvent?
    
    I could make these events a type of EmpAlarm? They respond to events.
    That would take little to no change to the registry...
        
        alarms would need to do commands and etc... make a new type of 
        alarm? move commands out of attachment? it could be a type of
        interface, that gets stored permanently...
        
    Is there a way of implementing just enough that we don't have to implement
    the whole thing until later? I would really like to get an alpha version 
    out to run tests on...
    
    Are all events able to be 'subevented' from? 
    
    Is the language that we would be building verbose enough?
"""
