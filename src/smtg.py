#!/usr/bin/env python3.0
"""
Social Monitor for the Terminal Geek (SMTG) - 
  A way for the socially inept to stay connected!
 
By: Alexander Dean <dstar@csh.rit.edu> 

For support please visit Alexander's blog or even the 
SMTG project page: http://code.dstar4138.com/view?pid=2
"""

__version__ = "version 0.0.2"
__usage__ = "usage: %prog [options] [config-file]"
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

import sys
from smtg.daemon.SmtgDaemon import SmtgDaemon
from optparse import OptionParser, OptionGroup, SUPPRESS_HELP

###############################################################################
#######################    Other Helper methods    ############################
###############################################################################
#XXX: no one will use this damn program without a nice interface...
def setupParser():
    """
        Sets up the parser by pulling all the plug-in's 
        options into the main parser. Also does some simple
        type checking and sets some constant values.
    """
    tmpP = OptionParser(usage=__usage__, 
                        version=__version__,
                        add_help_option=False)
    tmpP.add_option("-?","--help", action="help", help="show this help screen");
    
    daemonGroup = OptionGroup(tmpP, "Daemon Options", "Options for controlling the SMTG Daemon");
    daemonGroup.add_option("-t", "--start-daemon", action="store_const", const=1, dest="daemonStatus", help="Starts the daemon, if off.", default=-1);
    daemonGroup.add_option("-e", "--restart-daemon", action="store_const", const=2, dest="daemonStatus", help="Restarts the Daemon.");
    daemonGroup.add_option("-s", "--stop-daemon", action="store_const", const=0, dest="daemonStatus", help="Stops the daemon if it is running.");
    daemonGroup.add_option("-c", "--config", action="store_const", help="Stops the daemon if it is running.");
    daemonGroup.add_option("-d", nargs=0, dest="daemonize", help=SUPPRESS_HELP)
    tmpP.add_option_group( daemonGroup );    

    pluginGroup = OptionGroup(tmpP, "Plugin Options", "Options utilizing plugins, use carefully, might affect logs and config files.");
    pluginGroup.add_option("-p","--plugin", dest="plugin", help="describes which of the plugins given the command will be referencing.", metavar="PLUGIN");
    pluginGroup.add_option("-l","--list-plugins", action="store_false", dest="listPlugins", help="list the plug-ins visible by the smtg daemon");
    pluginGroup.add_option("-h","--plugin-help", help="get help on a given PLUGIN", metavar="PLUGIN");
    tmpP.add_option_group( pluginGroup );
    
    return tmpP




###############################################################################
###############################    MAIN    ####################################
###############################################################################
def main():
    try:
        parser = setupParser()
        if len(sys.argv[1:]) == 0:
            parser.print_usage()
            print("Use '-?' for help and a list of options.")
            return
            
        (options, args) = parser.parse_args()    
        if len(args) > 1:
            print("Invalid argument structure. Use '-?' for help.\n")
            return
       

        if hasattr(options, 'daemonStatus'):
            if len(args) == 1:
                daemon = SmtgDaemon(configfile=args[0], dprg="smtg.py")
            else:
                daemon = SmtgDaemon(dprg="smtg.py")

            if options.daemonStatus == 0: #stop
                daemon.stop()
            elif options.daemonStatus == 1: #start
                daemon.start()
            elif options.daemonStatus == 2: #restart
                daemon.restart()
            elif hasattr(options, 'daemonize'):
                daemon._run()

        #
        # TODO run the other options
        #
        #some methods will need to check if the daemon is running before hand
        #
        
    except Exception as e:
        ''' Handle some exceptions!! '''
        print(e)
        sys.exit(1)
    else:
        ''' no issues, return correctly '''
        sys.exit(0)



if __name__ == "__main__":
    main();

