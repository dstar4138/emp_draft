EMP Files!
=============

This gets its own file in the documentation tree because its just that 
important. Emp Files are formated like Windows INI files and EMP's own 
configuration file. They discribe the Attachment to EMP so that it can verify
and validate, and even configure it before it EMP even finishes loading.

*NOTE: All Attachments have to have an Emp file.*

An EMP file has three sections, in each section there are some required and
some optional variables. If they are required, I will state that in the 
description.


[Core] Section
--------------

The core section is the most important and has three required variables.

* Name : The name of your Attachment that will show up in Interfaces.
* Module : The relative location to your the class file implementing it.
* Cmd : The default command name that people will use to target this attachment.
* load : If this is present and set to 'False', then EMP wont even load the 
         Attachment into memory for your use. 
         

[Defaults] Section
------------------

This is where you can set variables that your attachment will get at run time. 
All the variables here are optional, however there are a few "Special" key
variable names that you should be aware of:

* required : if this is present and set to 'True', then if the Attachment can't
             be loaded for whatever reason, the daemon will not load.
         
* makeactive : If this is present and set to 'False', then EMP will load the 
               Attachment, but won't let it run or update or trigger. It can
               be activated at runtime at anytime my asking EMP to activate it.

* importance : Only useful for LoopPlugs, but this determines its position in 
               the Pull-Loop. The Higher the importance value, the sooner it 
               gets to be updated in the Pull-Loop. You can get fancy with this
               and define when each and every LoopPlug gets updated, or you can
               just utilize the defaults.


[Documentation] Section
-----------------------

Everything in this section is optional, but will be viewable to the user when
asked for via EMP's general case interface. There are a set number of variables
in this section, so anything else you add wont be readable.

* Author
* Version
* Website
* Copyright
* Description


