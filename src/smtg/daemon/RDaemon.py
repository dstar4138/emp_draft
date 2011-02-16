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
import sys
from smtg.daemon.comm.CommRouter import Routee
from smtg.daemon.daemon import Daemon

class RDaemon(Daemon, Routee):
    """ Created to just provide portability of the current Daemon 
    implementation. I didn't want people to have to remove or change the
    daemon code to create their own projects without internal CommRouters.
    """
    def __init__(self, pidfile, name, commrouter, 
                 pchannel=8080, dprog=sys.argv[0], 
                 dargs="", daemonizerArg="-d", daemonizingCommand=None):
        """ Create a RDaemon, which is a daemon, that is also a Routee. """
        Daemon.__init__(self, pidfile, pchannel, dprog, dargs, daemonizerArg, daemonizingCommand)
        Routee.__init__(self, name, commrouter) 