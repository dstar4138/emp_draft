# EMP Attachment API #

There are two main types of Attachments that EMP recognizes; Plugs (things you
monitor) and Alarms (things that alert). Depending on what you would like to 
build there are multiple avenues to work in.

-------------------------------------------------------------------------------

## Alarm Attachments ##


There is only one kind of Alarm which makes it easy for creating one of your 
own. All your class has to do is implement EmpAlarm and follow the EMP API.
Heres an example of the most basic EMP style Alarm

    from empbase.attach.attachments import EmpAlarm
    class MyAlarm(EmpAlarm):
        def __init__( self, config ):
            EmpAlarm.__init__(self, config)
            
        def save(self):
            EmpAlarm.save()

        def get_commands(self):
            return []
            
        def alert(self):
            pass

And that is it! Now all you have to do is fill in the blanks. But heres an 
explaination of each function and why it needs to be there:

* `__init__` : this is your initialization function, if you are familiar with 
python then this should be no supprise to you. Notice you have a single 
parameter. This is all the variables you want to have EMP save for you in 
its configuration file. See the Using your Configurations section below for 
more information.
             
* `save` : This is whats called when EMP is shutting down, so if you have 
variables that you want to save in the config file for next time, put them in 
conf. Also dont forget to call EmpAlarm.save() first.

* `get_commands` : This returns a list of Command objects so that the message
router can quickly trigger them. Please see the Command Object section for more 
information on how to make them.

* `alert` : This is what gets called when the Alarm gets triggered. So this is 
the main functionality that you will need to write. If this function throws an 
error the exception is automatically caught and saved to the EMP error log. So 
if you arn't getting the result you expected, look there.


-------------------------------------------------------------------------------


## Plug Attachments ##

Plug-ins are a little bit more complicated because you have a choice between two
types of EmpPlug objects. There are LoopPlugs and SignalPlugs, and there is a 
huge difference between the two. But first a small overview:

* LoopPlugs :  The most used type and the easiest to use. EMP has what's called
a Pull-Loop, where it triggers all LoopPlugs to update on an interval set by 
the user. 
               
* SignalPlugs : These are used for instantaneous updates. These can be used for
security or "to-the-second" alert precisions. These could be used for chat 
relays, program crashes, security monitoring, and more.
                
Now for a more in depth look at them. They both inherit from EmpPlug which 
extends EmpAttachment. But thats not really not that important to how you write 
your own.


### LoopPlugs ####

As stated above, the LoopPlug is the most used type for creating plug-ins. It is
simple to build:

        from empbase.attach.attachments import LoopPlug    
        class MyPlugin(LoopPlug):
            def __init__(self, config):
                LoopPlug.__init__(self, config)
                
            def save(self):
                LoopPlug.save()

            def get_commands(self):
                return []
                
            def get_events(self):
                return []
                
            def update(self, *args):
                pass    
            

The only thing that differs from an EmpAlarm is the last two functions.

* `get_events` : Returns a list of Event objects so the EventManager can trigger
all of the Alarms that have subscribed to them. See below for more information 
about how to use Event objects.

* `update` : This is what gets run when the Pull-Loop calls the plugin. It never 
passes in any parameters, but the *args param is there if you wanted to provide
capability for forcing an update with params. etc.
            
Thats fairly simple right?

                
### SignalPlugs ###

SignalPlugs are exactly the same as LoopPlugs except that instead of an update 
function they have a run function. 

        from empbase.attach.attachments import SignalPlug    
        class MyPlugin(SignalPlug):
            def __init__(self, config):
                SignalPlug.__init__(self, config)
                
            def save(self):
                SignalPlug.save()

            def get_commands(self):
                return []
                
            def get_events(self):
                return []
                
            def run(self):
                pass

The `run` function is called when the SignalPlug is activated by the Daemon. This
is at start up. This means that the SignalPlug gets its own Thread inside the 
Daemon. This also means that if your run function fails to run in any way, it 
will not get re-run unless its de-activated and then activated again, or the 
Daemon is restarted. So code carefully and catch those exceptions!


-------------------------------------------------------------------------------

# Helpful Hints! #


This section has a few hints as to how to get the most out of the EMP Attachment
API! Use it!!


#### What is an EMP file? ####


An EMP file is how the EMP Daemon knows about an Attachment. When it finds an 
EMP file it will parse it and load the Attachment it describes. If you forget
to write an EMP file then it will not be seen and loaded into EMP. If you want
help writing one, check out EmpFileFormat.md in this directory.


#### Using Your Configurations! ####

