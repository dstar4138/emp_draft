#!/usr/bin/env python3.2
"""
Extensible Monitoring Platform (EMP) 
    By: Alexander Dean <dstar@csh.rit.edu> 

For support please visit Alexander's blog or even the 
EMP project page: http://code.dstar4138.com/view?pid=2
"""

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

__simple__ = "emp [options] [command [args ...]]"
__usage__ = "emp [-h | -a | -i | -l | -t T [ -g | -? C ]] [-n | -p | -r] [cmd [args ...]]"
__desc__ = '''
Emp is the interface for the EMP Daemon. This is a full "general case"  
interface for handling most (if not all) commands for every plug-in, alarm, 
and the daemon itself. The interactive mode is a simple Curses interface for 
looking cool while monitoring the hell out of your plug-ins. 
'''
import sys
import argparse
from empbase.daemon.EmpDaemon import EmpDaemon
from empbase.comm.messages import makeCommandMsg,strToMessage
from empbase.daemon.daemonipc import DaemonClientSocket

from interface.printhelper import fancyprint, checkMsg


def help():
    print( "%s\n%s" % (__usage__, __desc__) )
    print("""
Positional arguments:
  command            A command for the target and any arguments for it.

Optional arguments:
  -h, --help         Show this help message and exit.
  -a, --all          Generate the total command list for all attachments.
                      Think of it as a uber-help screen.
  -i, --interactive  Launch interactive mode.
  -l, --list         List targets.
  -t T, --target T   Change the command target by name or id. (Defaults to the
                      pointing at the daemon).
                      
Output arguments: 
  -n, --nowait       Don't wait for a response from the daemon for the 
                      command sent.
  -p, --pretty       Attempt to format the raw JSON that comes out of EMP.
  -r, --nopretty     Some commands will asked to be pretty, this forces a
                      them to be raw JSON. Use if utilizing in a script.
   
Target commands:
  -g, --tcmds        Get target's commands.
  -? C, --ask C      Ask the target how to use the command, will return 
                      either the command's detailed usage, or the simple help 
                      if not provided.
""")


def setupParser():
    """ Sets up the parser for emp, this can be expanded when necessary."""
    parser = argparse.ArgumentParser(description=__desc__,
                                     usage=__usage__,
                                     prog="emp",
                                     add_help=False)
    parser.set_defaults(target=['daemon'])
    
    parser.add_argument("-h","--help", action="store_true")
    
    parser.add_argument("-i", action="store_true")
    parser.add_argument("-l","--list", action="store_true")
    parser.add_argument("-a","--all", action="store_true")
    
    parser.add_argument("-t","--target", nargs=1, metavar="T")
    parser.add_argument("-g","--tcmds", action="store_true")
    parser.add_argument("-?", "--ask", nargs=1, metavar="C")
    
    parser.add_argument("-n", "--nowait", action="store_true")
    parser.add_argument("-p", "--pretty", action="store_true")
    parser.add_argument("-r", "--nopretty", action="store_true")
    
    parser.add_argument("command", nargs='*')
    return parser


#
# MAIN 
#  Handles the incoming command and parses it.
#
def main():
    parser = setupParser()
    args = parser.parse_args()
    #handle the commands given
    if len(sys.argv) == 1:
        print("Usage:",__simple__,"\n\nType 'emp -h' for some help.")
        return
    
    #print(args)
    if args.help: help()
    elif args.i:
        from interface.empcurse import interactiveMode
        interactiveMode()
    else:
        try:
            # we will be communicating with the daemon
            commport = EmpDaemon().getComPort()
            if commport is None: print("Error: Daemon isn't running!");return
            
            daemon = DaemonClientSocket(port=commport)
            daemon.connect()
            msg = strToMessage(daemon.recv())
            if msg is None or msg.getValue() != "proceed": 
                print("Error: Couldn't connect to the daemon.")
                return
            
            myID = msg.getDestination()
                
            #what are we communicating    
            if args.list:
                daemon.send(makeCommandMsg("alarms",myID))
                alerters = checkMsg(daemon.recv())
                daemon.send(makeCommandMsg("plugs",myID))
                plugs = checkMsg(daemon.recv())
            
                #print the list all pretty like:
                print("Attached targets and their temp IDs:")
                print("   Plugs:")
                for k in plugs.keys():
                    print("     %s" % plugs[k][1])
                    print("        Name: %s"%plugs[k][0])
                    print("        ID: %s"%k)
                print("\n   Alarms:")
                for k in alerters.keys():
                    print("     %s" % alerters[k][1])
                    print("        Name: %s"%alerters[k][0])
                    print("        ID: %s"%k)
                print()
                
        
            elif args.all: 
                daemon.send(makeCommandMsg("help",myID, args=["all"]))
                cmds = checkMsg(daemon.recv(), dict)
                for target in cmds.keys():
                    print("%s"%target)
                    if len(cmds[target].keys()) > 0:
                        print("Commands:")
                        fancyprint(cmds[target])
                    else: print("No Commands available!")
                    print()
                    
            else:
                # now we can start parsing targets and figuring out what to do with them
                if args.tcmds:
                    daemon.send(makeCommandMsg("help",myID, args=args.target))
                    cmds = checkMsg(daemon.recv(), dict)
                    print("%s Commands: "%args.target[0])
                    fancyprint(cmds)
                elif args.ask:
                    daemon.send(makeCommandMsg("help",myID, args=args.target))
                    cmds = checkMsg(daemon.recv(), dict)
                    cmdfound = False
                    for cmd in cmds.keys():
                        if args.ask[0] == cmd:
                            print("  %s  -%s"%(cmd,cmds[cmd]))
                            cmdfound = True
                            break
                            
                    if not cmdfound:
                        print("The target does not have that command.")
                else:
                    if len(args.command) < 1:
                        print("Usage: ",__usage__)
                        daemon.send(makeCommandMsg("help", myID, args=args.target))
                        cmds = checkMsg(daemon.recv(), dict)
                        print("\n%s Commands: "%args.target[0])
                        fancyprint(cmds)
                    else:
                        daemon.send(makeCommandMsg(args.command[0], myID, dest=args.target[0], args=args.command[1:]))
                        
                        if not args.nowait:
                            result = checkMsg(daemon.recv())
                            # since this is a general case interface, we don't really know 
                            # how to interpret the result of an argument. But this can
                            # be utilized in a script or a higher level interface. if you 
                            # want to call smtg through your program be sure you can 
                            # handle JSON 
                            if args.pretty: fancyprint(result)
                            # No-pretty is the default, but its an argument just to specify 
                            # if the command line is placed in scripts.
                            else: print(result) 
                        else: print("success")
            
            # now lets close the port to indicate that we are finished.
            daemon.close()
        except:
            if not args.nowait: raise
            else: print("error") # scripts can check for this.
                

if __name__ == "__main__": main()
    
