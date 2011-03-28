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

######
#These are the default configurations that are loaded based on the type
#of operating system, and system setup.
######
import sys, os

# the platform you are running on!
CUR_PLATFORM = sys.platform

# OVERRIDE DEBUG MODE?
DEBUG_MODE = True ##XXX: REMOVE ME!!

#
# This is included as the default configuration for the config parser.
# Im fairly sure there is probably a more effective and easier way of
# getting the OS and adjusting default values, but this seemed the 
# quickest (for time effectiviness for loading process) way of getting
# it done. (As opposed to loading from a coupled default config file 
# that is build upon first time run.)
#
DEFAULT_CONFIGS = {

#Daemon section-
#  Will be used to hold variables pertaining to running the daemon
"Daemon" : 
    { 
    # the location of the pid file, can not be relative.
      "pid-file" : "",
 
    # registry file.
      "registry-file" : "",
 
    # the location of the directory to save all data to, can't be relative. 
      "base-dir" : "",
    
    # the location all attachments should save their data
      "save-dir" : "",
    
    # the port number for the interface communications.
      "port" : "8080",
 
    # update speed for feed defaults to 1 minute. This is the fastest this is 
    # allowed to go, but it can be adjusted to longer than 1 minute.
      "update-speed" : "1.0",
 
    # only allow local interface connections.
      "local-only" : "true",
      
    # IPs that you don't mind connecting to the daemon, ignored unless 
    # local-only is false and allow-all is true
      "whitelisted-ips" : "",

    # Allow all incoming connections to connect to the daemon.      
      "allow-all" : "false",
      
    # Allow emp to boot up at startup
      "boot-launch" : "true"
    },

#Logging section-
# It has its own section since there's a lot to possibly be able to log.
"Logging" :
    {
    # Logging can be turned on and off by the master switch (default to True) 
     "logging-on" : "true",

    # Plugins and the daemon can put more info in logs like a stack traces
     "debug-mode" : "false",

    # What to log is another matter
     "log-warnings" : "true",

    # Logging file need to be set as well
     "log-file" : ""

    }
}

###### THE FOLLOWING ARE GENERATED BASED ON OS ######
BASE_DIR = None # base configuration directory where logs, etc are saved.
SAVE_DIR = None # the sub directory that all attachment data is saved

# the locations of all config files to read in. It must be in order
#   - OS defaults
#   - User defaults 
DEFAULT_CFG_FILES    = []

# Locations of attachments, then joined in variable ATTACHMENT_DIRS below
default_plugin_dirs  = []
default_alerter_dirs = []

# this is the file that the config parser will write to when its closing.
SAVE_CFG_FILE = None

#
# Set up OS specific variables in the default configuration variable, we can
# also set up some other stuff if need be. Namely call setup.py if there is 
# anything missing? These defaults will then be overrode when we read in 
#
if CUR_PLATFORM.find("linux")!=-1:    #linux systems.
    BASE_DIR = os.path.expanduser("~/.emp")
    SAVE_DIR = BASE_DIR + "/save"
    SAVE_CFG_FILE = BASE_DIR+"/emp.cfg"
    
    DEFAULT_CONFIGS["Daemon"]["pid-file"]="/var/tmp/emp.pid"
    DEFAULT_CONFIGS["Daemon"]["registry-file"]=SAVE_DIR+"/registry.xml"
    
    DEFAULT_CONFIGS["Logging"]["log-file"]=BASE_DIR+"/errors.log"
    
    DEFAULT_CFG_FILES.append("/etc/emp/emp.cfg")
    DEFAULT_CFG_FILES.append(SAVE_CFG_FILE)
    # then a given file will be read in at the end in SmtgConfigParser

    default_plugin_dirs.append("/etc/emp/plugs")
    default_plugin_dirs.append(BASE_DIR+"/plugs")

    default_alerter_dirs.append("/etc/emp/alarms")
    default_alerter_dirs.append(BASE_DIR+"/alarms")
    

elif CUR_PLATFORM.find("win32")!=-1:  # Windows systems.
    #TODO: distinguish between NT and later, write!
    BASE_DIR = "~user/.emp"
    SAVE_DIR = BASE_DIR + "/save"
    SAVE_CFG_FILE = BASE_DIR+"/emp.cfg"
    
    DEFAULT_CONFIGS["Daemon"]["pid-file"]=BASE_DIR+"/running.pid"
    DEFAULT_CONFIGS["Daemon"]["registry-file"]=SAVE_DIR+"/registry.xml"
    
    DEFAULT_CONFIGS["Logging"]["log-file"]=BASE_DIR+"/errors.log"
    
    DEFAULT_CFG_FILES.append("emp.cfg") #FIXME: right location?
    DEFAULT_CFG_FILES.append(SAVE_CFG_FILE)

    default_plugin_dirs.append(BASE_DIR+"/plugs")
    default_alerter_dirs.append(BASE_DIR+"/alarms")
    
elif CUR_PLATFORM.find("darwin")!=-1: # Mac OSX, older?
    pass #TODO: write this!!

else:  # the poor souls not using one of the above. :(
    import logging
    logging.warning("Could not determine current operating system.")


################# AFTER THOUGHT VARIABLE CHANGES!! #######################
# Open base and save dirs for user editing.
DEFAULT_CONFIGS["Daemon"]["base-dir"]=BASE_DIR
DEFAULT_CONFIGS["Daemon"]["save-dir"]=SAVE_DIR

# Look at local directories for attachments
default_plugin_dirs.append("plugs") # look in the local src/plugs directory
default_alerter_dirs.append("alarms") # look in the local src/alarms directory too

#Set up the attachments directories!
ATTACHMENT_DIRS = default_plugin_dirs + default_alerter_dirs
#set the debug mode variable if its internally set!
if DEBUG_MODE: DEFAULT_CONFIGS["Logging"]["debug-mode"]="true" ##XXX: REMOVE ME




############## ALT MAIN TO TEST ######################
#if __name__ == "__main__":
#    print("Your os is: ", CUR_PLATFORM)
#    print("So here are your default variables:")
#    for i in default_configs:
#        print("[",i,"]")
#        for n in default_configs[i]:
#            print("\t-",n,"=",default_configs[i][n])
#        print()
######################################################

