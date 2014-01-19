#!/usr/bin/env python
#-*- coding:utf-8 -*-

import threading
import Queue

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

class FileSysMonitor(threading.Thread):
    """Common File System Monitor"""
    def __init__(self, name=None):
        super(FileSysMonitor, self).__init__()
        if name:
            self.setName(name)
        self.msgQueue = Queue.Queue()
        self.threadStop = False
        self.defaultMask = 0

        self.operTable = {
                MSG_TYPE_T_FILE: lambda msg : self.handleFile(msg),
                MSG_TYPE_T_OPER: lambda msg : self.handleOper(msg),
                MSG_TYPE_T_RES : lambda msg : self.handleRes(msg),
                MSG_TYPE_T_CONF: lambda msg : self.handleConf(msg)
                }

    def run(self):
        """Child class should run this function before it call it"""
        self.regToMsgBus()
        logging.info('[%s]: is starting', self.getName())

    def addWatch(self, path, mask=None):
        """add watch path"""
        if mask:
            tmp = mask
        else:
            tmp = self.defaultMask

        logging.debug('[%s]: add watch path %s mask %d', self.getName(), path, tmp)


    def regToMsgBus(self):
        """register message queue to message bus"""
        MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_FS_MONITOR, self.msgQueue)
        MsgBus.getBus().regReceiver(MSG_UNIQUE_ID_T_CONTROLLER, MSG_UNIQUE_ID_T_FS_MONITOR)

    def stop(self):
        """stop Controller thread"""
        logging.info('[%s] is stopping', self.getName())
        self.unregFromMsgBus()
        self.threadStop = True

    def unregFromMsgBus(self):
        """regsiter message queue to manager"""
        MsgBus.getBus().unregQ(MSG_UNIQUE_ID_T_FS_MONITOR)
        MsgBus.getBus().unregReceiver(MSG_UNIQUE_ID_T_CONTROLLER, MSG_UNIQUE_ID_T_FS_MONITOR)

    def notify(self, action, path, src_path=None):
        """notify to others who cares about files change"""
        if src_path:
            logging.debug('[%s]: action: %s path: %s, src_path: %s', self.getName(), ACTIONS_NAMES[action], path, src_path)
            mBody = {'path': path, 'action': action, 'src_path': src_path}
        else:
            logging.debug('[%s]: action: %s path: %s', self.getName(), ACTIONS_NAMES[action], path)
            mBody = {'path': path, 'action': action}

        for recID in MsgBus.getBus().getReceivers(MSG_UNIQUE_ID_T_FS_MONITOR):
            msgQueue = MsgBus.getBus().findQ(recID)
            if msgQueue:
                msgQueue.put(CloudMessage(MSG_TYPE_T_FILE, MSG_ID_MAP[action], MSG_UNIQUE_ID_T_FS_MONITOR, mBody))

    def processMsg(self, timeout=None):
        """process message loop for not blocking"""
        try:
            msg = self.msgQueue.get(True, timeout)
            if msg != None:
                res = self.operTable[msg.mType](msg)
                if res != E_OK:
                    logging.debug('[%s]: handle message %d failure', self.getName(), msg.mID)
        except Queue.Empty, e:
            '''
            if timeout:
                logging.debug('[%s]: processMsg get empty queue item within %d', self.getName(), timeout)
            else:
                logging.error('[%s]: processMsg get empty queue item while blocking', self.getName())
            '''
        finally:
            pass

    def handleOper(self, msg):
        """handle file operation"""
        if msg.mID == MSG_ID_T_OPER_STOP:
            self.replyMsg(msg, E_OK)
            self.stop()
        return E_OK

    def handleRes(self, msg):
        """handle file operation"""
        return E_OK

    def handleConf(self, msg):
        """handle file operation"""
        return E_OK


    def handleFile(self, msg):
        """handle file operation"""
        return E_OK

    def replyMsg(self, msg, result):
        """reply message with result"""
        rMsgQueue = MsgBus.getBus().findQ(msg.mUid)
        rMsgQueue.put(CloudMessage(msg.mType, msg.mID, MSG_UNIQUE_ID_T_FS_MONITOR, {'result': result}))
