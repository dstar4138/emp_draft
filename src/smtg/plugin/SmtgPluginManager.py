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

from smtg.plugin.smtgplugin import FeedPlugin, AlertPlugin
from yapsy.PluginManagerDecorator import PluginManagerDecorator

#
# loads the plug-ins and is able to provide the daemon/server with up-to-date
# alert feed-back on any plug-in loaded.
#

PLUGIN_CATEGORIES = {"Feeds": FeedPlugin,
                     "Alerts": AlertPlugin}

class SmtgPluginManager(PluginManagerDecorator):
    """The plugin manager for the SMTG daemon.
    """
    
    def __init__(self, plugin_dirs):
        """ """
        PluginManagerDecorator.__init__(self, 
                                        categories_filter=PLUGIN_CATEGORIES,
                                        directories_list=plugin_dirs,
                                        plugin_info_ext="smtg-plugin")
        
        
    def pullFeeds(self):
        """ Run all the feed plugin's pull loops. """
        pass
    
    
    def runCommand(self,plugin_name,cmd):
        """ Search for the plugin with the name given and send the 
        command to it, then return the result as a message (see iAPI). 
        """
        pass
    
    #XXX: does this method need to be here? an we send commands to the plugin manager?
    def runAlertThread(self, plugin_name):pass