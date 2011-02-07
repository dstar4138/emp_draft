#!/usr/bin/env python3.0

#
# This is an example daemon server that you can run to test the tmpInterface.py
# code. Take a look at the conversation and how it's structured, its important!
#
# By: Alexander Dean
#


import time
from threading import Thread
from smtg.daemon.daemonipc import DaemonServerSocket

""" Time the server starts """
start_time = time.time()

def registered(id):
    """The actually daemon checks to see if the connecting interface id is
    valid, and if it is what kind of commands its been authorized for.
    """
    return True

def killall(connections):
    """Kills all the open interface connections. A violent little method."""
    for connection in connections:
        try: connection.close()
        except: pass

def runner(socket,id):
    """The thread that gets run to handle the interface connection. 
    Responds to commands, and handles closing the connection after 
    disconnecting.
    """
    socket.send('proceed')
    
    while True:
        data = socket.recv()
        print("id(",id,")=",data)
        if not data: break
        
        elif data == "info":
            run_time = time.ctime(start_time)
            statusMessage = "SERVER STATUS: Running...\nInterface id:"+str(id)+"\nBeen running since: "+str(run_time)+"\n"
            socket.send(statusMessage)
            
        elif data == "plug": #talk to plugin? aka. other commands    
            pass
        
        else: #not valid command.
            socket.send("invalid command")
            
    socket.close()        
    print("closed connection") #means the thread is also quitting


def printConnections(interfaces):
    #only print the open ones!!!
    print("connections{",end="")
    for conn in interfaces:
        print(conn,",")
    print("}")


if __name__ == "__main__":
    # Create socket and bind to address
    TCPSock = DaemonServerSocket()
    
    #open interface connections
    interfaces = []

    while True: # listen forever for local connections
        client_socket = TCPSock.accept()
        
        #When connects ask for id
        identifier = client_socket.recv()
        if registered(identifier):
            #the id will have a type key
            key = str(identifier)[0]
            id = str(identifier)[1:]
            print("key: ",key,"\nid: ",id)
            if key == 'k': #kill-switch
                print("received kill-switch, shutting down... ")
                killall(interfaces)
                break
            
            elif key == 'i':#interfaces
                print("received interface connection - id:", id)
                interfaces.append(client_socket)
                Thread(target=runner, args=(client_socket, id)).start()
                printConnections(interfaces)        
            else:
                #close the connection since id is not valid
                # shouldn't ever happen since the id was registered...
                TCPSock.close()
        else:
            #close the connection since id is not registered
            TCPSock.close()
            
            
            
