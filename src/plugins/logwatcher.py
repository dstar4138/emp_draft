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
from plugins.filewatcher import FileWatcher
from smtg.plugin.smtgplugin import HIGH_IMPORTANCE


class LogWatcher(FileWatcher):
    """Essentially a file watcher except that it can handle log formatting and 
    get just the message, it also knows how to grab the appended data. Which makes
    it quite a bit more useful. (This can also handle local RSS feeds, but its probably 
    better to use the FeedWatcher plug-in).
    """
    
    def __init__(self, conf, comrouter):
        FileWatcher.__init__(self, conf, comrouter)
        self.change_importance(HIGH_IMPORTANCE)
        logging.debug("logwatcher set to high importance")