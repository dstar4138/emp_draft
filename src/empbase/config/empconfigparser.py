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

import os, sys, logging
from configparser import ConfigParser
from empbase.attach.attachments import EmpAlarm
from empbase.config.defaults import ATTACHMENT_DIRS, DEFAULT_CONFIGS, DEFAULT_CFG_FILES, SAVE_CFG_FILE

CATEGORY_MAP = {"Loops":"plug_",
                "Signals":"plug_",
                "Alarms":"alarm_"}

class EmpConfigParser(ConfigParser):
    """At its heart, this config parser is a SafeConfigParser. The
    only added functionality is the default configurations automatically
    added and automatic config file validation. Oh, and there are some
    functions for getting certain values quicker.
    """

    def __init__(self, configfile=None):
        """ Check the config file and include the defaults. """
        self.CONFIG_FILES = DEFAULT_CFG_FILES

        if configfile is not None:
            if not os.path.exists(configfile):
                raise IOError("Configuration File does not exist.")
            
            self.CONFIG_FILES.append(configfile)

        ## now set up the parent class using defaults ##
        ConfigParser.__init__(self)
        #reset internal configparser variable...
        if sys.version_info[0]==3 and sys.version_info[1]<2:            
            # i know thats bad form, but this is what happens when
            # you dont think ahead 
            self._sections=DEFAULT_CONFIGS
        else:
            #this is in python3.2+ only
            self.read_dict(DEFAULT_CONFIGS) 

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
                if not os.path.exists(dirs):
                    os.makedirs(os.path.abspath(dirs))
            except: 
                return False
            return True
            
        
        
    def getAttachmentVars(self, name):
        """Returns a TinyCfgPrsr of the attachment's variables that were in 
        saved to smtg's config file. TinyCfgPrsr provides some utility functions
        for retrieving the types of variable that were stored there.
        """
        if type(name) is not str: 
            raise TypeError("Plugin Name must be a string")
        
        attach_name="plug_"+name
        try: return TinyCfgPrsr(dict(self.items(attach_name)))
        except:
            attach_name="alarm_"+name
            try: return TinyCfgPrsr(dict(self.items(attach_name)))
            except: return TinyCfgPrsr({})
        

    def getAttachmentDirs(self):
        """ Gets the directories that attachments can be found in."""
        #TODO: ?? allow to be changable via cfg file ??
        return ATTACHMENT_DIRS
    
    def getRegistryFile(self):
        """ The registry file to be read in by the Registry object. """
        return self.get("Daemon","registry-file")
    
    
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
    
    def save(self, attachments):
        #XXX: rewrite to conserve comments in the config file if there are any.
        """ Save the configurations to the local user's configuration. """
        if SAVE_CFG_FILE is not None:
            # update the plug-in variables before saving.
            for attach in attachments:
                try:
                    attach.plugin_object.save() #make the plugin save before pulling the configs
                    
                    if isinstance(attach.plugin_object, EmpAlarm):
                        for key in attach.plugin_object.config.keys():
                            self.set("alarm_"+attach.plugname, str(key), str(attach.plugin_object.config[key]))
                    else:
                        for key in attach.plugin_object.config.keys():
                            self.set("plug_"+attach.plugname,key,str(attach.plugin_object.config[key]))
                        #else, it doesn't matter 
                except Exception as e: 
                    logging.exception(e)
            
            # make sure it exists and can be written to.
            logging.debug("Trying to save cfg to: %s"%SAVE_CFG_FILE)
            if self.__try_setup_path(SAVE_CFG_FILE):
                self.write(open(SAVE_CFG_FILE, mode="w"))
                logging.debug("Saved to cfg file!")
            else:
                logging.error("Couldn't write to cfg file, it cant be created.")

BOOL_CHOICES = {"0":False,"1":True,"no":False,"yes":True,"true":True,
                "false":False,"on":True,"off":False, "":False}


class TinyCfgPrsr():
    """ A Utility class to make handling configuration variables easier for
    attachment construction. They mimic the functionality of a standard 
    config parser, but minus a lot of un-needed functions and variables. It
    also just holds one section as a dictionary.
    """
    def __init__(self,dictionary):
        self._value = dictionary
    
    def keys(self):
        return list(self._value.keys())
    
    def __getitem__(self, i):
        return self.get(i,None)
    
    def get(self, key, default):
        if key in self._value:
            return self._value[key]
        else: return default
    
    def getint(self, key, default):
        if key in self._value:
            return int(self._value[key])
        else: return default

    def getfloat(self, key, default):
        if key in self._value:
            return float(self._value[key])
        else: return default

    def getlist(self, key, default):
        if key in self._value and self._value[key] != '':
            return self._value[key].split(',')
        else: return default
    
    def getboolean(self, key, default):
        if key in self._value:
            res=self._value[key].lower()
            if res in BOOL_CHOICES:
                return BOOL_CHOICES[res]
            else: return False
        else: return default
    
    def set(self, key, value):
        self._value[key] = value
    