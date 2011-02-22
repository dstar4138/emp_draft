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

from smtg.plugin.smtgplugin import SignalPlugin



class TimerPlug(SignalPlugin):
    """The Timer plug-in will be the most simplistic SignalPlugin. It will
    create a timer in accordance with the time you need, and then send an 
    alert once the timer is finished. You can ask for a port number from 
    this plug-in if you want the alert to bypass the daemon all together and
    ping some other program.
    """
    pass