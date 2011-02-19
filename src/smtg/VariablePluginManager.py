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
from yapsy.PluginInfo import PluginInfo
from yapsy.PluginManager import PluginManager
from yapsy.FilteredPluginManager import FilteredPluginManager


class SmtgPluginInfo(PluginInfo):
    def __init__(self, plugin_name, plugin_path):
        self.defaults = {}
        PluginInfo.__init__(self, plugin_name, plugin_path)
        
        
    def setDefaults(self, defaults):
        """ Plug-ins and Alerters in SMTG have default variables that come
        with the distribution, these need to get read out and given to the
        SmtgConfigParser, so everyone can get at them and change them if 
        need be.
        """
        if isinstance(defaults, dict):
            self.defaults.update(defaults)
        
    def __str__(self):
        """Added to improve logging.""" 
        return "<PLUGIN: "+str(self.name)+" - "+str(self.defaults)+">"


class VariablePluginManager(FilteredPluginManager):
    """Makes creating a filtered default plugin manager easier"""
    
    def __init__(self, cfg_p, categories_filter={"Default":IPlugin}, 
                                directories_list=None, 
                                plugin_info_ext="yapsy-plugin"):
        """ Creates the base VariablePluginManagaer. """
        decorated_object = DefaultPluginManager(cfg_p,
                                                categories_filter,
                                                directories_list,
                                                plugin_info_ext)
        
        FilteredPluginManager.__init__(self, decorated_manager=decorated_object)
        
        


class DefaultPluginManager(PluginManager):
    """Extension to the standard PluginManager to allow for default variables for
    each plug-in. These variables are read in and can be passed into the plug-in
    by using a dict object. See smtg.plugin.smtgplugin
    """
    def __init__(self, cfg_p, 
                 categories_filter={"Default":IPlugin}, 
                 directories_list=None, 
                 plugin_info_ext="yapsy-plugin"):
        PluginManager.__init__(self, categories_filter, directories_list, plugin_info_ext)
        self.setPluginInfoClass(SmtgPluginInfo)
        self.config = cfg_p
    
        
    def loadPlugins(self, callback=None):
        """Re-written to allow for passing variables to the new plug-ins. """
        
        if not hasattr(self, '_candidates'):
            raise ValueError("locatePlugins must be called before loadPlugins")

        for candidate_infofile, candidate_filepath, plugin_info in self._candidates:
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
                for category_name in self.categories_interfaces:
                    try:
                        is_correct_subclass = issubclass(element, self.categories_interfaces[category_name])
                    except: continue
                    
                    if is_correct_subclass:
                        if element is not self.categories_interfaces[category_name]:
                            current_category = category_name
                            break
                if current_category is not None:
                    if not (candidate_infofile in self._category_file_mapping[current_category]): 
                        # we found a new plugin: initialise it and search for the next one
                        self.config.defaultAttachmentVars(plugin_info.name, plugin_info.defaults, current_category)
                        plugin_info.plugin_object = element(self.config.getPluginVars(plugin_info.name))
                        plugin_info.category = current_category
                        self.category_mapping[current_category].append(plugin_info)
                        self._category_file_mapping[current_category].append(candidate_infofile)
                        current_category = None
                    break

        # Remove candidates list since we don't need them any more and
        # don't need to take up the space
        delattr(self, '_candidates')      
        
        
    def gatherBasicPluginInfo(self, directory, filename):
        plugin_info,config_parser = self._gatherCorePluginInfo(directory, filename)
        if plugin_info is None:
            return None
        # collect additional (but usually quite useful) information
        if config_parser.has_section("Documentation"):
            if config_parser.has_option("Documentation","Author"):
                plugin_info.author    = config_parser.get("Documentation", "Author")
            if config_parser.has_option("Documentation","Version"):
                plugin_info.setVersion(config_parser.get("Documentation", "Version"))
            if config_parser.has_option("Documentation","Website"): 
                plugin_info.website    = config_parser.get("Documentation", "Website")
            if config_parser.has_option("Documentation","Copyright"):
                plugin_info.copyright    = config_parser.get("Documentation", "Copyright")
            if config_parser.has_option("Documentation","Description"):
                plugin_info.description = config_parser.get("Documentation", "Description")
        
        if config_parser.has_section("Defaults"):
            for option in config_parser.options("Defaults"):
                plugin_info.defaults[option] = config_parser.get("Defaults", option)
        return plugin_info
    
