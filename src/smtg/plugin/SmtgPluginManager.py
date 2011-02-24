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
#import logging
#import smtg.daemon.comm.routing as routing
from smtg.VariablePluginManager import VariablePluginManager
from smtg.plugin.smtgplugin import LoopPlugin, SignalPlugin


# this is the default plugin descriptor extention. See yapsy.PluginInfo
PLUGIN_EXT = "smtg-plugin"

# this is the default plugin categories
PLUGIN_CATEGORIES = {"Feeds": LoopPlugin,
                     "Signals": SignalPlugin}


class SmtgPluginManager(VariablePluginManager):
    """The plug-in manager for the SMTG daemon, This is never directly 
    accessed by the users, only through the daemon itself. If config variables
    need to be changed, access the daemon and ask it to change it. If a plug-in
    variable needs to be changed, then ask the plug-in. 
    """
    
    def __init__(self, plugin_dirs, cfg_p):
        """Create the Plug-in Manager for SMTG."""
        VariablePluginManager.__init__( self, cfg_p,
                                        categories_filter=PLUGIN_CATEGORIES,
                                        directories_list=plugin_dirs,
                                        plugin_info_ext=PLUGIN_EXT )


    def isPluginOk(self, info):
        """ Don't load the plug-in if there's a variable called 'daemon-load'
        in the plug-ins variable section and its set to false.
        """ 
        try: return bool(info.defaults.get("daemon-load",True))
        except: return True


    def activatePlugins(self):
        """Activates all the valid LoopPlugins, and any SignalPlugins that 
        require an auto-start.
        """
        #TODO: implement SmtgPluginManager.activatePlugins() to handle config files and alert plugins...
        # right now i'll just activate everything.
        plugs = self.getAllPlugins()
        for plug in plugs:
            plug.plugin_object.activate()
        
    def getLoopPlugins(self):
        """ Get all the loop plug-ins that are loaded. This is used in the pull
        loop thread for updating all of them. 
        """
        return sorted( self.getPluginsOfCategory("Feeds"),
                       key=lambda x: x.plugin_object.update_importance)


    def getSignalPlugins(self):
        """ Utility function for getting all the signal plugins. """
        return sorted( self.getPluginsOfCategory("Signals"),
                       key=lambda x: x.plugin_object.update_importance)

    def getPluginNames(self):
        """ Get all the names of the plug-ins."""
        names = {}
        for plugin in self.getAllPlugins():
            names[plugin.plugin_object.ID] = (plugin.plugname, plugin.name)
        return names
    
    def getPluginIDs(self):
        """ Get all the plug-ins IDs."""
        ids = []
        for plugin in self.getAllPlugins():
            ids.append(plugin.plugin_object.ID)
        return ids
    
    def getPluginID(self, name):
        """ Get the plug-in ID given a plug-in's name. """
        for plugin in self.getAllPlugins():
            if name == plugin.name:
                return plugin.plugin_object.ID
        return None

