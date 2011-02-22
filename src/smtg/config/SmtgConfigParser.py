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

import os, sys
from configparser import SafeConfigParser
from smtg.config.defaults import default_configs, default_cfg_files, writeto_cfg_file

CATEGORY_MAP = {"Feeds":"plugin_",
                "Signals":"plugin_",
                "Alerts":"alerter_"}

class SmtgConfigParser(SafeConfigParser):
    """At its heart, this config parser is a SafeConfigParser. The
    only added functionality is the default configurations automatically
    added and automatic config file validation. Oh, and there are some
    functions for getting certain values quicker.
    """

    def __init__(self, configfile=None):
        """ Check the config file and include the defaults. """
        self.CONFIG_FILES = default_cfg_files

        if configfile is not None:
            if not os.path.exists(configfile):
                raise IOError("Configuration File does not exist.")
            
            self.CONFIG_FILES.append(configfile)

        ## now set up the parent class using defaults ##
        SafeConfigParser.__init__(self)
        #reset internal configparser variable...
        if sys.version_info[0]==3 and sys.version_info[1]<2:            
            # i know thats bad form, but this is what happens when
            # you dont think ahead 
            self._sections=default_configs
        else:
            #this is in python3.2+ only
            self.read_dict(default_configs) 

    def validateInternals(self):
        """ Check all the values you are overwriting from the config 
        file. 
        """
        self.read(self.CONFIG_FILES)
        
        ### ### VALIDATION ### ### 
        #then check if the update speed is valid, must be >= 1 minute
        if self.getfloat("Daemon","update-speed") < 1.0:
            self.set("Daemon","update-speed", 1.0)
            
        #first check logging capabilities.
        if self.getboolean("Logging","logging-on"):              
            self.__try_setup_path(self.get("Logging","log-file"))


    def __try_setup_path(self,path):
        if os.path.exists(path):
            return os.access(path, os.W_OK)
        else:
            try:
                dirs, _ = os.path.split(path)
                os.makedirs(os.path.abspath(dirs))
            except: return False
            return True
            
        
        
    def getPluginVars(self, plugin_name):
        """A quick function to return the plugin's variables from the 
        configuration files.
        """
        if type(plugin_name) != str: 
            raise TypeError("Plugin Name must be a string")
        
        #adjust plugin name to compensate for cfg file
        plugin_name="plugin_"+plugin_name
        try: return self.items(plugin_name)
        except: return None
        
    
    def getAlerterVars(self, alerter_name):
        """A quick function to return the alerter's variables from the 
        configuration files.
        """
        if type(alerter_name) != str: 
            raise TypeError("Alerter Name must be a string")
        
        #adjust alerter name to compensate for cfg file
        alerter_name="alerter_"+alerter_name
        try: return self.items(alerter_name)
        except: return None
    
    def defaultAttachmentVars(self, name, defaults, category):
        """Called by SmtgPluginManager and SmtgAlertManager to load the default
        configurations into the database for use later.
        """
        section = CATEGORY_MAP[category]+name
        if not self.has_section(section):
            self.add_section(section)

        for option in defaults.keys():
            if not self.has_option(section, option):
                self.set(section, option, defaults[option])
    
    def save(self, plugins, alerters):
        """ Save the configurations to the local user's configuration. """
        if writeto_cfg_file is not None:
            # update the plug-in variables before saving.
            for plugin in plugins:
                try:
                    for key,value in plugin.plugin_object.config:
                        self.set("plugin_"+plugin.name,key,value)
                        
                    if hasattr(plugin.plugin_object, "autostart"): #its a SignalPlugin
                        self.set("plugin_"+plugin.name,
                                 "autostart",str(plugin.plugin_object.autostart))
                    elif hasattr(plugin.plugin_object,"update_importance"):
                        self.set("plugin_"+plugin.name,
                                 "importance",str(plugin.plugin_object.update_importance))
                    #else, it doesn't matter 
                except: pass
            
            # update the alerter variables before saving.
            for alerter in alerters:
                try:
                    for key,value in alerter.plugin_object.config:
                        self.set("alerter_"+alerter.name, str(key), str(value))
                except: pass
            
            # make sure it exists and can be written to.
            if self.__try_setup_path(writeto_cfg_file):
                self.write(open(writeto_cfg_file, mode="w"))
            
    
    
