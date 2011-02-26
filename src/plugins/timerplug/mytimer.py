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

import time
from threading import _Timer

class MyTimer(_Timer):
    """Simplistic extension to the Timer class to provide some strings
    for sending via messages.
    """
    def __init__(self, interval, function):
        self._created = time.time()
        _Timer.__init__(self, interval, function, args=[self])

    def getTimeCreated(self):
        """ Returns the time it was created as a pretty string. """
        return time.ctime(self._created)
    
    def getTimeFor(self):
        """ Returns the timer's time it was set for as a float. """
        return self.interval
                   
    def getTimeToEnd(self):
        """ Returns the time the timer was set for as a pretty string. """
        return time.ctime(self._created+self.interval)
    
    def isFinished(self):
        """ Checks if the finished flag has been set, this indicates that
        the Timer has ended and run the function.
        """
        return self.finished.is_set()