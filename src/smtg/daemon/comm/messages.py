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
MSG_TYPES = [ERROR_MSG_TYPE, COMMAND_MSG_TYPE, BASE_MSG_TYPE]


def strToMessage(s):
    """ Converts a string into a Message object. Handy way of using this is to
    wrap the incoming string from a DaemonSocket. Make sure the protocol you 
    are using uses JSON, or else this is fairly useless.
    
    SMTG uses JSON for all communication between the interfaces and daemon and 
    any communication between the interface and a plug-in. You most likely wont
    have to worry about this since the API 'should' take care of the 
    communication for you. 
    """
    if s is not str:
        logging.warning("Value given to convert to message was not a string.")
        return None
    try:
        tmp = json.load(s)
    except:
        logging.warning("String parsed was not a message type.")
        return None
    
    type = tmp.get("message")
    if type==ERROR_MSG_TYPE or type==COMMAND_MSG_TYPE or type==BASE_MSG_TYPE:
        return Message(tmp)
    else:
        logging.warning("String parsed was not a message type.")
        return None


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

def makeCommandMsg(cmd, to, args=[], kill=False):
    """ Utility method for quickly creating a command message."""
    return Message({"message":COMMAND_MSG_TYPE,
                    "source":to,
                    "command":cmd,
                    "args":args,
                    "kill":kill})

def makeMessage(source, value):
    """ Utility method for quickly creating a message."""
    return Message({"message":BASE_MSG_TYPE,
                    "source":source,
                    "value":value})


class Message(dict):
    """ Message objects are used to make communication easier in the interface
    API. If you are writing your own interface in another language then it might
    be a good idea to get an idea of how these dictionaries are constructed.
    Please see the below description.
    """
    
    def __init__(self, value):
        """ Initializes the message with a dictionary object. """
        self.value = value
        
    def getType(self):
        """ Gets the type of the message, which is one of the following:
        error, command, or base. These can be checked using the globals
        given: `ERROR_MSG_TYPE`, `COMMAND_MSG_TYPE` and `BASE_MSG_TYPE`
        """
        return self.value.get("message")
    
    def getValue(self):
        """Gets the value that the message is carrying. For Command messages 
        this is the name of the plug-in that the command is aimed towards. For
        either Base or Error messages, the value is just the
        """
        if self.getType()==COMMAND_MSG_TYPE:
            return self.get("source")
        else:
            return self.get("value")
        
    def __str__(self):
        try:
            return json.dump(self)
        except Exception as e:
            logging.error(e)
            raise e
        
"""
The below is the JSON structure for the message objects used in the 
communication API:

#######
  Command Message Structure
#######
    Commands are used by interfaces for making plug-ins do what they want them
to. So commands can vary by plug-in, see the plug-in API for handling these.
    
        {"message" : "cmd",
         "source"  : "plugin-name"/null,
         "command"    : "name of command",
         "args"    : ["list", "of", "arguments"],
         "kill"    : true/false }
         
  Explanation:
    - message: this tells smtg that it is a command type message to parse.
    - source: this is the name of the plugin to run the command through, or
        if source is not present, or its set to null, smtg tries to
        run the command.
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
                {"message":"cmd","name":"stats","kill":true}
    - Heres a more complicated one to update your facebook status through an
      imaginary plugin:
          {"message":"cmd","source":"my-fb-plugin",
            "name":"updateStatus","args":["This is cool!!!"]}
    - Another example, this time asking the daemon to list the plugins that
      are attached to it:
                 {"message":"cmd","name":"list-plugins"}
                 
#######
  Error Message Structure
#######                 
     Error messages can come from anywhere, but most typically from the 
plug-ins. Occasionally there may be a daemon error in which case the source 
will be null.
    
        {"message" : "err",
         "source"  : "plugin-name"/null,
         "code"    : 1823012,
         "value"   : "error message",
         "dead"    : true/false,
         "kill"    : true/false }
         
  Explanation:
    - message: this tells you that it is an error type message to parse.
    - source: the source of the error, if this value is missing or set to null
        it means the error came from smtgd itself.
    - code: some errors are very common, so instead of you having to parse the
        value field, there is also this code information.
    - value: the value of the error, normally human readable.
    - dead: if the daemon crashed, or is in the process of, it will set this
        to true.
    - kill: if the connection needs to be terminated, this will be set to true.    


#######
  Base Message Structure
#######                 
     <base> messages are structured as JSON objects. <base> messages are the 
bare minimum message that can be sent. These aren't Here is the their 
structure:
    
        {"message" : "base",
         "source"  : "plugin-name",
         "value"   : value }
         
  Explanation:
    - message: this tells you that it is a base type message to parse.
    - source: the source of the message. 
    - value: the value of the message. This can be anything from an array of
        values, to an float value, to a serialized object inside it.
  Warning:
    I don't really recommend using this type of message since it isn't really
    easily parsed. In fact the only real use I can foresee to use this with is 
    for sending an interface a port number to connect to an AlertPlugin object
    thread.
"""
      
        
        
        
        
        