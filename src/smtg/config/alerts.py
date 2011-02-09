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


# Alerts are of one of the following types only:
ALERT_TYPE = ["email","sound","exec"]



class Alert(object):
    """The base type of alert that can be passed or created in SMTG """
    
    def __init__(self,type):
        """Create the alert of a given type, see ALERT_TYPE 
        for more information. 
        """
        self.type = type
        
        
#TODO: fix alerts. This needs to be more thought out.