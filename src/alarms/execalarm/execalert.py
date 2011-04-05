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
from empbase.event.alerts import Alert

class ExecAlert(Alert):
    def __init__(self, aid, cfg, xml):
        #TODO: set these based on cfg
        self.progname = ''
        self.progpath = ''
        self.msgasparam = False
        self.groupid = None
        self.__valid = True
        #LOAD THE CFG AND XML
        self.__load(cfg, xml)
        
        name = "exec_"+self.groupid
        Alert.__init__(self, name, aid)
        
    def __load(self, cfg, xml):
        pass
        
        

    def asCfgDict(self):
        pass
    
    def asXMLNode(self):
        pass
    
    def isStillValid(self):
        return self.__valid
        
    def run(self, eventobj):
        if self.msgasparam:
            pass #TODO: run the program
        else: pass