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
import sys
from empbase.comm.messages import strToMessage, ERROR_MSG_TYPE

def checkMsg(msg, typeCheck=None):
    """Checks if the return is an error, if it is, it will handle it. If not 
    then it will check it against the provided type. If is not the valid type 
    it will print it right then and there. If it IS the valid type it will 
    return it.
    """
    msg = strToMessage(msg)
    if msg is None: 
        print("ERROR: Is the Daemon running?")
        sys.exit(1)
    
    if msg.getType() == ERROR_MSG_TYPE:
        print("ERROR:",msg.getValue())
        sys.exit(1)
    elif typeCheck is None or typeCheck is type(msg.getValue()):
        return msg.getValue()
    else:
        print(msg.getValue())


def fancyprint(value, indent="",noneval="None!"):
    if type(value) is dict:
        #check if multilevel
        if multileveldict(value):
            fancymultidict(value, indent=indent)
        else:
            fancydict(value)
    elif type(value) is list:
        fancylist(value)
    elif type(value) is bool:
        if value: print("True!")
        else: print("False!")
    elif type(value) is None:
        print(noneval)
    else:
        try:
            val = str(value)
            fancystr(val)
        except: #can't be a string
            print(value) 
    
def fancystr(st):    
    pass

def fancylist(lst, indent=" "):
    print(indent,end="")
    print(", ".join(str(k) for k in sorted(lst)))

def multileveldict(dct):
    if type(dct) is not dict: 
        return False
    else:
        for k in dct.keys():
            if type(dct[k]) is dict:
                return True
        return False

def fancymultidict(dct, indent=" "):
    for k in sorted(dct.keys()):
        print(indent+str(k))
        fancyprint(dct[k], indent=spacegen((indent)+1))

def spacegen(i):
    s=""
    for _ in range(0,i): s+=" "
    return s

def fancydict(dct, buffer=2, st="-", indent=" ", mx=80):
    rside = max(map(len, dct.keys()))
    rside += buffer
    
    def carefulprint(s):
        push=rside+len(st)+len(indent)+1
        count=push
        sent = s.split(" ")
        for i in range(0,len(sent)):
            print(sent[i],end=' ');count+=len(sent[i])+1
            if len(sent)>i+1 and count+len(sent[i+1]) >= mx:
                print("\n"+spacegen(push), end='')
                count=push
        print()
    
    ks = sorted(dct.keys())
    for k in ks:
        print(indent+k,end=spacegen(rside-len(k)))
        carefulprint(st+" "+dct[k])
        