SMTG: Social Monitor for the Terminal Geek
==========================================

Short Description:
------------------

SMTG is the foundation and means of extension for monitoring whatever your
heart desires.



Longer Description:
-------------------

SMTG has three parts: the daemon, the plug-ins, and the interfaces. The 
daemon sits and runs the feed loop along with facilitating communication 
between the interfaces and the plug-ins. Interfaces are what you look at when
you are running the program, a bunch of interfaces can be connected to the 
daemon at once.
 
For example, you could be running the daemon on a server and have a 
web-portal interface, and then code yourself up a pretty little GUI to run on
your desktop and another on your new smart-phone. These interfaces all get 
alerts, updates, and messages from the daemon simultaneously (more or less).

The plug-ins are what do all the hard work. There are two types of plug-ins 
FeedPlugins and AlertPlugins. Feed plug-ins are the most common and easiest to 
make and use. They just run through the SMTG feed loop and can run commands 
sent to them via the daemon from the interfaces. Most if not all of the below 
examples of plug-ins will use this type. 

However, the real power and difference of SMTG to feed readers, are the 
AlertPlugins. These are instantaneous triggers that can do whatever you need 
them to do. For example, say you make a simple bluetooth arduino trigger on 
your dorm door that sends a message back to your computer when someone enters 
your room. You can have an SMTG AlertPlugin be triggered and send a message to 
all of your interfaces letting them know of the event. Instant security system!  

Here are a couple more examples of plug-ins that are or will be made in the 
(hopefully near) future:

* RSS Rake: This is your simple plug-in to facilitate scraping your favorite news/blog feeds.
* Log Watch: Watches local files, like a log file, and keeps track of changes. Useful for system administration or debugging programs that are running.
* Email: Watch email accounts for new messages!
* Facebook: Keep track of your friends and family.
* Twitter: Yep, every single public API out there can be turned into a plug-in. All you have to do is follow the SMTG-API for plug-ins.
* Jabber/chat: You can then use SMTG as a chat client!
* Much much more... use your imagination!
	
	

Contributing
------------
Please do! It would be nice to have some help on this! Just shoot me an email.
