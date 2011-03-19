EMP Interface API
==================

This is the main source of documentation for how to write your own interfaces to
EMP. If you feel that this document could be improved in anyway, please let me 
know as i'm always wanting help. So if you see any spelling errors, missing 
information, or even something that is just plain wrong, please dont hesitate to
shoot me an email.

--My Assumptions:--
I am assuming you know how to program (I dont care which language, and neither
will EMP), and that you know at least a little networking (Sockets, TCP, etc..).
Oh and knowing how JSON works and at least what it is would be helpful.


What is an Interface?
---------------------

An interface is a program that talks to the EMP Daemon that is running on 
either the computer you are using or on a server somewhere. Interfaces connect
to emp via a TCP socket that it creates. Once connected interfaces can talk to 
EMP via the specialized message protocol that is entirely in JSON.


What is a "General-Case" Interface?
----------------------------------

A "General-Case" interface is one that handles all possible return types that an
Attachment can pass. Attachments (once a command has been called), will return 
its value to the interface that called it. This value is not subjected to any
type checks or string parsing, thats the interfaces job. 

An example of a "General-Case" Interface is the emp.py program that is provided,
its way of handling the command return is to keep the value in JSON and print it
to stdout. Of course if you wrote one, you could do a lot more parsing and do 
something pretty with it.


Does my Interface have to be "General-Case"?
--------------------------------------------

Of course not, you could talor your interface to be perfect for your 
attachments. But If a new attachment comes out that has some awesome features
you are kinda out of luck. Also, what if your Attachments ever change the way 
they work, then you might need to alter how your entire interface works. That
would of course suck.


How should an Interface work?
------------------------------

As long as the interface connects to the Daemon with a UTF-8 encoded TCP socket
and utilizes the message protocol it should be fine. (*Also as a note, make sure
you use your Interface ID that has been given to you when you connect. See the 
steps below.


What do I need to do to connect to EMP:
---------------------------------------

The it does not matter if the daemon is on the local machine or on one 300 miles
away. As long as you connect correctly. Heres how:

1. Connect using UTF-8 encoded TCP socket on right port (Default 8080)
 *There may be a security check here once security has been added*
2. Wait for a response:
    3. If you dont get a response, EMP died or you weren't authenticated.
    4. If you get a response it will be a BaseMsg. The Destination field is
        your new ID for the interface. Set this in your Source field whenever
        you are sending a message to EMP.
5. Send a CommandMsg
6. Wait for a response will be an AlertMsg, ErrorMsg, or BaseMsg.
7. Go back to step 5, or continue to 8.
8. Send a blank string, EMP will recognize this as you closing the connection.
9. Close your socket, and continue about your day.

Check out emp.py for the example, or even jemp.java to see how to do it in a 
different language.


What are messages?
-------------------

Messages are JSON strings that are formatted according to EMP's Message 
protocol. You can read about the message protocol in the document called
MessageProtocol.md located in this directory.


Do I have to use your silly message protocol?
----------------------------------------------

Well no, but if you want EMP to understand you then you will need to use it.


