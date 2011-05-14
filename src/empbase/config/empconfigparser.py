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

import os, sys, logging
from configparser import ConfigParser, DEFAULTSECT
from empbase.attach.attachments import EmpAlarm
from empbase.config.defaults import ATTACHMENT_DIRS, DEFAULT_CONFIGS, \
                                    DEFAULT_CFG_FILES, SAVE_CFG_FILE

CATEGORY_MAP = {"Loops"   : "plug_",
                "Signals" : "plug_",
                "Alarms"  : "alarm_"}

def isCommentBlank(line, comments="#;"):
    l = line.strip()
    if l == '': return True
    if l[0] in comments: return True
    if l.split(None,1)[0].lower() == 'rem' and l[0] in 'rR': return True
    return False
    

class EmpConfigParser(ConfigParser):
    """At its heart, this config parser is a SafeConfigParser. The
    only added functionality is the default configurations automatically
    added and automatic config file validation. Oh, and there are some
    functions for getting certain values quicker.
    
    EmpConfigParser also is given all the default config variables for 
    all the attachments on EMP. This means they can retrieve their 
    variables and they can be adjusted by the user at run time.
    """
    def __init__(self, configfile=None):
        """ Check the config file and include the defaults. """
        self.CONFIG_FILES = DEFAULT_CFG_FILES

        if configfile is not None:
            if not os.path.exists(configfile):
                raise IOError("Configuration File does not exist.")
            
            self.CONFIG_FILES.append(configfile)

        ## now set up the parent class using defaults ##
        ConfigParser.__init__(self)
        #reset internal configparser variable...
        if sys.version_info[0]==3 and sys.version_info[1]<2:            
            # i know thats bad form, but this is what happens when
            # you dont think ahead 
            self._sections=DEFAULT_CONFIGS
        else:
            #this is in python3.2+ only
            self.read_dict(DEFAULT_CONFIGS) 

    def validateInternals(self):
        """ Check all the values you are overwriting from the config 
        file. 
        """
        self.read(self.CONFIG_FILES)
        
        ### ### VALIDATION ### ### 
        #then check if the update speed is valid, must be >= 1 minute
        if self.getfloat("Daemon","update-speed") < 1.0:
            self.set("Daemon","update-speed", 1.0)
            
        #first check logging capabilities.
        if self.getboolean("Logging","logging-on"):              
            self.__try_setup_path(self.get("Logging","log-file"))

    def __try_setup_path(self,path):
        if os.path.exists(path):
            return os.access(path, os.W_OK)
        else:
            try:
                dirs, _ = os.path.split(path)
                if not os.path.exists(dirs):
                    os.makedirs(os.path.abspath(dirs))
            except: 
                return False
            return True
                      
    def getAttachmentVars(self, module):
        """Returns a TinyCfgPrsr of the attachment's variables that were in 
        saved to smtg's config file. TinyCfgPrsr provides some utility functions
        for retrieving the types of variable that were stored there.
        """
        if type(module) is not str: 
            raise TypeError("Plugin Name must be a string")
        
        savedir = self.get("Daemon", "save-dir")
        attach_name="plug_"+module
        try: return TinyCfgPrsr(dict(self.items(attach_name)))
        except:
            attach_name="alarm_"+module
            try: return TinyCfgPrsr(dict(self.items(attach_name)),savedir)
            except: return TinyCfgPrsr({},savedir)
        
    def getAttachmentDirs(self):
        """ Gets the directories that attachments can be found in."""
        #TODO: ?? allow to be changable via cfg file ??
        return ATTACHMENT_DIRS
    
    def getRegistryFile(self):
        """ The registry file to be read in by the Registry object. """
        return self.get("Daemon","registry-file")
    
    def defaultAttachmentVars(self, module, defaults, category):
        """Called by SmtgPluginManager and SmtgAlertManager to load the default
        configurations into the database for use later.
        """
        section = CATEGORY_MAP[category]+module
        if not self.has_section(section):
            self.add_section(section)

        for option in defaults.keys():
            if not self.has_option(section, option):
                self.set(section, option, defaults[option])
    
    def getlist(self, section, option, default=[]):
        """ Utility function for getting a list from the config file. 
        The format for saving them is easy too. """
        try:
            val = self.get(section, option)
            return str(val).split(",")
        except: 
            return default
    
    def save(self, attachments):
        """ Save the configurations to the local user's configuration. """
        if SAVE_CFG_FILE is not None:
            # update the plug-in variables before saving.
            for attach in attachments:
                try:
                    attach.plugin_object.save() #make the plugin save before pulling the configs
                    
                    if isinstance(attach.plugin_object, EmpAlarm):
                        for key in attach.plugin_object.config.keys():
                            self.set("alarm_"+attach.module, str(key), str(attach.plugin_object.config[key]))
                    else:
                        for key in attach.plugin_object.config.keys():
                            self.set("plug_"+attach.module,key,str(attach.plugin_object.config[key]))
                        #else, it doesn't matter 
                except Exception as e: 
                    logging.exception(e)
            
            # make sure it exists and can be written to.
            logging.debug("Trying to save cfg to: %s"%SAVE_CFG_FILE)
            if self.__try_setup_path(SAVE_CFG_FILE):
                fp=None
                try: fp = open(SAVE_CFG_FILE, mode="r+")
                except:# new file 
                    fp = open(SAVE_CFG_FILE, mode="w+")
                    fp.write("#\n# EMP CONFIGS\n#")
                self.update_myfile(fp)
                logging.debug("Saved to cfg file!")
            else:
                logging.error("Couldn't write to cfg file, it cant be created.")

    def update_myfile(self, fp, add_missing=True):
        """ This function was suppose to be released as a standard in 
        python3.2 when they overhauled the configparser module, but they
        didn't. See:
                     http://bugs.python.org/issue1410680
        I included it as a different name, in case they do end up adding it
        later... sigh... I would have thought this would be a more important
        feature request. Obviously the python gods thought otherwise.
        
        Oh, I changed a lot since it was messing with variable order and adding
        random newlines and spacing. I also pushed a couple checks into new 
        functions so I could adjust things later.
        """
        from io import StringIO
        sections = {}
        current = StringIO()
        replacement = [current]
        sect = None
        opt = None
        written = []
        # Default to " = " to match write(), but use the most recent
        # separator found if the file has any options.
        vi = " = "
        while True:
            line = fp.readline()
            if not line:
                break
            # Comment or blank line?
            if isCommentBlank(line):
                current.write(line)
                continue
            # Continuation line?
            if line[0].isspace() and sect is not None and opt:
                if ';' in line:
                    # ';' is a comment delimiter only if it follows
                    # a spacing character
                    pos = line.find(';')
                    if line[pos-1].isspace():
                        comment = line[pos-1:]
                        # Get rid of the newline, and put in the comment.
                        current.seek(-1, 1)
                        current.write(comment + "\n")
                continue
            # A section header or option header?
            else:
                # Is it a section header?
                mo = self.SECTCRE.match(line)
                if mo:
                    # Remember the most recent section with this name,
                    # so that any missing options can be added to it.
                    if sect:
                        sections[sect] = current
                    sect = mo.group('header')
                    current = StringIO()
                    replacement.append(current)
                    if sect in self.sections():
                        current.write(line)
                    # So sections can't start with a continuation line:
                    opt = None
                # An option line?
                else:
                    mo = self.OPTCRE.match(line)
                    if mo:
                        opt, vi, value = mo.group('option', 'vi', 'value')
                        comment = ""
                        if vi in ('=', ':') and ';' in value:
                            # ';' is a comment delimiter only if it follows
                            # a spacing character
                            pos = value.find(';')
                            if value[pos-1].isspace():
                                comment = value[pos-1:]
                        opt = opt.rstrip().lower()
                        if self.has_option(sect, opt):
                            value = self.get(sect, opt)
                            # Fix continuations.
                            value = value.replace("\n", "\n\t")
                            current.write("%s%s%s %s\n" % (opt, vi, value,
                                                          comment))
                            written.append((sect, opt))
        if sect:
            sections[sect] = current
        if add_missing:
            # Add any new sections.
            sects = [DEFAULTSECT]
            sects.extend(self.sections())
            sects.sort()
            for sect in sects:
                if sect == DEFAULTSECT:
                    opts = self._defaults.keys()
                else:
                    # Must use _section here to avoid defaults.
                    opts = self._sections[sect].keys()
                #opts.sort() <-- dont sort my keys
                if sect in sections:
                    output = sections[sect] or current
                else:
                    output = current
                    #only write the non default section headers.
                    if sect is not DEFAULTSECT:
                        output.write("\n[%s]\n" % (sect,))
                    sections[sect] = None
                for opt in opts:
                    if opt != "__name__" and not (sect, opt) in written:
                        value = self.get(sect, opt)
                        # Fix continuations.
                        value = value.replace("\n", "\n\t")
                        output.write("%s%s%s\n" % (opt, vi, value))
                        written.append((sect, opt))
                #output.write("\n")
        # Copy across the new file.
        fp.seek(0)
        fp.truncate()
        for sect in replacement:
            if sect is not None:
                fp.write(sect.getvalue())
        # fp.write("\n")
        fp.close()



