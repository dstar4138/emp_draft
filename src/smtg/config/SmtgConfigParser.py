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
from configparser import SafeConfigParser
from smtg.config.defaults import default_configs, default_cfg_files


class SmtgConfigParser(SafeConfigParser):
    """At its heart, this config parser is a SafeConfigParser. The
    only added functionality is the default configurations automatically
    added and automatic config file validation. Oh, and there are some
    functions for getting certain values quicker.
    """

    def __init__(self, configfile=None):
        """ Check the config file and include the defaults. """
        self.VALIDATED = False
        self.CONFIG_FILES = default_cfg_files

        if configfile is not None:
            if not os.path.exists(configfile):
                raise IOError("Configuration File does not exist.")
            
            self.CONFIG_FILES.append(configfile)

        ## now set up the parent class using defaults ##
        SafeConfigParser.__init__(self)
        #reset internal configparser variable...
        # i know thats bad form, but this is what happens:
        self._sections=default_configs 


    def validateInternals(self):
        """ Check all the values you are overwriting from the config 
        file. 
        """
        if self.VALIDATED: return

        self.VALIDATED = True
        self.read(self.CONFIG_FILES)
        
            ### ### VALIDATION ### ###
        #first check logging capabilities.
        if self.getboolean("Logging","logging-on"):              
            self.__try_setup_path(self.get("Logging","log-file"))
            
        #then check if the update speed is valid, must be >= 1 minute
        if self.getfloat("Daemon","update-speed") < 1.0:
            self.set("Daemon","update-speed", 1.0)


    def __try_setup_path(self,path):
        #LATER: check if path exists, if it doesn't the create it safely.
        pass

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
    
    def save(self):
        """ Save the configurations to the local user's configuration. """
        pass #TODO: please implement me!
    
    
