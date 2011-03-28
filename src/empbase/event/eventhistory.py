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

#TODO: write event history module!
class EventHistory():
    """ Holds the history of all events ever triggered. It allows for
    querying the history logs and saving to them. 
    """
    def __init__(self, config): pass
    def save(self): pass
    def load(self): pass
    def __bufferBack(self): pass
    def __clearBuffer(self): pass
    def triggeredLast(self, eid): pass
    def triggered(self, eid): pass
    
    