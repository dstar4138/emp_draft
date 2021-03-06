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

from empbase.attach.attachments import LoopPlug

#i want it to act similarly to twurl but only through smtg, this means 
#that when it updates it can pull information that you want it to, and 
#thus twurl becomes a monitor.


#commands
TWITTER = {}


class TwitPlug(LoopPlug):
    """This will fully utilize the Twitter.com API and allow you to
    send any command that it allows. It will also readily check your 
    private-message mailbox and you time-line.
    """
    def __init__(self, conf):
        LoopPlug.__init__(self, conf)
        
        
    def handle_msg(self, msg):
        pass
        
    def get_commands(self):
        return TWITTER

    def save(self):
        pass