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

class Command():
    """ Command objects make Plug development easier and more explicitly
    standard. To create a Command, give it its name and the method that
    it calls when it gets fired. eg.
        help = Command( "help", 
                        trigger=helpscreen,
                        help="Displays a help screen for this Plug" )
    """
    def __init__(self, name, trigger=None, help=None):
        self.name = name
        self.trigger = trigger
        self.help = help
        
    def __eq__(self, other):
        """ The command can be compared to a string. It compares its 
        function name.
        """
        if type(other) is str:
            return other == self.name
        elif type(other) is Command:
            return other.name == self.name
        else:
            return False
        
    def run(self, *args):
        """ Runs the function this Command represents."""
        if self.trigger is None: return
        else: self.trigger(*args)
        
    def asMap(self):
        """ Returns this command as a map of name to help string. """
        if self.help is not None:
            return {self.name : self.help}
        else:
            return {self.name : ""}
        
    def __str__(self):
        return str(self.asMap())
    