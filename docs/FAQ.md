# EMP F.A.Q. #

Just in case all the documentation doesn't help I've provided this FAQ so that
any questions people have can be answered for everyone. So if you have any 
questions about ANYHING relating to EMP, just let me know and I'll answer it 
here.

-------------------------------------------------------------------------------

### Why Python 3.2? ###


Well because the python gods did a major update to 3.* on how ConfigParser 
defaults are read in. Previously I was having to do a pretty major hack that I 
hated so that I could pull it off the way I wanted to do it. It also adds a lot
more features and language reworkings to make things faster. So please upgrade.

If you have a version higher then 3.2, good for you. :P


### Why not Python 2.*? ###

Because I'm not stuck in a cave. I will eventually get around to writing a 
backported interface for 2.*, but I have no intention of backporting the whole
EMP Daemon over.


### Can I use a different language to interface with EMP? ###


Yep, as long as you keep to the EMP Message Protocol and use a UTF-8 encoded
TCP socket.


### Can I use a different language to write an Attachment? ###


Yep, as long as you write a wrapper in Python and provide an EMP file.


### What is this YAPSY thing? ###


YAPSY is this awesome library that makes the whole Attachment searching and 
loading work. I made a few changes to port it to Python3.2 and to work with
EMP, but its essentially all the same. Here's a link to the original:
<http://yapsy.sourceforge.net/>

                    
### How does Attachment X work? ###

I don't know, you will have to ask the Attachment developer if they weren't kind
enough to provide a README or some form of documentation. Anything in the base
release has documentation either in the EMP file as a comment or in a README
file bundled with it.

                              
### Can an Attachment be both a Plug and an Alarm? ###

You bet, but of course they would need to implement the functionality of both.
This also means that the attachment will be utilized as both. (This means that
there will be two references in the Daemon but only one instance of it.)


### Can I have multiple instances of the same Attachment running? ###


Short answer: No   
Shortish answer: Maybe in the future.   
Why would you want to though? In most, if not all, cases its a flaw in design
of the attachment that causes the "need" for a separate one. And if its so bad
that you can't or plum don't want to rewrite your code to be more flexible and
adaptive, write a wrapper that spawns instances and acts like an Attachment.




