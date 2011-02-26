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

from smtg.attach.VariablePluginManager import VariablePluginManager
from smtg.attach.attachments import Alerter, LoopPlugin, SignalPlugin

# the internal categories that the attachment manager can handle.
ATTACH_CAT = {"Alerters":Alerter,
              "Loops": LoopPlugin,
              "Signals": SignalPlugin}

# the expected extension of description files for SMTG attachments
ATTACH_EXT = "smtg"

class AttachmentManager(VariablePluginManager):
    
    def __init__(self, dirs, conf):
        VariablePluginManager.__init__( self, conf,
                                        categories_filter=ATTACH_CAT,
                                        directories_list=dirs,
                                        plugin_info_ext=ATTACH_EXT )
        
        
    def activatePlugins(self):
        """ Activates the attachments that want to be activated on
        start-up. The rest are in idle state until hand-activated by 
        the user.
        """
        for attach in self.getAllPlugins():
            if attach.plugin_object.makeactive:
                attach.plugin_object.activate()
                
    def getLoopPlugins(self):
        """ Get all the loop plug-ins that are loaded. This is used in the pull
        loop thread for updating all of them. 
        """
        return sorted( self.getPluginsOfCategory("Loops"),
                       key=lambda x: x.plugin_object.update_importance)
        
    def getSignalPlugins(self):
        """ Utility function for getting all the signal plugins. """
        return self.getPluginsOfCategory("Signals")
    
    def getAlerters(self):
        """ Utility function for getting all the Alerter attachments. """
        return self.getPluginsOfCategory("Alerters")
    
    def getPlugs(self):
        return self.getPluginsOfCategory("Signals").extend(
                            self.getPluginsOfCategory("Loops"))
        
    def getAllNames(self):
        """ Returns a dictionary of IDs to (plugname, name) for every 
        attachment.
        """
        names = {}
        for attach in self.getAllPlugins():
            names[attach.plugin_object.ID] = (attach.plugname, attach.name)
        return names
    
    def getAlerterNames(self):
        names = {}
        for attach in self.getAlerters():
            names[attach.plugin_object.ID] = (attach.plugname, attach.name)
        return names
    
    def getPluginNames(self):
        names = {}
        for attach in self.getPlugs():
            names[attach.plugin_object.ID] = (attach.plugname, attach.name)
        return names
    
    
    def getAttachmentID(self, name):
        """ If the name given is one of the attachment's name or plugname, then
        it will return its ID, otherwise it will return None.
        """
        for attach in self.getAllPlugins():
            if name == attach.name or name == attach.plugname:
                return attach.plugin_object.ID
        return None
    
    
    