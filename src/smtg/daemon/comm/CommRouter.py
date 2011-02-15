__copyright__ = """
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



class CommRouter():
    """The CommRouter internally handles inter-thread communication and
    message passing. SMTG uses this to handle incoming Interface and Plug-in
    messages and route them to the right Plug-in, Interface, Alert, or internal
    handler. 
    
    In order to utilize the router, the objects must be registered and an id 
    must be given to it. This id must be used as the source/destination in the
    Message.
    """
    def __init__(self):
        pass
    