When your Attachment is instantiated it is given a configuration object that is
saved internally. You can access it via: self.config

The Config object has the following methods:

* `keys()` - returns the list of variable names.
* `get(key, default)` - returns the a keys value, if it doesn't exit, it returns
the default.
* `getint(key, default)` - casts the variable into an integer
* `getfloat(key, default)` - casts the variable into a float
* `getlist(key, default)` - casts the variable into a python list
* `getboolean(key, default)` - casts the variable into a boolean
* `set(key, value)` - set the key equal to the value

You can also utilize it like a list but it will always either return a string
(since thats how its stored) or None. (eg. `self.config['name']`)


#### Using Command Objects ####

Command objects are exceedingly simple to use, they take four parameters, three
of which are optional. Here is an example:

        help = Command("helpme", 
                       trigger=helpscreen, 
                       pargs=(),
                       help="Displays this help screen")

The first parameter is what the user will have to type when targeting the 
Command's Attachment it is for. (E.g. `./emp.py --target=twitter helpme`)

The second parameter `trigger`, is a reference to a function that is called 
automatically when the command is called.

The third parameter is any parameters that you want to supply to the function.
When a command is issued to an attachment it will also have some arguments that
will be sent to the command anyway, `pargs` will be concatenated to the front
of that list. Example:

        def dosomething( *args ):
            ... blah ...
            
        def doOtherThing( one, two, *args ):
            ... blah ...
            
        variable = 1234567
                    
        cmd1 = Command("command1",
                       trigger=dosomething,
                       help="Does something")
                       
        cmd2 = Command("command2",
                        trigger=doOtherThing,
                        pargs=("param1", variable),
                        help="Does something else")
                       
The two parameters given in `pargs` will be used in the function `doOtherThing`
as the first two parameters (eg. `one`, `two`). Anything given by the user will 
be in `*args`. (Which by the way is a tuple if you haven't seen that syntax.)

The fourth parameter to Command, `help`, is a short string that describes what 
the command does. It is what gets displayed when EMP is asked for a complete 
help menu.

For completeness sake, here is an example of how to use them in an Attachment:

            ...
            def __init__(self, conf):
                LoopPlug.__init__(self, conf)
                ...
                self.mycommands = [
                        Command("status",
                                trigger=self.status,
                                help="Get the status of the Plugin."),
                        Command("update",
                                trigger=self.update,
                                help="Force an update."),
                                ... ]

            ...
            
            def get_commands(self):
                return self.mycommands
            ...

*NOTE:* When commands are executing, the return from that function is sent in 
a message back to the thing that triggered it. If there is an Exception of any
form is thrown, it is caught and sent back as an ErrorMsg.


#### Using Event Objects ####

Events is the whole purpose of EMP, it is why it exists. Each Plug has a list
of events it can trigger. This means there can be different types of events  
that can happen. For example: the email plug-in can watch a bunch of different 
email accounts and set up a different event for each one. That way you only 
have to get a text message if you get an email to your work account but a 
little pop up on your screen if you get one to your personal account.

Here is a simple example of setting up an event.

                ...
                def __init__(self, conf):
                    ...
                    self.eventx = Event(self.ID, "Event X")
                    self.myevents = [ self.eventx ]
                    ...

                def get_events(self):
                    return self.myevents
                    
                ...  
                def update(self, *args):
                    ...
                    self.eventx.trigger("Event x happened!")
                    ...
                    
From this example you can see not only how to create events, but also how to 
trigger the events in your Plug-in. The `trigger` function can take an optional
string to send to all those that are subscribed to that Event. When creating 
your Event object you can give it a message too:
                  
               ...   
               self.eventx = Event(self.ID, "Event X",
                                   msg="Event x happened!")
               ...                    
                                   
*NOTE:* YOU HAVE TO PROVIDE THE ATTACHMENT ID AS THE FIRST PARAMETER. This is
important because its how the event gets registered to the Plug-in.
                              
*NOTE:* The second parameter must be constant, its the event's name and it 
shouldn't change because thats how its tied to subscribers. So if they are
generated, like the email plug-in does, make sure it creates them the same
way each time.
                              
#### Attachment Cache Space? ####

One of the major TODOs that I have planned is to provide the ability to save 
more than just simple configuration variables for Attachments. This is what I 
call the Cache Space. 

Attachments will be able to access their own cache to retrieve and save files,
logs, more configuration files, actual caches, serialized objects, dumps, 
databases and more. As long its not needed on a 'per user' level. This means, 
anything that needs to be accessed between users of the daemon, should be saved
here. All personal configurations should be housed elsewhere.
