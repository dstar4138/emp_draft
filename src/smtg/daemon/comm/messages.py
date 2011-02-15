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

import json
import logging


# Can be used for type checking.
ERROR_MSG_TYPE   = "err"
COMMAND_MSG_TYPE = "cmd"
BASE_MSG_TYPE    = "base"
ALERT_MSG_TYPE   = "alrt"
MSG_TYPES = [ERROR_MSG_TYPE, COMMAND_MSG_TYPE, BASE_MSG_TYPE, ALERT_MSG_TYPE]


def strToMessage(s):
    """ Converts a string into a Message object. Handy way of using this is to
    wrap the incoming string from a DaemonSocket. Make sure the protocol you 
    are using uses JSON, or else this is fairly useless.
    
    SMTG uses JSON for all communication between the interfaces and daemon and 
    any communication between the interface and a plug-in. You most likely wont
    have to worry about this since the API 'should' take care of the 
    communication for you. 
    """
    try:
        tmp = json.loads(s)
        logging.debug("value JSON unloaded was: %s" % tmp)
    except Exception as e:
        logging.error("Error parsing with JSON: %s" % e)
        return None
    
    if tmp.get("message") in MSG_TYPES:
        return Message(tmp)
    else:
        logging.error("String parsed was not a message type: %s"% tmp.getType())
        return None


def makeMsg(value, source=None, dest=None):
    """ Utility method for quickly creating a base message."""
    return Message({"message":BASE_MSG_TYPE,
                    "source":source,
                    "dest": dest,
                    "value":value})

def makeAlertMsg(value, source, dest=None, title="", args=None):
    """ Utility method for quickly creating an alert message."""
    return Message({"message":ALERT_MSG_TYPE,
                    "source":source,
                    "dest": dest,
                    "title":title,
                    "value":value,
                    "args":args})

def makeCommandMsg(cmd, source, dest=None, args=[], kill=False):
    """ Utility method for quickly creating a command message."""
    return Message({"message":COMMAND_MSG_TYPE,
                    "source":source,
                    "dest":dest,
                    "command":cmd,
                    "args":args,
                    "kill":kill})

def makeErrorMsg(value, source=None, code=None, dead=False, kill=False):
    """ Utility method for quickly creating an error message."""
    if code==None: 
        return Message({"message":ERROR_MSG_TYPE,
                    "source":source, 
                    "dead":dead,
                    "kill":kill})
    else:    
        return Message({"message":ERROR_MSG_TYPE,
                    "source":source, 
                    "code":code,
                    "dead":dead,
                    "kill":kill})


class Message():
    """ Message objects are used to make communication easier both internally 
    and external to the daemon. Please do not use this class directly when 
    writing your Interfaces or Plug-ins as this internally may change. Instead
    use the above constructor methods.
    
    If you are writing your own interface in another language then it might
    be a good idea to get an idea of how these dictionaries are constructed.
    Please see the below description.
    """
    
    def __init__(self, value):
        """ Initializes the message with a dictionary object. """
        self.value = value
        
    def getSource(self):
        """ Returns the source of the message """
        return self.get("source")
    
    def getDestination(self):
        """ Returns the destination of the message """
        return self.get("dest")

    def getType(self):
        """ Gets the type of the message, which is one of the following:
        error, command, or base. These can be checked using the globals
        given: `ERROR_MSG_TYPE`, `COMMAND_MSG_TYPE` and `BASE_MSG_TYPE`
        """
        return self.get("message")
    
    def getValue(self):
        """Gets the value that the message is carrying. For Command messages 
        this is the name of the command that is wanted to run. For either Base 
        or Error messages, the value is just the
        """
        if self.getType()==COMMAND_MSG_TYPE:
            return self.get("command")
        else:
            return self.get("value")
        
    def __getattr__(self,name):
        # get all the methods from the internal dictionary. 
        #Message is just a decorator to dict.
        return getattr(self.value,name)
    
    def __str__(self):
        try: #output in compact form.
            return json.dumps(self.value, separators=(',', ':'))
        except Exception as e:
            logging.exception(e)
        
