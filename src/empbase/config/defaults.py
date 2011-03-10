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
import logging
import sys, os

# the platform you are running on!
CUR_PLATFORM = sys.platform

# OVERRIDE DEBUG MODE?
DEBUG_MODE = True

#
# This is included as the default configuration for the config parser.
# Im fairly sure there is probably a more effective and easier way of
# getting the OS and adjusting default values, but this seemed the 
# quickest (for time effectiviness for loading process) way of getting
# it done. (As opposed to loading from a coupled default config file 
# that is build upon first time run.)
#
default_configs = {

#Daemon section-
#  Will be used to hold varibles pertaining to running the daemon
"Daemon" : 
    { 
    # the location of the pid file, can not be relative.
      "pid-file" : "",
 
    # the location of the directory to save all data to, can't be relative. 
      "base-dir" : "",
    
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
      "allow-all" : "false"
    },

#Logging section-
# It has its own section since theres a lot to possibly be able to log.
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

default_cfg_files = []
default_plugin_dirs = []
default_alerter_dirs = []

# this is the file that the config parser will write to when its closing.
writeto_cfg_file = None

#
# Set up OS specific variables in the default configuration variable, we can
# also set up some other stuff if need be. Namely call setup.py if there is 
# anything missing?
#
if CUR_PLATFORM.find("linux")!=-1:    #linux systems.
    base_dir = os.path.expanduser("~/.emp")
    
    default_configs["Daemon"]["pid-file"]="/var/tmp/emp.pid"
    default_configs["Daemon"]["base-dir"]=base_dir
    
    default_configs["Logging"]["log-file"]=base_dir+"/errors.log"
    writeto_cfg_file = base_dir+"/emp.cfg"
    
    default_cfg_files.append("/etc/emp/emp.cfg")
    default_cfg_files.append(writeto_cfg_file)
    # then a given file will be read in at the end in SmtgConfigParser

    default_plugin_dirs.append("/etc/emp/plugs")
    default_plugin_dirs.append(base_dir+"/plugs")
    default_plugin_dirs.append("plugs") # look in the local src/plugins directory too


    default_alerter_dirs.append("/etc/smtg/alarms")
    default_alerter_dirs.append(base_dir+"/alarms")
    default_alerter_dirs.append("alarms") # look in the local src/alerters directory too

elif CUR_PLATFORM.find("win32")!=-1:  # Windows systems.
    pass
elif CUR_PLATFORM.find("darwin")!=-1: # Mac OSX
    pass
else:  # the poor souls not using one of the above. :(
    logging.warning("Could not determine current operating system.")


#Set up the attachments directories!
attachment_dirs = default_plugin_dirs + default_alerter_dirs
#set the debug mode variable if its internally set!
if DEBUG_MODE: default_configs["Logging"]["debug-mode"]="true"

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

