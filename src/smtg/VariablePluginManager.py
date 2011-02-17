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
import sys
import logging
from yapsy.IPlugin import IPlugin
from yapsy.FilteredPluginManager import FilteredPluginManager

class VariablePluginManager(FilteredPluginManager):
    """Loads Plugins with a SmtgConfigParser and a CommReader, and also can
    filter plugins like the FilteredPluginManager.
    """
    
    def __init__(self, cfg_p, commreader, decorated_manager=None,
                                          categories_filter={"Default":IPlugin}, 
                                          directories_list=None, 
                                          plugin_info_ext="yapsy-plugin"):
        """ Creates the base VariablePluginManagaer. """
        self.config=cfg_p
        self.msg_handler = commreader
        FilteredPluginManager.__init__( self,
                                        decorated_manager,
                                        categories_filter,
                                        directories_list,
                                        plugin_info_ext)
        
    def loadPlugins(self, callback=None):
        """Re-written to allow for passing variables to the new plug-ins. """
        
        if not hasattr(self._component, '_candidates'):
            raise ValueError("locatePlugins must be called before loadPlugins")

        for candidate_infofile, candidate_filepath, plugin_info in self._component._candidates:
            if callback is not None:
                callback(plugin_info)
                
            candidate_globals = {"__file__":candidate_filepath+".py"}
            if "__init__" in  os.path.basename(candidate_filepath):
                sys.path.append(plugin_info.path)                
            try:
                logging.debug("trying to exec: %s.py" % candidate_filepath)
                exec(open(candidate_filepath+".py","rb").read(), candidate_globals)
            except Exception as e:
                logging.debug("Unable to execute the code in plugin: %s" % candidate_filepath)
                logging.debug("\t The following problem occured: %s %s " % (os.linesep, e))
                if "__init__" in  os.path.basename(candidate_filepath):
                    sys.path.remove(plugin_info.path)
                continue

            if "__init__" in  os.path.basename(candidate_filepath):
                sys.path.remove(plugin_info.path)
                
            for element in candidate_globals.values():
                current_category = None
                for category_name in self._component.categories_interfaces:
                    try:
                        is_correct_subclass = issubclass(element, self._component.categories_interfaces[category_name])
                    except: continue
                    
                    if is_correct_subclass:
                        if element is not self._component.categories_interfaces[category_name]:
                            current_category = category_name
                            break
                if current_category is not None:
                    if not (candidate_infofile in self._component._category_file_mapping[current_category]): 
                        # we found a new plugin: initialise it and search for the next one
                        plugin_info.plugin_object = element(self.config.getPluginVars(plugin_info.name),
                                                            self.msg_handler)
                        plugin_info.category = current_category
                        self._component.category_mapping[current_category].append(plugin_info)
                        self._component._category_file_mapping[current_category].append(candidate_infofile)
                        current_category = None
                    break

        # Remove candidates list since we don't need them any more and
        # don't need to take up the space
        delattr(self._component, '_candidates')  
