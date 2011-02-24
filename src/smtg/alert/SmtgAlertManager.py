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

from smtg.alert.smtgalert import Alerter
from smtg.VariablePluginManager import VariablePluginManager

# this is the default alert descriptor extention. See yapsy.PluginInfo
ALERTER_EXT = "smtg-alerter"

# this is the default alert categories
ALERTER_CATEGORIES = {"Alerts": Alerter}

class SmtgAlertManager(VariablePluginManager):
    """ Handles alerters as similarly to how plug-ins work. """
    
    def __init__(self,alrtdirs,conf):
        VariablePluginManager.__init__( self, conf,
                                        categories_filter=ALERTER_CATEGORIES,
                                        directories_list=alrtdirs,
                                        plugin_info_ext=ALERTER_EXT )
    def isPluginOk(self, info): 
        """Inhereted from FilteredPluginManager, used to tell whether or
        not an alert is ok to load. This relies on whether the configuration
        says its ok to autoload."""
        return True #FIXME: fix how the alerts are installed
        
        
    def activatePlugins(self):
        """Activates all the valid LoopPlugins, and any SignalPlugins that 
        require an auto-start.
        """
        #TODO: implement SmtgPluginManager.activatePlugins() to handle config files and alert plugins...
        # right now i'll just activate everything.
        alerts = self.getAllPlugins()
        for alert in alerts:
            alert.plugin_object.activate()
            
           
    def getAlerterNames(self):
        """ Get all the names of the plug-ins."""
        names = {}
        for alerter in self.getAllPlugins():
            names[alerter.plugin_object.ID] = (alerter.plugname, alerter.name)
        return names
            
    def getAlerterIDs(self):
        """ Get all the alerters IDs."""
        ids = []
        for alerter in self.getAllPlugins():
            ids.append(alerter.plugin_object.ID)
        return ids
    
    def getAlerterID(self, name):
        """ Get the alerter's ID given a plug-in's name. """
        for alerter in self.getAllPlugins():
            if name == alerter.name:
                return alerter.plugin_object.ID
        return None
    
    