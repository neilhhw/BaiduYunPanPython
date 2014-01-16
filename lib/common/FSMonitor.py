#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading
import Queue

from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.LogManager import logging

#Common file operation that should be monitored here
FILE_CREATE     = 0
FILE_DELETE     = 1
FILE_MODIFY     = 2
FILE_MOVED_FROM = 3
FILE_MOVED_TO   = 4

# a map of the actions to names so that we have better logs.
ACTIONS_NAMES = {
    0: 'FILE_ACTION_CREATE',
    1: 'FILE_ACTION_DELETE',
    2: 'FILE_ACTION_MODIFY',
    3: 'FILE_ACTION_MOVED_FROM',
    4: 'FILE_ACTION_MOVED_TO',
}

class FileSysMonitor(threading.Thread):
    """Common File System Monitor"""
    def __init__(self, name=None):
        super(FileSysMonitor, self).__init__()
        if name:
            self.setName(name)
        self.msgQueue = Queue.Queue()
        self.threadStop = False
        #logging.debug('[FileSysMonitor]: __init__ name %s', name)

    def run(self):
        """Child class should run this function before it call it"""
        logging.debug('[%s]: is starting', self.getName())
        self.regQ()

    def addWatch(self, path, mask=None):
        """add watch path"""
        logging.debug('[%s]: add watch path %s', self.getName(), path)
        if mask:
            logging.debug('[%s]: add watch mask %d', mask)

    def regQ(self):
        """register message queue to message bus"""
        MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_FS_MONITOR, self.msgQueue)

    def stop(self):
        """stop Controller thread"""
        logging.debug('[%s] is stopping', self.getName())
        self.unregQ()
        self.threadStop = True

    def unregQ(self):
        """regsiter message queue to manager"""
        MsgBus.getBus().unregQ(MSG_UNIQUE_ID_T_FS_MONITOR)

    def notify(self, action, path):
        """notify to others who cares about files change"""
        logging.debug('[%s]: action: %s path %s', self.getName(), ACTIONS_NAMES[action], path)
        #print 'action: %s path %s' % (ACTIONS_NAMES[action], path)
