#!/usr/bin/env python3.0 

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

__usage__ = "usage: %prog {option} [configfile]"
__description__ = """ 
The smtgd program is a small example interface for interacting with 
just the daemon. Any actual useful functionality is in smtg instead.
Please use smtgd only for your startup scripts to get the daemon up 
and running, and then shutting it down.  
"""

import sys,logging
from optparse import OptionParser, SUPPRESS_HELP

from smtg.daemon.daemonipc import DaemonClientSocket
from smtg.daemon.SmtgDaemon import SmtgDaemon, __version__
from smtg.daemon.comm.messages import makeCommandMsg, strToMessage
   
def main():
    parser = OptionParser( usage=__usage__, 
                           version="Version: smtgd "+__version__,
                           description=__description__ )
    parser.add_option("--start",action="store_const", const=0, dest="state", 
                      help="start the SMTG daemon")
    parser.add_option("--stop", action="store_const", const=1, dest="state",  
                      help="stop a running SMTG daemon, may take some time to \
                       close all plug-ins")
    parser.add_option("--restart", action="store_const", const=2, dest="state", 
                      help="restart a running SMTG daemon")
    parser.add_option("--status", action="store_const", const=1, dest="status",
                      help="show the status of the currently running SMTG \
                      daemon")
    
    ### the special daemonizer token. see Daemon class for more info ###
    parser.add_option("-d", nargs=0, dest="daemonize", help=SUPPRESS_HELP)
    
    # if there are no command line args, then print usage
    if len(sys.argv[1:]) == 0:
        parser.print_usage()
        print("Use '-h' for more help and a list of options.")
        return
    
    ## parse the command line arguments ##
    (options, args) = parser.parse_args()
    if len(args) > 1:
        print("Invalid argument structure. Use '-h' for help.\n")
        return
    

    try: ## find out what the user wants to do. ##
        
        # user wants to run some functions on the daemon.
        # First we have to construct it to talk to it,
        # which of course takes some time.
        if options.state != None: 
            #we want to mess with the daemon, so construct it
            if len(args) == 1: daemon = SmtgDaemon(configfile=args[0])
            else: daemon = SmtgDaemon()

            # then call functions on it.
            if options.state == 0:
                daemon.start()
            elif options.state == 1:
                daemon.stop()
            elif options.state == 2:
                daemon.restart()
        

        # all the user wants to do is ask how the daemon is doing
        # so open up a port and ask it for some information.
        elif options.status != None:
            try:
                daemon = SmtgDaemon()
                port = daemon.getComPort()
                if port is not None:
                    socket = DaemonClientSocket(portNum=port)
                    socket.connect()
                    msg = strToMessage(socket.recv())
                    logging.debug("smtgd got back: %s"%msg)
                    if msg.getValue() == "proceed":# it connected
                        myId= msg.getDestination()
                        socket.send(makeCommandMsg("status", myId))
                        print(strToMessage(socket.recv()).getValue(),"\n")
                        socket.close()
                    else: print("ERROR: Daemon rejected connection attempt.")
                else: print("ERROR: Daemon is not running.")
            except Exception as e:
                print("ERROR: couldn't communicate with daemon:", e)
                
        # The process has been called via a background thread so 
        # it is ok to just run the daemon, we are one!!
        # see smtg.daemon.daemon.Daemon for more information.
        elif options.daemonize != None:
            #we want to mess with the daemon, so construct it
            if len(args) == 1: daemon = SmtgDaemon(configfile=args[0])
            else: daemon = SmtgDaemon()
            daemon._run()            

    except Exception as e:
        print("ERROR:",e)
 

### Run main() if the file is called correctly ###
if __name__ == "__main__":
    main()

