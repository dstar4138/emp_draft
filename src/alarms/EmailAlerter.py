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
import smtplib
from empbase.attach.attachments import EmpAlarm

class EmailAlerter(EmpAlarm):
    """ This alerter uses an SMTP server to send you an email when you get
    alerted.
    """
    
    def __init__(self, conf):
        """Sets up the alerter."""
        EmpAlarm.__init__(self, conf)
        
    
    def get_commands(self):
        return []
    
    
    def get_alerts(self):
        return []
    
    
    def save(self):
        EmpAlarm.save(self)