"""
The below is the JSON structure for the message objects used in the 
communication API:
#######
  Base Message Structure
#######                 
     <base> messages are structured as JSON objects. <base> messages are the 
bare minimum message that can be sent. These are discuraged, since they are 
more difficult to parse genericly for Interfaces. But here is the their 
structure:
    
        {"message" : "base",
         "source"  : "obj-id"/null,
         "dest"    : "obj-id"/null,
         "value"   : value }
         
  Explanation:
    - message: this tells you that it is a base type message to parse.
    - source: the source of the message. 
    - dest: the destination to send the message to.
    - value: the value of the message. This can be anything from an array of
        values, to an float value, to a serialized object inside it.

#######
  Alert Message Structure 
#######
  Alert messages are structured as JSON objects. Alerts are treated differently
than all the other types of messages since they don't NEED to have a destination.
If a destination is missing, then the alert is sent out to all Alerters and 
Interfaces. If the destination is present, then it MUST be a valid Alerter id.

        {"message" : "alrt",
         "source"  : "obj-id",
         "dest"    : "obj-id"/null,
         "title"    : "name of alert",
         "value"    : "value of alert",
         "args"    : ["list", "of", "arguments"]/null}
  Explanation:
    - message: this tells smtg that it is a command type message to parse.
    - source: this is the id of the registered object that the alert is coming from.
    - dest: just like source, but this can be set to null, or not exist. If either
        of these is the case the alert will go to everyone in the Router's registry
    - title: this is the name of the alert, not really neccessary. 
    - value: this is not neccessary all the time
    - args: this is a list of arguments for the alert. If there are no 
        arguments needed for the alert args can be ignored or you can use
        a null.
 
#######
  Command Message Structure
#######
    Commands are used by interfaces for making plug-ins do what they want them
to. So commands can vary by plug-in, see the plug-in API for handling these.
    
        {"message" : "cmd",
         "source"  : "obj-id",
         "dest"    : "obj-id"/null,
         "command" : "name of command",
         "args"    : ["list", "of", "arguments"],
         "kill"    : true/false }
         
  Explanation:
    - message: this tells smtg that it is a command type message to parse.
    - source: this is the id of the registered object that the cmd is coming from.
    - dest: just like source, but this can be set to null, or not exist. If either
        of these is the case SMTG itself will try to execute it.
    - name: this is the name of the command to run at the source.
    - args: this is a list of arguments for the command. If there are no 
        arguments needed for the command args can be removed or you can use
        a null.
    - kill: this tells smtg that we only want to run this one last command and 
        then we will kill our connection. Typically this is used when querying
        for the daemon status. This is optional as it defaults to false.
  Examples:
    - Here is an example to just grab the daemon stats real quick after the 
      connecting process is complete:
        {"message":"cmd","source":"i0934287342","name":"stats","kill":true}
    - Heres a more complicated one to update your facebook status through an
      imaginary plugin:
          {"message":"cmd","source":"i0934287342",
           "dest":"p934728","name":"updateStatus",
           "args":["This is cool!!!"]}
    - Another example, this time asking the daemon to list the plugins that
      are attached to it:
          {"message":"cmd","source":"i0934287342"."name":"list-plugins"}
             
#######
  Error Message Structure
#######                 
     Error messages can come from anywhere, but most typically from the 
plug-ins. Occasionally there may be a daemon error in which case the source 
will be null.
    
        {"message" : "err",
         "dest"    : "obj-id",
         "source"  : "obj-id"/null,
         "code"    : 1823012,            ## Remove??
         "value"   : "error message",
         "dead"    : true/false,
         "kill"    : true/false }
         
  Explanation:
    - message: this tells you that it is an error type message to parse.
    - dest: the object to send the error message to.
    - source: the dest of the error, if this value is missing or set to null
        it means the error came from smtgd itself.
    - code: some errors are very common, so instead of you having to parse the
        value field, there is also this code information.
    - value: the value of the error, normally human readable.
    - dead: if the daemon crashed, or is in the process of, it will set this
        to true.
    - kill: if the connection needs to be terminated, this will be set to true.    
"""
      
        
        
        
        
        