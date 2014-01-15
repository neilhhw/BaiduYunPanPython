#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading
import Queue

from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.LogManager import logging

class FileSysMonitor(threading.Thread):
    """Common File System Monitor"""
    def __init__(self, name=None):
        super(FileSysMonitor, self).__init__()
        if not name:
            self.setName(name)
        self.msgQueue = Queue.Queue()


    def run(self):
        """Child class should run this function before it call it"""
        logging.debug('[%s]: is starting', self.getName())

    def addWatch(self, path):
        """add watch path"""
        logging.debug('[%s]: add watch path %s', self.getName(), path)

    def regQ(self):
        """register message queue to message bus"""
        MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_FS_MONITOR, self.msgQueue)


