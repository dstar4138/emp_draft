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

__usage__ = "emp [-h | -a | -i | -l | -t T [ -g | -? C ]] [-n] [command [args ...]]"
__desc__ = '''
Emp is the interface for the EMP Daemon. This is a full "general case"  
interface for handling most (if not all) commands for every plug-in, alarm, 
and the daemon itself. The interactive mode is a simple Curses interface for 
looking cool while monitoring the hell out of your plug-ins. 
'''
import sys
import argparse
from empbase.daemon.EmpDaemon import EmpDaemon
from empbase.comm.messages import makeCommandMsg,strToMessage, ERROR_MSG_TYPE
from empbase.daemon.daemonipc import DaemonClientSocket
#import curses


def help():
    print( "%s\n%s" % (__usage__, __desc__) )
    print("""
positional arguments:
  command           A command for the target and any arguments for it.

optional arguments:
  -h, --help        show this help message and exit
  -a, --all         Generate the total command list for all plugins. Think
                    of it as a uber-help screen.
  -i                Launch interactive mode
  -l, --list        List targets
  -t T, --target T  Change the command target by name/id. (Defaults to the
                    pointing at the daemon).
  -g, --tcmds       Get target commands
  -n, --nowait      Don't wait for a response from the daemon for the 
                    command sent.
  -? C, --ask C     Ask the target how to use the command
""")


def setupParser():
    """Sets up the parser for emp, this can be expanded when necessary."""
    parser = argparse.ArgumentParser(description=__desc__,
                                     usage=__usage__,
                                     prog="emp",
                                     add_help=False)
    parser.set_defaults(target=['daemon'])
    
    parser.add_argument("-h","--help", action="store_true", help="show this help message and exit")
    
    parser.add_argument("-i", action="store_true",  help="Launch interactive mode")
    parser.add_argument("-l","--list", action="store_true", help="List targets")
    parser.add_argument("-a","--all", action="store_true", help="Generate the total command list for all plugins ")
    
    parser.add_argument("-t","--target", nargs=1, metavar="T", help="Change the command target by name/id. (Defaults to the pointing at the daemon).")
    parser.add_argument("-g","--tcmds", action="store_true", help="Get target commands")
    parser.add_argument("-?", "--ask", nargs=1, metavar="C",  help="Ask the target how to use the command")
    parser.add_argument("-n", "--nowait", action="store_true")
    
    parser.add_argument("command", nargs='*', help="A command for the target and any arguments for it.")
    return parser

def fancyprint(dct, buffer=2, st="-", fnt=" ", mx=80):
    rside = max(map(len, dct.keys()))
    rside += buffer
    
    def spacegen(i):
        s=""
        for _ in range(0,i): s+=" "
        return s
    
    def carefulprint(s):
        push=rside+len(st)+len(fnt)+1
        count=push
        sent = s.split(" ")
        for i in range(0,len(sent)):
            print(sent[i],end=' ');count+=len(sent[i])+1
            if len(sent)>i+1 and count+len(sent[i+1]) >= mx:
                print("\n"+spacegen(push), end='')
                count=push
        print()
    
    for k in dct:
        print(fnt+k,end=spacegen(rside-len(k)))
        carefulprint(st+" "+dct[k])
    


def interactiveMode():
    #TODO: interactive mode in glorious curses! 
    # purhaps consider urwid to make things easier: http://excess.org/urwid/
    print("Apologies, interactive mode is not yet finished. Please try again later.")

def checkMsg(msg, typeCheck=None):
    """Checks if the return is an error, if it is, it will handle it. If not 
    then it will check it against the provided type. If is not the valid type 
    it will print it right then and there. If it IS the valid type it will 
    return it.
    """
    msg = strToMessage(msg)
    if msg is None: 
        print("ERROR: Is the Daemon running?")
        sys.exit(1)
    
    if msg.getType() == ERROR_MSG_TYPE:
        print("ERROR:",msg.getValue())
        sys.exit(1)
    elif typeCheck is None or typeCheck is type(msg.getValue()):
        return msg.getValue()
    else:
        print(msg.getValue())


#
# MAIN 
#  Handles the incoming command and parses it.
#
def main():
    parser = setupParser()
    args = parser.parse_args()
    #handle the commands given
    if len(sys.argv) == 1:
        print("Usage:",__usage__,"\n\nType 'emp -h' for some help.")
        return
    
    #print(args)
    if args.help: help()
    elif args.i:  interactiveMode()
    else:
        try:
            # we will be communicating with the daemon
            commport = EmpDaemon().getComPort()
            if commport is None: print("Error: Daemon isn't running!");return
            
            daemon = DaemonClientSocket(port=commport)
            daemon.connect()
            msg = strToMessage(daemon.recv())
            if msg.getValue() != "proceed": print("Error: Couldn't connect to the daemon.");return
            
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
                            print(result) 
                        else:
                            print("Command sent.")
            
            # now lets close the port to indicate that we are finished.
            daemon.close()
        except:
            raise
            #print("Error: Couldn't connect to the daemon. Is it running?")
                

if __name__ == "__main__": main()
    
