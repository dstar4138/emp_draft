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

from smtg.alert.smtgalert import Alerter
from smtg.VariablePluginManager import VariablePluginManager

# this is the default alert descriptor extention. See yapsy.PluginInfo
ALERT_EXT = "smtg-alert"

# this is the default alert categories
ALERT_CATEGORIES = {"Default": Alerter}

class SmtgAlertManager(VariablePluginManager):
    """ Handles alerters as similarly to how plug-ins work. """
    
    def __init__(self):
        pass