EMP: Extendable Monitoring Platform
==========================================

WARNING:
---------
THIS VERSION IS NO LONGER IN DEVELOPMENT AND IS HERE FOR POSTERITY OF FUTURE VERSIONS. 
Please go to the newer EMP project.


Short Description:
------------------

EMP is the foundation and means of extension for monitoring whatever your
heart desires.



Longer Description:
-----------------
SNTG was the original name, it stood for "Social Networking for the Terminal 
Geek". It was going to be a framework/API for making Facebook/Twitter 
accessible to the command line. But that was far too simple, so it evolved into 
'SMTG: Social Monitor for the Terminal Geek'. Its new goal was to be a constant 
monitoring daemon for a Geek's social network (eg. still Facebook, Twitter and 
the like). But again, exceedingly simple and not entirely worth the time I was 
spending on it. Besides, it has already been done several times over in pretty 
much every language.

So then it grew. EMP is now a platform for developing your own private security 
center, networking hub, news feed, and more. It allows you to monitor anything 
you want, and then give you a notification whenever and however you want. How 
does it do this? Attachments.

Attachments can be one of two things: Plugs (things you monitor), or Alarms 
(things that alert you). Of course you can make your own, but for a list of 
bundled attachments see the plugs or the alarms directories in the source code 
base. But if you wanted to learn more about *making* Plugs or Alarms, please 
look at: empbase.attach.attachments.py.

When EMP starts up, it looks in the directories you specified and loads all the 
Alarms and Plugs right then and there, oh and they can be written in any 
language (as long as it has a Python adapter). EMP then waits for one of the 
Plugs to trigger and then sends it to the right Alarm (based on your settings 
and the Alarms' subscriptions). This is all great, however EMP is just a 
multi-threaded daemon sitting in the background making your wishes come true... 
how do you talk to it?

To interface with EMP is simple, it uses UTF-8 encoded TCP sockets and JSON to 
transfer information. But no need to worry about that for now, EMP comes with 
two easy to use interfaces:

* empd - This is a simple interface meant for starting up the daemon.
* emp  - This is the bigger "general-case" interface that you can use to query the daemon.

If you would like to write a more "feature-full" interface check out JSON and 
take a quick look at how EMP does sockets, but it should be straight forward 
and fairly simple.

Well suffice it to say theres a lot you can do. But go on and give it a test 
and see if you like it. And when you are done, check out the TODO file and see
if theres anything you would either like to add or do yourself.


Contributing
------------
Please do! It would be nice to have some help on this! Just shoot me an email.
Right now EMP is not fully working, so if you would like to be put on the list
of people I email when its ready, let me know as well.

