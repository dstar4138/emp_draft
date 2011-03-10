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

#
#  Here are the building blocks for a standard daemon process. Provided
# are the basic Daemon interface and the DaemonError class which will get 
# raised if there are issues creating/killing/running the daemon process.
#
#  To create your own daemon just inherit from the daemon and override 
# the internal _run() function. To learn more on how to start the daemon
# Please read the Daemon documentation located with the class description.
#
__version__ = "0.5"


import os
import sys
import subprocess


class DaemonError(Exception):
    """A Daemon Error is an issue caused from within the daemon and can
    be used to represent anything from daemon-recreation, poor config files,
    or even issues in file creation. 
        
    Attributes:
        msg  --  the message for the daemon error
    """
    def __init__(self, msg):
        self.message = msg
    def __str__(self):
        return repr(self.message)
    
    
class Daemon():
    """A Daemon is a background process. This implementation is more fragile 
    but works on all operating systems that support the subprocess package.
    Which is basically any OS. The daemonizingCommand is the command line
    command for running the current process. An example is:
                    python daemon.py -d configfile.cfg
    Where the '-d' command indicates to your newly running process that its
    a daemon. Forking does not work on all systems, but running an alternate
    process is still valid. See smtgd for more information.
    
    Attributes:
        pidfile --  the name and path of a temporary file for the daemon 
                    process, it should not exist beforehand
        pchannel -- port for inter-process communication
        dprog -- the program that has to be run as a daemon
        dargs -- the arguments for your daemonized process
        daemonizerArg -- the argument to indicate to the currently running 
                         program that it is now a daemon
        daemonizingCommand -- overrides the previous two attributes to run 
                              a different command
    """
    def __init__(self, pidfile, pchannel=8080, dprog=sys.argv[0], dargs="", 
                 daemonizerArg="-d", 
                 daemonizingCommand=None):
        self.PID_FILE = pidfile # the pid-file name and path
        self.PCHANNEL = pchannel

        if dargs is not None: self.args = dargs
        else: self.args = ""

        if not daemonizingCommand:
            self.daemonizingCommand = "./"+dprog+" "+daemonizerArg+" "+self.args+" &"
        else:
            self.daemonizingCommand = daemonizingCommand
    
    def isRunning(self):
        """Checks to see if the process id file is still existent. If 
        it has been removed, or has yet to be created, then the daemon
        is not currently running.
        """
        return os.path.exists(self.PID_FILE)
        
    def start(self):
        """Starts the daemon by running sntgd with a special set of
        commands. To start the process, the PID file must be created
        so that the _run method will loop correctly.
        """
        if not self.isRunning():
            pid = subprocess.Popen(self.daemonizingCommand, shell=True).pid
            open(self.PID_FILE, "w+").write(str(self.PCHANNEL)+"\n"+str(pid))
        else:
            raise DaemonError("Daemon already running!")
   
    def stop(self):
        """To stop the daemon, the PID only needs to get removed. The 
        running process should see the removal and then terminate.
        """
        if self.isRunning():
            os.remove(self.PID_FILE) #the daemon should see this and kill itself.
        else:
            raise DaemonError("Daemon isn't running!")
    
    def restart(self):
        """Helper function to restart the running daemon. Speeds things
        up a small amount by reducing function calls. But you may want to
        reimplement this method for your own implementation.
        """
        if self.isRunning():
            os.remove(self.PID_FILE)
            
        pid = subprocess.Popen(self.daemonizingCommand, shell=True).pid
        open(self.PID_FILE, "w+").write(str(self.PCHANNEL)+"\n"+str(pid))
    
    def getComPort(self):
        """Returns the port to send interface commands to the daemon. See
        daemonipc for more information about inter-process communication.
        """
        if self.isRunning():
            #first line is port num, so jus read first line
            return int(open(self.PID_FILE, "r").readline())
        else:
            return None
 
    def _run(self):
        """ Write this yourself """
        raise NotImplementedError("Run functionality is default. Please override.")
      
        # an example _run() implementation could consist of the following:
        #
        # def _run(self):
        #   while(self.isRunning()):
        #       print("doing stuff here!!")
        #       
        #       try: time.sleep(time_break) #sleep for some time
        #       except: pass
        #   print("daemon is dead")
        #
