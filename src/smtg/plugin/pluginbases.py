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

from smtg.daemon.comm.messages import Message, makeErrorMsg, BASE_MSG_TYPE
from smtg.plugin.smtgplugin import FeedPlugin, MID_IMPORTANCE

class FileWatcher(FeedPlugin):
    """ Watches a list of local files for changes. Any changes are added 
    to the internal alert queue. The commands that can be sent to this are:
        help x  - get help on command x, x is optional
        update  - forces an update
        status  - checks whether the plug-in is activated
        files   - returns a list of the files being watched
        cfile x - gets the most recent changes to the file x
    """
    def __init__(self, files, name="File Watcher", importance=MID_IMPORTANCE):
        FeedPlugin.__init__(self, name, importance)
        self._files = files # the internal files to watch.
        self._commands =["help","update","status","files","cfile"]
    
    def _check_status(self):
        """ Returns whether or not this plug-in is activated or not. """
        return self.is_activated
    
    def _get_commands(self):
        return Message({"message":BASE_MSG_TYPE, 
                        "source":self.__name__,
                        "value":self._commands})
        
    def _run_commands(self, msg):
        if msg is not dict and msg.get("message") != "cmd":
            return makeErrorMsg("message was invalid", source=self.__name__)
        
        if msg.get("value") in self._commands:
            value = msg.get("value")
            if value == "help": self.help(msg.get("args"))
            elif value == "update": self.update(msg.get("args"))
            elif value == "status": self._check_status()
            elif value == "files": self.get_files()
            elif value == "cfile": self.get_file(msg.get("args"))
            else: return makeErrorMsg("command did not exist", source=self.__name__)
        else:
            return makeErrorMsg("command did not exist", source=self.__name__)
        
    def _update(self, args=[]):
        pass # TODO: implement filewatcher.update
        
        
    def help(self, args):
        pass # TODO: implement filewatcher.help
    
    def get_files(self):
        """ Gets the internal list of files """
        return Message({"message":BASE_MSG_TYPE, 
                        "source":self.__name__,
                        "value":self._files})
    
    def get_file(self, args):
        pass # TODO: implement filewatcher.get_file