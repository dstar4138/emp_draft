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

from smtg.plugin.smtgplugin import LoopPlugin, SignalPlugin
from yapsy.FilteredPluginManager import FilteredPluginManager


# this is the default plugin descriptor extention. See yapsy.PluginInfo
PLUGIN_EXT = "smtg-plugin"

# this is the default plugin categories
PLUGIN_CATEGORIES = {"Feeds": LoopPlugin,
                     "Signal": SignalPlugin}


class SmtgPluginManager(FilteredPluginManager):
    """The plugin manager for the SMTG daemon.
    """
    
    def __init__(self, plugin_dirs, commreader=None):
        """ """
        FilteredPluginManager.__init__(self, 
                                        categories_filter=PLUGIN_CATEGORIES,
                                        directories_list=plugin_dirs,
                                        plugin_info_ext=PLUGIN_EXT)
        self.msg_handler = commreader
        
        
    def activatePlugins(self):
        """Activates all the valid LoopPlugins, and any SignalPlugins that 
        require an auto-start.
        """
        #TODO: implement SmtgPluginManager.activatePlugins() to handle config files and alert plugins...
        # right now i'll just activate everything.
        plugs = self.getAllPlugins()
        print("plugs",plugs)
        for plug in plugs:
            plug.plugin_object.activate()
    
    def collectPlugins(self):
        self.locatePlugins()
        self.loadPlugins(plugin_args=self.msg_handler)
        
    def getLoopPlugins(self):
        """ Run all the feed plugin's pull loops. """
        return self.getPluginsOfCategory("Feeds") #TODO: sort based on importance
    
    
    def runCommand(self,plugin_name,cmd):
        """ Search for the plugin with the name given and send the 
        command to it, then return the result as a message (see iAPI). 
        """
        pass
    
    #XXX: does this method need to be here? an we send commands to the plugin manager?
    def runAlertThread(self, plugin_name):pass
    
    # TODO: define the filtering method
    # def isPluginOk(self, info): return True