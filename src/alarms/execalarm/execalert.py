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
from subprocess import Popen
from empbase.event.alerts import Alert

def ConstructAlert( id, cfgdata, xmldata ):
    pass

class ExecAlert(Alert):
    def __init__(self, aid, groupid, progpath, progname, msgasparam):
        self.progname = progname
        self.progpath = progpath
        self.msgasparam = msgasparam
        self.groupid = groupid
        self.isvalid = True
        
        name = "exec_"+self.groupid
        Alert.__init__(self, name, aid)

    def asCfgDict(self):
        pass
    
    def asXMLNode(self):
        pass
        
    def run(self, eventobj):
        logging.debug("Launching program %s", self.progname)
        if self.msgasparam:
            pid = Popen([self.progpath, eventobj.msg ]).pid
        else: 
            pid = Popen([self.progpath]).pid
        logging.debug("Launched '%s', pid=%s",(self.progname, pid))