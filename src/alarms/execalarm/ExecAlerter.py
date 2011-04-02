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
from empbase.attach.attachments import EmpAlarm
from alarms.execalarm.execalert import ExecAlert    
    

class ExecAlarm(EmpAlarm):
    """ Runs a program when an alert happens."""
    
    def __init__(self, config):
        """Sets up the alerter."""
        EmpAlarm.__init__(self, config)
        self.__alerts = []
        
    def get_alerts(self):
        return self.__alerts   
        
    def activate(self):
        EmpAlarm.activate(self)
        self.__loadXML()
        self.init()
        
    def init(self):
        _, groups = self.config.getgroups()
        for g in groups.keys():
            self.__alerts.append(ExecAlert(self.ID,
                                           groups[g],
                                           self.__XMLFor(g)))
    def save(self):
        EmpAlarm.save(self)
        
            
    def __XMLFor(self, groupid):
        pass
    
    def __loadXML(self):
        self.config.getMyEmpSaveDir(self.ID)