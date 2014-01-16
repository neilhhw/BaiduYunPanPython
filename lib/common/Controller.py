#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
import Queue
import threading

from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.FSMonitor import *
from UniFileSync.lib.common.SyncActor import SyncActor
from UniFileSync.lib.common.LogManager import logging


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

    def regQ(self):
        """register queue to message bus"""
        MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_CONTROLLER, self.msgQueue)

    def unregQ(self):
        """unregister queue to message bus"""
        MsgBus.getBus().unregQ(MSG_UNIQUE_ID_T_CONTROLLER)

    def run(self):
        """thread entry"""
        logging.debug('[%s]: is starting', self.getName())
        self.regQ()
        sActor = SyncActor("SyncActor")
        fMonitor = FileSysMonitor("FSMonitor")
        fMonitor.addWatch(os.getcwd())
        fMonitor.start()
        sActor.start()

        while not self.__threadStop:
            try:
                msg = self.msgQueue.get(True)
                # Block until get one message
                if msg != None:
                    self.operTable[msg.mType](msg)
            except Queue.Empty:
                pass

    def stop(self):
        """stop Controller thread"""
        logging.debug('[%s] is stopping', self.getName())
        self.unregQ()
        self.__threadStop = True

    def handleFile(self, msg):
        """handle file operation"""
        pass

    def handleOper(self, msg):
        """handle file operation"""
        bMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_BAIDU_ACTOR)
        fMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_FS_MONITOR)
        #mMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_CONTROLLER)

        if msg.mID == MSG_ID_T_OPER_STOP:
            bMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_CONTROLLER, {}))
            fMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_CONTROLLER, {}))

            '''
            msg = mMsgQueue.get(True, 2)
            if msg.mUid == MSG_UNIQUE_ID_T_BAIDU_ACTOR and msg.mID == MSG_ID_T_OPER_STOP:
                if msg.mBody[0] == E_OK:
                    print "Stop BaiduCloudActor OK"
                else:
                    print "Stop BaiduCloudActor NOK: 0x%X" % msg.mBody[0]

            msg = mMsgQueue.get(True, 2)
            if msg.mUid == MSG_UNIQUE_ID_T_FS_MONITOR and msg.mID == MSG_ID_T_OPER_STOP:
                if msg.mBody[0] == E_OK:
                    print "Stop FSMonitor OK"
                else:
                    print "Stop FSMonitor NOK: 0x%X" % msg.mBody[0]

            '''
            self.stop()

    def handleRes(self, msg):
        """handle file operation"""
        pass

    def handleConf(self, msg):
        """handle file operation"""
        pass


if __name__ == '__main__':
    controller = Controller('UniFileSync Controller')
    controller.start()

    while True:
        try:
            pass
        except KeyboardInterrupt:
            logging.info('[UniFileSync Controller]: Press Ctrl+C')
            msgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_CONTROLLER)
            msgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_CONTROLLER, {}))
