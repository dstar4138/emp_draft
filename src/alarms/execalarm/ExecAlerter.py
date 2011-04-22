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
import logging
import xml.etree.ElementTree as ET

from empbase.comm.command import Command
from empbase.attach.attachments import EmpAlarm
from alarms.execalarm.execalert import ExecAlert    
    

"""
 The save directory is saved like so:
 .../save/self.ID/alerts.xml
 
 and the alerts xml is layed out like so:
 <alerts>
     <alert id='' group='' msgasparam='' name=''>
         path
     </alert>
     ...
 </alerts>
 
 Commands that might be good:
     add  - add a program, defaults to using msg as param
     rm   - remove a program
     lst  - list all programs currently being used.
     nousemsg - turn msgasparam off
     usemsg - turn msgasparam back on
 
"""
class ExecAlarm(EmpAlarm):
    """ Runs a program when an alert happens."""
    
    def __init__(self, config):
        """Sets up the alerter."""
        EmpAlarm.__init__(self, config)
        self.__savedir = ""
        self.__alerts  = []
        self.__root    = None 
        self.__commands = [Command("add",trigger=self.addAlarm,   help="Adds a program to be turned into an alarm."),
                           Command("rm", trigger=self.removeAlarm,help="Removes a program that ExecAlerter uses."),
                           Command("lst",trigger=self.listAlarms, help="Lists all the programs ExecAlerter has avaliable.")]
      
###########
# Attachment API functions.
###########
    def get_alerts(self): return self.__alerts   
    def get_commands(self): return self.__commands
              
    def activate(self):
        """ Grab all setups and configurations from saves and caches."""
        EmpAlarm.activate(self)
        self.__load() # load all internal variables via saved config files
        self.__setup() # setup all the alarms based on internal vars
        
    def deactivate(self):
        """ We need to reset all of our variables when they get back."""
        EmpAlarm.deactivate(self)
        self.__alerts = []
        self.__root   = None
            
    def save(self):
        """ Save all internal variables as xml file in Attachment's cache. """
        EmpAlarm.save(self)
        try:
            tree = ET.ElementTree(self.__root)
            self.__makeBackup()
            with open(self.__savedir+"alarms.xml", "w") as savefile:
                tree.write(savefile)
            self.__removeBackup()
        except:
            logging.error("Couldn't save the alerts for "+self.ID)
            self.__restoreBackup()
    
##############
# ExecAlerter's command functions.
##############    
    def addAlarm(*args):
        pass
    
    def removeAlarm(*args):
        pass
    
    def listAlarms(*args):
        pass
            
            
###########
# Internal Utility functions.
###########      
    def __setup(self):
        """Loads all the alerts into memory."""
        if self.__root is None: return
        
        _, groups = self.config.getgroups()
        for g in groups.keys():
            self.__alerts.append(ExecAlert(self.ID,
                                           groups[g],
                                           self.__XMLFor(g)))
        # Make sure all the alerts are valid
        self.__alerts = [a for a in self.__alarms if a.isStillValid()]
        # after setting up we dont need the xml anymore.
        self.__root = None
            
    def __XMLFor(self, groupid):
        """Grabs the XML node for an alarm so that it can be created 
        upon activation. 
        """
        if self.__root is None: return None
        for alarm in self.__root.getchildren():
            if "group" in alarm.attrib and  \
               groupid == alarm.attrib["group"]:
                return alarm
        return None
    
    def __load(self):
        """ Load the xml file of the alarms data into memory. """
        self.__savedir = self.config.getMyEmpSaveDir(self.ID)
        path = self.__savedir+"alarms.xml"
        if self.__try_setup_path(path):
            tree = ET.parse(path)
            self.__root = tree.getroot()
        else:pass

#############   
# File IO for backing up and saving.
#############
    def __makeBackup(self):
        try:
            import shutil
            src = self.__savedir+"alarms.xml"
            dst = self.__savedir+"alarms_backup.xml"
            shutil.copy(src, dst)
        except: logging.error("ExectAlerter failed at making a backup.")
     
    def __restoreBackup(self):
        import shutil
        src = self.__savedir+"alarms.xml"
        dst = self.__savedir+"alarms_backup.xml"
        if os.path.exists(dst):
            shutil.copy(dst, src)
            self.__removeBackup()
        else: logging.error("ExecAlerter tried to restore a non-existent backup.")
        
    def __removeBackup(self):
        try: os.remove(self.__savedir+"alarms_backup.xml")
        except: logging.warning("ExectAlerter failed at removing its backup file.")
            
    def __try_setup_path(self,path):
        if os.path.exists(path):
            return os.access(path, os.W_OK)
        else:
            try:
                dirs, _ = os.path.split(path)
                if not os.path.exists(dirs):
                    os.makedirs(os.path.abspath(dirs))
            except: 
                return False
            return True    
        
        
        
        