class TinyCfgPrsr():
    """ A Utility class to make handling configuration variables easier for
    attachment construction. They mimic the functionality of a standard 
    config parser, but minus a lot of un-needed functions and variables. It
    also just holds one section as a dictionary.
    """
    
    BOOL_CHOICES = {"0":False,"1":True,"no":False,"yes":True,"true":True,
                "false":False,"on":True,"off":False, "":False}
    
    def __init__(self, dictionary, savedir=""):
        self._savedir = savedir
        self._value = dictionary
    
    def keys(self):
        """ Returns a list of the variable names."""
        return list(self._value.keys())
    
    def __getitem__(self, i):
        """ Runs TinyCfgPrsr.get(i, None) to get the string of whatever 
        the variable is holding.
        """
        return self.get(i,None)
    
    def get(self, key, default):
        """ Values are held as strings, so this will return the value 
        as a string.
        """
        if key in self._value:
            return self._value[key]
        else: return default
    
    def getint(self, key, default):
        """ Gets the value held and casts it as an integer, may throw a 
        ValueError if there is a problem casting the value.
        """
        if key in self._value:
            return int(self._value[key])
        else: return default

    def getfloat(self, key, default):
        """ Gets the value held and casts it as a float, may throw a 
        ValueError if there is a problem casting the value.
        """
        if key in self._value:
            return float(self._value[key])
        else: return default

    def getlist(self, key, default):
        """ Gets the value held and parses it as a list. In the emp.cfg files
        lists are held like this:
            [section]
            islist = value1,value2,value3
            notlist = value
        This means that any list given to TinyCfgPrsr will turn it into this 
        string.
        """
        if key in self._value and self._value[key] != '':
            return self._value[key].split(',')
        else: return default
    
    def getboolean(self, key, default):
        """ Gets the value held and casts it as a boolean, may throw a 
        ValueError if there is a problem casting the value.
        """
        if key in self._value:
            res=self._value[key].lower()
            if res in TinyCfgPrsr.BOOL_CHOICES:
                return TinyCfgPrsr.BOOL_CHOICES[res]
            else: return False
        else: return default
    
    def getgroups(self, grouptag="_g*"):
        """If you want a group of variables TinyCfgPrsr can help you get 
        them quickly. Heres an example of what groups are:
            [mysection]
            myinfo = 3843.398
            name_g*1 = bob 
            address_g*1 = 123 mystreet rd
            address_2_g*1 = 12345, New Port, State
            name_g*2 = mary
            phone_g*2 = 128739174
        When you call getgroups() you will get back a TinyCfgPrsr with the
        value 'myinfo' since it doesnt belong to a group, and a dictionary
        with two values '1' and '2' (these can be different strings, just
        using numbers for demonstration). These values map to two 
        TinyCfgPrsrs with the values on the other side of _g*. 
            (eg. name, address, address_2 are the keys in the first 
            TinyCfgPrsr and name, phone are the keys in the other.) 
        """
        defaults = {}
        groups = {}
        for key in self._value.keys():
            if grouptag in key:
                try: 
                    name,group = self.__parsekey(key, grouptag)
                    if group in groups:
                        groups[group].update({name:self._value[key]})
                    else: groups[group] = {name:self._value[key]}
                except: defaults[key] = self._value[key]
        
        tinygroups = {}
        for key in groups.keys():
            tinygroups[key] = TinyCfgPrsr(groups[key])
        
        return TinyCfgPrsr(defaults), tinygroups
    
    def __parsekey(self, key, tag):
        lst = key.split(tag)
        if len(lst) != 2: raise Exception("doesn't have tag")
        else: return lst[0], lst[1]
    
    def __cvrtList(self, val):
        return ",".join(str(n) for n in val)
    
    def set(self, key, value):
        """ Converts the value into a string and then saves it in the
        internal configuration index. Can be retrieved by using the 
        get methods. Can only save integers, floats, booleans, strings,
        and lists of any of the above. Objects and dictionaries are
        expressly prohibited. (for now)
        """
        if type(value) is list:
            value = self.__cvrtList(value)
        elif type(value) is dict:
            raise Exception("Can't save dictionaries in the config file.")
        elif type(value) is object:
            raise Exception("Can't save objects in the config file.")
        else: value = str(value)
        self._value[key] = value

    def setgroup(self, cfgs, groupname, grouptag="_g*"):
        """ Saves a group of variables as a 'group'. Make sure the 
        group name you give is unique from the others, as TinyCfgPrsr
        will not do it for you. If you want a different separator between 
        the variable name and the group-name than'_g*' you can, but make 
        sure you 'getgroups' with the same separator.
        
        cfgs can be a dictionary that you make of variable names to values
        (of any valid value), or another TinyCfgParser (as retrieved from
        'getgroups').
        """
        val = {}
        if type(cfgs) is dict: val = cfgs
        elif type(cfgs) is TinyCfgPrsr: val = cfgs._value
        else: raise Exception("invalid value, must be dictionary or TinyCfgPrsr")
        
        for key in val.keys():
            newkey = key+grouptag+groupname
            self.set(newkey, val[key])
    
    def getMyEmpSaveDir(self, id):
        """ All attachments should save their information in the save directory
        on the local machine and should only work in their own directory.
        An example would be on linux:
                                    ~/.emp/save/2ejqo2/...
        Where '2ejqo2' is the id of the Attachment.
        """
        return self._savedir+"/"+id+"/"
        
    
    