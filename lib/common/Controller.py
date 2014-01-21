#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
import Queue
import threading
import platform

from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.SyncActor import SyncActor
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.PluginManager import PluginManager

if platform.system() == 'Windows':
    from UniFileSync.lib.platform.windows.FSMonitor import WinFileSysMonitor as FileSysMonitor
elif platform.system() == 'Linux':
    from UniFileSync.lib.platform.linux.FSMonitor import LinuxFileSysMonitor as FileSysMonitor
else:
    pass


class Controller(threading.Thread):
    """UniFileSync Controller"""
    def __init__(self, name=None):
        super(Controller, self).__init__()
        if name:
            self.setName(name)
        self.msgQueue = Queue.Queue()
        self.__threadStop = False

        self.operTable = {
                         MSG_TYPE_T_FILE: lambda msg : self.handleFile(msg),
                         MSG_TYPE_T_OPER: lambda msg : self.handleOper(msg),
                         MSG_TYPE_T_RES : lambda msg : self.handleRes(msg),
                         MSG_TYPE_T_CONF: lambda msg : self.handleConf(msg)
                         }

    def regToMsgBus(self):
        """register queue to message bus"""
        MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_CONTROLLER, self.msgQueue)
        MsgBus.getBus().regReceiver(MSG_UNIQUE_ID_T_FS_MONITOR, MSG_UNIQUE_ID_T_CONTROLLER)
        MsgBus.getBus().regReceiver(MSG_UNIQUE_ID_T_SYNC_ACTOR, MSG_UNIQUE_ID_T_CONTROLLER)

    def unregFromMsgBus(self):
        """unregister queue to message bus"""
        MsgBus.getBus().unregQ(MSG_UNIQUE_ID_T_CONTROLLER)
        MsgBus.getBus().unregReceiver(MSG_UNIQUE_ID_T_FS_MONITOR, MSG_UNIQUE_ID_T_CONTROLLER)
        MsgBus.getBus().unregReceiver(MSG_UNIQUE_ID_T_SYNC_ACTOR, MSG_UNIQUE_ID_T_CONTROLLER)

    def run(self):
        """thread entry"""
        logging.info('[%s]: is starting', self.getName())
        self.regToMsgBus()
        PluginManager.getManager().loadAllPlugins()
        self.sActor = SyncActor("SyncActor")
        self.fMonitor = FileSysMonitor("FSMonitor")
        self.fMonitor.addWatch(os.getcwd()+'/conf')
        self.fMonitor.start()
        self.sActor.start()

        while not self.__threadStop:
            try:
                msg = self.msgQueue.get(True, 2)
                # Block until get one message
                if msg != None:
                    logging.debug('[%s]: receives message ID: %d, Type: %d', self.getName(), msg.mID, msg.mType)
                    self.operTable[msg.mType](msg)
            except Queue.Empty:
                pass

    def stop(self):
        """stop Controller thread"""
        logging.info('[%s] is stopping', self.getName())
        self.unregFromMsgBus()
        self.__threadStop = True

    def handleFile(self, msg):
        """handle file operation"""
        pass

    def handleOper(self, msg):
        """handle file operation"""
        sMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_SYNC_ACTOR)
        fMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_FS_MONITOR)
        #mMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_CONTROLLER)

        if msg.mID == MSG_ID_T_OPER_STOP:
            logging.debug('[%s]: do stop', self.getName())
            sMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_CONTROLLER, {}))
            fMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_CONTROLLER, {}))

            ack_msg = self.msgQueue.get(True)
            if ack_msg.mUid == MSG_UNIQUE_ID_T_SYNC_ACTOR and ack_msg.mID == MSG_ID_T_OPER_STOP:
                if ack_msg.mBody['result'] == E_OK:
                    logging.debug('[%s]: stop sync actor OK', self.getName())
                else:
                    logging.debug('[%s]: stop sync actor NOK=>%d', self.getName(), ack_msg.mBody['result'])

            ack_msg = self.msgQueue.get(True)
            if ack_msg.mUid == MSG_UNIQUE_ID_T_FS_MONITOR and ack_msg.mID == MSG_ID_T_OPER_STOP:
                if ack_msg.mBody['result'] == E_OK:
                    logging.debug('[%s]: stop file system monitor OK', self.getName())
                else:
                    logging.debug('[%s]: stop file system monitor NOK=>%d', self.getName(), ack_msg.mBody['result'])

            self.replyMsg(msg, E_OK)
            self.stop()
        elif msg.mID == MSG_ID_T_OPER_ADD_WATCH:
            self.fMonitor.addWatch(msg.mBody['path'], msg.mBody['mask'])

    def replyMsg(self, msg, result):
        """reply message with result"""
        rMsgQueue = MsgBus.getBus().findQ(msg.mUid)
        rMsgQueue.put(CloudMessage(msg.mType, msg.mID, MSG_UNIQUE_ID_T_CONTROLLER, {'result': result}))
        logging.debug('[%s]: replyMsg: ID=>%d, uID=>%d, result=>%d', self.getName(), msg.mID, msg.mUid, result)


    def handleRes(self, msg):
        """handle file operation"""
        pass

    def handleConf(self, msg):
        """handle file operation"""
        pass


if __name__ == '__main__':
    controller = Controller('UniFileSync Controller')
    controller.start()
    MSG_UNIQUE_ID_T_TEST = 5
    MsgBus.getBus().regUniID(MSG_UNIQUE_ID_T_TEST)
    msgQueue = Queue.Queue()
    MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_TEST, msgQueue)

    try:
        while True:
            pass
    except KeyboardInterrupt:
        logging.info('[UniFileSync Controller]: Press Ctrl+C')
        cMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_CONTROLLER)
        cMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_TEST, {}))
        msg = msgQueue.get(True)

