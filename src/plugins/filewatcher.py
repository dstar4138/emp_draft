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
import smtg.comm.routing as routing
from smtg.comm.messages import makeMsg, makeAlertMsg,  \
                                      makeErrorMsg, COMMAND_MSG_TYPE
from smtg.attach.attachments import LoopPlugin

class FileWatcher(LoopPlugin):
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
        LoopPlugin.__init__(self, conf)
        self._files = {}
        if "files" in self.config:
            if self.config["files"] != "": 
                for file in str(self.config["files"]).split(","):
                    try: self._files[file] = os.path.getmtime(file)
                    except Exception as e:
                        logging.error("%s had an error getting the file time" % e)
                        break
        self._commands =["help","update","status","files","add","rm"]
    
    def handle_msg(self, msg):
        try:
            if msg.get("message") == COMMAND_MSG_TYPE:
                value = msg.get("command")
                dest = msg.get("source")
                if value in self._commands:
                    if value == "update": 
                        self.update(msg.get("args"))
                    elif value == "status": 
                        if self.check_status():
                            routing.sendMsg(makeMsg("File Watcher is running!",self.ID,dest))
                        else:
                            routing.sendMsg(makeMsg("File Watcher is not running!",self.ID,dest))
                    elif value == "files": 
                        self.get_files(dest)
                    elif value == "add": 
                        self.add_file(dest,msg.get("args"))
                    elif value == "rm": 
                        self.rm_file(dest,msg.get("args"))
                else: routing.sendMsg(makeErrorMsg("command '"+value+"' did not exist", self.ID, dest))
            #else it is ignored.
        except Exception as e:
            logging.exception(e)
            try:routing.sendMsg(makeErrorMsg("command did not exist", self.ID,msg.get("source")))
            except: routing.sendMsg(makeErrorMsg("command did not exist", self.ID,None))
    
    def get_commands(self):
        return {"update": "forces an update, if a file is given then it will update just that one.",
                "status": "checks whether the plug-in is activated.",
                "files": "returns a list of the files being watched.",
                "add": "add file x to list of files being watched.",
                "rm": "remove file x from list, x being an index or the file name."}
    
    def check_status(self):
        """ Returns whether or not this plug-in is activated or not. """
        return self.is_activated
   
    def update(self, *args):
        if len(args) > 0: #update the one given
            if args[0] in self._files:
                if self._files.get(args[0]) < os.path.getmtime(args[0]):
                        self._files[args[0]] = os.path.getmtime(args[0])
                        routing.sendMsg(makeAlertMsg("File '"+args[0]+"' changed at "+str(self._files[args[0]])+"!", self.ID))
            #ignore the fact that the file doesn't exist, if this problem arises.
        else:#update all
            for file in list(self._files.keys()):
                try: 
                    if self._files.get(file) < os.path.getmtime(file):
                        self._files[file] = os.path.getmtime(file)
                        routing.sendMsg(makeAlertMsg("File '"+file+"' changed at "+str(self._files[file])+"!", self.ID))
                except Exception as e: logging.exception(e)
                    
        
    def get_files(self, dest):
        """ Gets the internal list of files """
        routing.sendMsg(makeMsg(list(self._files.keys()), self.ID, dest))
    
    def add_file(self, dest, args):
        try:
            self._files[args[0]] = int(time.time())
            routing.sendMsg(makeMsg("success",self.ID,dest))
        except:
            routing.sendMsg(makeErrorMsg("couldn't add file.",self.ID,dest))

    def rm_file(self, dest, args):
        try:
            for key in self._files.keys():
                if key == args[0]:
                    self._files.remove(key)
                    break
            routing.sendMsg(makeMsg("success",self.ID,dest))
            
        except:
            routing.sendMsg(makeErrorMsg("couldn't remove file.",self.ID,dest))


    def save(self):
        """Pushes the internal variables to the config variable for saving! """
        LoopPlugin.save(self)
        filestring = ""
        count = len(self._files.keys())
        for file in self._files.keys():
            filestring+=file
            count-=1
            if count>0:filestring+=","
        self.config["files"] = filestring

