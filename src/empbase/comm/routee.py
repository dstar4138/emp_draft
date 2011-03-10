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


class Routee():
    """ Base object for every internal possibility for communication 
    within EMP."""
    ID = ''
    
    def handle_msg(self, msg):
        """Called by the router, this is what handles the message directed at 
        this object. WARNING: This method should be thread safe, since its 
        pushed to a new one upon getting called.
        """
        raise NotImplementedError("_handle_msg() not implemented")