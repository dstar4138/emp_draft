EMP Message Protocol:
======================

Below is the message protocol EMP uses with its Interfaces. Every modern 
programming language has some form of a JSON library which is why we chose it 
as our method for communication for EMP's Interfaces.

One of the promises that EMP makes is that once EMP goes version 1.0, the 
message structure will never ever change. Currently its in a bit of a flux,
but its still pretty solid. Most of the values wont change too much and if they
do, then they will still support the old way.

The result of this promise is that no matter how EMP grows, and changes, or 
what attachments a person might have or not have, you will still know how to
communicate with EMP. However, the type of commands will completely differ 
based on what attachments and version of EMP you'll be working with.


Base Message Structure
------------------------

Base messages are the bare minimum message that can be sent. These are 
discuraged, since they are more difficult to parse genericly for Interfaces. 
But here is the their structure:

                { "message" : "base",
                  "source"  : "obj-id",
                  "dest"    : "obj-id"/null,
                  "value"   : value }
Explanation:

* message: this tells you that it is a base type message to parse.
* source: the source of the message.
* dest: the destination to send the message to (null if you want the message to
        go to the daemon.
* value: the value of the message. This can be anything from an array of
         values, to an float value, to a serialized object inside it.



Alert Message Structure
------------------------

Alerts are treated differently than all the other types of messages since 
they don't NEED to have a destination. If a destination is missing, then the 
alert is sent out to all Alarms and Interfaces. If the destination is present, 
then it MUST be a valid Alerter id.

                    { "message" : "alrt",
                      "source"  : "obj-id",
                      "dest"    : "obj-id"/null,
                      "title"   : "name of alert",
                      "value"   : "value of alert",
                      "args"    : ["list", "of", "arguments"]/null }
Explanation:

* message: this tells smtg that it is a command type message to parse.
* source: this is the id of the registered object that the alert is coming from.
* dest: just like source, but this can be set to null, or not exist. If either
        of these is the case the alert will go to everyone in the Router's 
        registry.
* title: this is the name of the alert, not really neccessary.
* value: this is not neccessary all the time
* args: this is a list of arguments for the alert. If there are no
        arguments needed for the alert args can be ignored or you can use
        a null.



Error Message Structure
------------------------

Error messages can come from anywhere, but most typically from the
attachments. Occasionally there may be a daemon error in which case the source
will be null.
                    { "message" : "err",
                      "dest"    : "obj-id",
                      "source"  : "obj-id"/null,
                      "value"   : "error message",
                      "dead"    : true/false }
Explanation:

* message: this tells you that it is an error type message to parse.
* dest: the object to send the error message to.
* source: the dest of the error, if this value is missing or set to null
          it means the error came from smtgd itself.
* value: the value of the error, normally human readable.
* dead: if the daemon crashed, or is in the process of, it will set this
        to true. 



Command Message Structure
-------------------------

Commands are used by interfaces for making plug-ins do what they want them
to. So commands can vary by plug-in, see the plug-in API for handling these.
                    { "message" : "cmd",
                      "source" : "obj-id",
                      "dest" : "obj-id"/null,
                      "command" : "name of command",
                      "args" : ["list", "of", "arguments"] }
Explanation:

* message: this tells smtg that it is a command type message to parse.
* source: this is the id of the registered object that the cmd is coming from.
* dest: just like source, but this can be set to null, or not exist. If either
        of these is the case SMTG itself will try to execute it.
* name: this is the name of the command to run at the source.
* args: this is a list of arguments for the command. If there are no
        arguments needed for the command args can be removed or you can use
        a null.
        
Examples:

* Here is an example to just grab the daemon stats real quick after the
connecting process is complete:
        {"message":"cmd","source":"0934287342","name":"stats","kill":true}
        
* Heres a more complicated one to update your facebook status through an
imaginary plugin:
        { "message":"cmd","source":"0934287342",
          "dest":"p934728","name":"updateStatus",
          "args":["This is cool!!!"]}
          
* Another example, this time asking the daemon to list the plugins that
are attached to it:
        {"message":"cmd","source":"0934287342"."name":"list-plugins"}


