"""
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

import logging
from empbase.config.empconfigparser import EmpConfigParser

#The format of the logging to the screen, log file.
_LOGGING_FORMAT_ = "%(levelname)-8s::[%(asctime)s]-%(funcName)s@%(lineno)d %(message)s"
_DATE_FORMAT_ = "%a, %d %b %Y %H:%M:%S"

def setup_logging(configuration):
    """ Sets up the logging system for SMTG. 
    Requires a reference to the SMTGConfigParser that was built at
    the start of the program. Once this method has been called in 
    SmtgDaemon, all logging.*(msg) methods will go to the correct
    locations.
    
    Debugging - all debug information is pushed to stdout
    Warnings/Errors - all other information goes to their respective
        files taken from the configuration.
    Info - These are ignored and should not be used.
    """
    # if config param not the right type, return failed
    if type(configuration) is not EmpConfigParser:
        raise TypeError("Configuration isn't valid SmtgConfigParser object")
    
    # if no logging wanted, return setup success
    if not configuration.getboolean("Logging","logging-on"):
        #if debug mode on though, print to sys.stderr
        if configuration.getboolean("Logging","debug-mode"):
            logging.basicConfig(level=logging.DEBUG,
                            format=_LOGGING_FORMAT_,
                            datefmt=_DATE_FORMAT_)

    # since config wanted, check if we want debug:
    if configuration.getboolean("Logging","debug-mode"):
        logging.basicConfig(level=logging.DEBUG,
                            format=_LOGGING_FORMAT_,
                            datefmt=_DATE_FORMAT_,
                            filename=configuration.get("Logging","log-file"))
        console = logging.StreamHandler()
        console.setLevel(logging.DEBUG)
        logging.getLogger().addHandler(console)
        
    elif configuration.getboolean("Logging","log-warnings"):
        logging.basicConfig(level=logging.WARNING,
                            format=_LOGGING_FORMAT_,
                            datefmt=_DATE_FORMAT_,
                            filename=configuration.get("Logging","log-file"))
        
    else:# Errors are always logged. deal.
        logging.basicConfig(level=logging.ERROR,
                            format=_LOGGING_FORMAT_,
                            datefmt=_DATE_FORMAT_,
                            filename=configuration.get("Logging","log-file"))

    