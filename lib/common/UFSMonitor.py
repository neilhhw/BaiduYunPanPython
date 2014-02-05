#!/usr/bin/env python
#-*- coding:utf-8 -*-
import os

from UniFileSync.lib.common.UActor import UActor

from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.Error import *

#Common file operation that should be monitored here
FILE_CREATE     = 0
FILE_DELETE     = 1
FILE_MODIFY     = 2
FILE_MOVED_FROM = 3
FILE_MOVED_TO   = 4

# a map of the actions to names so that we have better logs.
ACTIONS_NAMES = {
    FILE_CREATE     : 'FILE_ACTION_CREATE',
    FILE_DELETE     : 'FILE_ACTION_DELETE',
    FILE_MODIFY     : 'FILE_ACTION_MODIFY',
    FILE_MOVED_FROM : 'FILE_ACTION_MOVED_FROM',
    FILE_MOVED_TO   : 'FILE_ACTION_MOVED_TO',
}

MSG_ID_MAP = {
    FILE_CREATE     :   MSG_ID_T_FILE_CREATE,
    FILE_DELETE     :   MSG_ID_T_FILE_DELETE,
    FILE_MODIFY     :   MSG_ID_T_FILE_MODIFY,
    FILE_MOVED_FROM :   MSG_ID_T_FILE_RENAME,
    FILE_MOVED_TO   :   MSG_ID_T_FILE_RENAME,
}


class UFSMonitor(UActor):
    """UniFileSync common file system monitor"""
    def __init__(self, name=None):
        super(UFSMonitor, self).__init__(name)
        self.setMsgUid(MSG_UNIQUE_ID_T_FS_MONITOR)

        self.addListener(MSG_UNIQUE_ID_T_CONTROLLER)
        self.addHandler(MSG_TYPE_T_OPER, self.handleOper)


    def handleOper(self, msg):
        """handle file operation"""
        if msg.header.mid == MSG_ID_T_OPER_STOP:
            if msg.header.ack:
                self.replyResult(msg, E_OK)
            self.stop()
        elif msg.header.mid == MSG_ID_T_OPER_ADD_WATCH:
            if 'mask' not in msg.body:
                self.addWatch(msg.body['path'])
            else:
                self.addWatch(msg.body['path'], msg.body['mask'])

            if msg.header.ack:
                self.replyResult(msg, E_OK)

    def addWatch(self, path, mask=0):
        """add watch path"""
        logging.debug('[%s]: add watch path %s mask %d', self.getName(), path, mask)

    def notify(self, action, watch_dir, path, src_path=''):
        """notify to others who cares about files change"""

        #TODO: need to improve more than delete operation
        '''
        #If it is delete action, and last change is the same
        if action == FILE_DELETE:
            #We ignore the same action with the same path within some time.
            if action == self.lastChange['action'] and path == self.lastChange['path']:
                if self.lastChange['time'] + 3 < time.time():
                    return False
        else:
            if not os.path.exists(path):
                #For not delete operation, path should exist
                logging.error('[%s]: notify path:%s not exist any more', self.getName(), path)
                return False

        #TODO: buffer some modification changes
        self.lastChange['action'] = action
        self.lastChange['path'] = path
        self.lastChange['time'] = time.time()
        '''

        msg = self.initMsg(MSG_TYPE_T_FILE, MSG_ID_MAP[action])

        #For delete dir, since it does not exist, so it is always False
        isdir = os.path.isdir(watch_dir + os.sep + path)

        logging.debug('[%s]: notify file change: action=>%s, watch_dir=>%s, path=>%s, src_path=>%s, isdir=>%s',
                        self.getName(), ACTIONS_NAMES[action], watch_dir, path, src_path, isdir)
        msg.body = {'path': path, 'action': action, 'src_path': src_path, 'watch_dir': watch_dir, 'isdir': isdir}

        self.notifyListeners(msg)
