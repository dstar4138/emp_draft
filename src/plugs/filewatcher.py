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
import time
import logging

from empbase.comm.command        import Command
from empbase.registration.events import Event
from empbase.attach.attachments  import LoopPlug


class FileWatcher(LoopPlug):
    """ Watches a list of local files for changes. Any changes are added 
    to the internal alert queue. The commands that can be sent to this are:
        update  - forces an update
        status  - checks whether the plug-in is activated
        files   - returns a list of the files being watched
        add x   - add file x to list of files being watched
        rm x    - remove file x from list, x being an index or the file name.
    The actual changes to the files are not known since they are not cached
    or stored in anyway. This can change if you want to write a more advanced
    FileWatcher class.
    """
    def __init__(self, conf):
        LoopPlug.__init__(self, conf)
        self._files = {}
        for file in self.config.getlist("files",[]):
            try: self._files[file] = os.path.getmtime(file)
            except Exception as e:
                logging.error("%s had an error getting the file time" % e)
                break
        self._commands =[Command("update", trigger=self.update, help="forces an update"),
                         Command("status", trigger=self.check_status, help="checks whether the plug is activated"),
                         Command("files", trigger=self.get_files, help="returns a list of files being watched"),
                         Command("add", trigger=self.add_file, help="add file x o list of files being watched"),
                         Command("rm", trigger=self.rm_file, help="remove file x from list, x being an index or the file name.")]
        # The file watcher only has one event...
        self.EVENT_filechange = Event(self.ID, "filechange")
        self._events = [self.EVENT_filechange]
    
    
    def get_commands(self):
        return self._commands
    
    def get_events(self):
        return self._events
    
    def check_status(self):
        """ Returns whether or not this plug-in is activated or not. """
        return self.is_activated
   
    def update(self, *args):
        if len(args) > 0: #update the one given
            if args[0] in self._files:
                if self._files.get(args[0]) < os.path.getmtime(args[0]):
                        self._files[args[0]] = os.path.getmtime(args[0])
                        self.EVENT_filechange.trigger("File '"+args[0]+"' changed at "+str(self._files[args[0]])+"!")
            #ignore the fact that the file doesn't exist, if this problem arises.
        else:#update all
            for file in list(self._files.keys()):
                try: 
                    if self._files.get(file) < os.path.getmtime(file):
                        self._files[file] = os.path.getmtime(file)
                        self.EVENT_filechange.trigger("File '"+file+"' changed at "+str(self._files[file])+"!")
                except Exception as e: logging.exception(e)
                    
        
    def get_files(self):
        """ Gets the internal list of files """
        return list(self._files.keys())
    
    def add_file(self, dest, args):
        try:
            self._files[args[0]] = int(time.time())
            return "success"
        except:
            raise Exception("couldn't add file.")

    def rm_file(self, dest, args):
        try:
            for key in self._files.keys():
                if key == args[0]:
                    self._files.remove(key)
                    break
                
            return "success"
        except:
            raise Exception("couldn't add file.")

    def save(self):
        """Pushes the internal variables to the config variable for saving! """
        LoopPlug.save(self)
        filestring = ""
        count = len(self._files.keys())
        for file in self._files.keys():
            filestring+=file
            count-=1
            if count>0:filestring+=","
        self.config.set("files", filestring)

