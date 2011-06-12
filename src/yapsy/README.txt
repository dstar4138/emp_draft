Yapsy is a small library implementing the core mechanisms needed to
build a plugin system into a wider application.

The main purpose is to depend only on Python's standard libraries (at
least version 2.3) and to implement only the basic functionalities
needed to detect, load and keep track of several plugins.

For more info see doc/index.rst

To use yapsy, make sure that the "yapsy" directory is in your Python
loading path and just import the needed class from yapsy (e.g. "from
yapsy.PluginManager import PluginManager"). To see more examples, you
may want to have a look at the unit tests inside the "test" directory.

Please let me know if you find this useful.

Thibauld Nion

Site of the project:
http://yapsy.sourceforge.net/

List of Contributors:
Thibauld Nion
Rob McMullen
Roger Gammans


Note From EMP developers:
There were some changes to this library here is a list of some of the 
major ones:
  - Converted entire library to python 3k
  	 - This means we ran 2to3 on it, and added some of our own changes
  - Added some logging data to make EMP debugging a little easier
  - Removed some unused files to reduce EMP download size.
  - Added the ability to pass parameters when initiating plugins.
  	 - we use this to pass the message handler and for giving the 
  	 plugins some variables we pulled from the config file on start up
  
To see a complete change list, see the git commit log.

fyi: When/if yapsy comes to git this might be pushed into a submodule. 