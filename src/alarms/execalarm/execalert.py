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
from subprocess import Popen
import xml.etree.ElementTree as ET
from empbase.event.alerts import Alert

def ConstructAlert( id, gid, cfgdata, xmldata ):
    gd,aid,valid = gid,'', True
    #pull attribs from xml first to get a baseline.
    if gid != xmldata.attrib["gid"]: valid = False
    try: aid = xmldata.attrib["id"]
    except: 
        valid=False
        logging.error("ID for alarm in ExecAlarm is missing! We have to delete the alarm.")
        
    #TODO: grab old vars from xml?
    
    path = cfgdata.get("path", '')
    name = cfgdata.get("name", '')
    msgasparam = cfgdata.getboolean("msgasparam", False)
    
    alert = ExecAlert(id,gd,path,name,mp)
    alert.isvalid = valid
    alert.ID = aid
    return alert
    
"""
  Certain portions of all the internal variables are saved in different locations
to maintain as accurate information as possible.

/<empsavedir>/alerts.xml
...
<alert gid="" id="">  <----gid is given by execalarm, id is given by EMP
    <var name="" val="" /> <--- backups of values from cfg, could be used for comparison
    ...
</alert>
...

/emp.cfg
...
[alarm_ExecAlarm]
progname_g1 = ''
progpath_g1 = '' 
msgasparam_g1 = False
...

"""
class ExecAlert(Alert):
    def __init__(self, aid, groupid, progpath, progname, msgasparam):
        self.progname = progname
        self.progpath = progpath
        self.msgasparam = msgasparam
        self.groupid = groupid
        self.isvalid = True
        self.ID = id
        
        name = "exec_"+self.groupid
        Alert.__init__(self, name, aid)

    def asCfgDict(self):
        return {"progpath":self.progpath,
                "progname":self.progname,
                "msgasparam":str(self.msgasparam)}
    
    def asXMLNode(self):
        alert = ET.Element("alert", attrib={"gid":self.groupid, "id":self.ID})
        dct = self.asCfgDict()
        for k in dct.keys(): ET.SubElement(alert, "var", attrib={"name":k,"val":dct[k]}) 
        return alert
        
    def run(self, eventobj):
        logging.debug("Launching program %s", self.progname)
        if self.msgasparam:
            pid = Popen([self.progpath, eventobj.msg ]).pid
        else: 
            pid = Popen([self.progpath]).pid
        logging.debug("Launched '%s', pid=%s",(self.progname, pid))
        