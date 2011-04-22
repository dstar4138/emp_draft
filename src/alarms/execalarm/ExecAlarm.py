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
from alarms.execalarm.execalert import ExecAlert, ConstructAlert  
    

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
     nousemsg - turn msgasparam off             <------NOT IMPLEMENTED
     usemsg - turn msgasparam back on           <------NOT IMPLEMENTED
     rename - rename a program path
 
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
                           Command("rm", trigger=self.removeAlarm,help="Removes a program that ExecAlarm uses."),
                           Command("lst",trigger=self.listAlarms, help="Lists all the programs ExecAlarm has available."),
                           Command("rename",trigger=self.renameAlarm, help="Rename the name that ExecAlarm uses.")]
      
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
            logging.error("Couldn't save the alerts for %s", self.ID)
            self.__restoreBackup()
    
##############
# ExecAlerter's command functions.
##############    
    def addAlarm(self, *args):
        if len(args) == 0:
            raise Exception("Command 'add' needs a full program path to add an alert.")
        path, name, msgasparam = args[0], "", ""
        if not os.path.exists(path):
            raise Exception("Path to program does not exist: %s", path)
        if len(args) > 1:
            name = args[1]
            if len(args) > 2: msgasparam = args[2]
        else: name = os.path.basename(path)
        if msgasparam in self.config.BOOL_CHOICES:
            msgasparam = self.config.BOOL_CHOICES[msgasparam]
        else: msgasparam = False
        try:
            alert = ExecAlert(self.ID, self.__generateGID(),
                              path, name, msgasparam)
            alert.register()# registers the alert with the eventmanager and registry
            self.__alerts.append(alert)
            return "Successfully added new alert to ExecAlarm."
        except: raise #explicitly raising the same err to show where the err is from
    
    def __generateGID(self):
        """ Generates a group id for all the alerts"""
        try:ls = self.listAlarms()
        except: return '0'
        import itertools
        for i in itertools.count(1):
            if i not in ls: return str(i)
    
    
    def removeAlarm(self, *args):
        """ Removal command, facilitates alert removal while EMP is running
        and ExecAlarm is attached.
        """
        if len(args) == 0:
            raise Exception(
                "Command 'rm' needs a id or the program name to remove.")
        removed = False
        for alert in self.__alerts:
            if args[0] == alert.groupid or \
               args[0] == alert.progname:
                self.__alerts.remove( alert )
                removed = True
        if not removed:
            raise Exception(
               "Could not remove program, are you sure you have the right id? "
               +"Try using the 'lst' command.")
        else: return "Removal was a success."
    
    def listAlarms(self, *args):
        """ Lists all the alarms with their ID or name. """
        ret = {}
        type, types = 'id', ['id','names']
        if len(args)>0 and args[0] in types: type = args[0]
        for alert in self.__alerts:
            if type=='names':
                ret[alert.progname] = alert.progpath
            else:ret[alert.groupid] = alert.progpath
        if len(ret) == 0:
            raise Exception("There are no alerts!")
        return ret
            
            
    def renameAlarm(self, *args):
        if len(args) < 2:
            raise Exception("Command 'rename' needs either an ID or an old name, and then a new name.")
        old, new, found = args[0], args[1], False
        for alert in self.__alerts:
            try:
                if alert.progname == old or alert.groupid == old:
                    alert.progname = new
                    found = True; break
            except:continue; 
        if found: return "Successfully renamed."
        else: raise Exception("Couldn't find program to rename. Use 'lst' command.")
            
###########
# Internal Utility functions.
###########      
    def __setup(self):
        """ Loads all the alerts into memory. Must be called after __load. """
        if self.__root is None: return
        
        _, groups = self.config.getgroups()
        for g in groups.keys():
            self.__alerts.append(ConstructAlert(self.ID, g,
                                                groups[g],
                                                self.__XMLFor(g)))
        # Make sure all the alerts are valid
        self.__alerts = [a for a in self.__alerts if a.isvalid]
        # after setting up we dont need the xml anymore.
        self.__root = None
            
    def __XMLFor(self, groupid):
        """ Grabs the XML node for an alarm so that it can be created 
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
