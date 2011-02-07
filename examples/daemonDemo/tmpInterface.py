#!/usr/bin/env python3.0

#
# This is a temporary interface to demo communication to the 
# daemon from anything like alert systems, or other interfaces. 
#
# By: Alexander Dean
#

from smtg.daemon.daemonipc import DaemonClientSocket

try:
    #1) first connect to daemon, let the daemon know who you are
    daemon = DaemonClientSocket()
    # may throw exception if daemon not running. 
    daemon.connect('i00000002') #interface, the id should follow it. This 
                                # connects you with the daemon via your 
                                # registered id. To register an interface
                                # consult smtgd.py.

    
    #2) wait for reply (there is either a reply, or a connection kill)
    reply = daemon.recv()
    if not reply: 
        print("Daemon could not be contacted.")
        exit()
    
        
    #3) start communicating, the conversation sequence is:
    #    1. send a command
    #    2. receive results
    #    3. repeat as long as you want
    while True:
        daemon.send('info') 
        print(daemon.recv())  
        #break
    # This is the basis of all communication with the server. The conversation 
    # sequence never changes, but the commands can change. Please check the 
    # SNTG-CommAPI for the commands and any specialized plug-in commands. The 
    # API is located either in the DOC directory bundled with the SNTG release,
    # or on the SNTG website.

   
    #4) finally close connection (if you don't want to keep talking)
    daemon.close()

except Exception as e:
    # exceptions can happen if the server isn't running!
    print(e) 
