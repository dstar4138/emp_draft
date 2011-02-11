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

# LATER: Add code for a registration table, maybe sqlite3?
# needed functionality
#   - add an (id,ips,level) group to table
#   - edit level,ip of id in table
#   - check if an id is in table
#   - check level of id
#   - remove id group
#
DEFAULT_PLUGIN_ACTIONS = []
DEFAULT_INTERFACE_ACTIONS = ["status", "plugin"]



def isPluginRegistered(id):
    """ Checks if a given plugin ID is registered with the daemon process."""
    #LATER: check registration table
    return DEFAULT_PLUGIN_ACTIONS


def isInterfaceRegistered(id):
    """Checks if a given interface ID is registered with the daemon process."""
    #LATER: check registration table
    return DEFAULT_INTERFACE_ACTIONS

