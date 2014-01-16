#!/usr/bin/env python
#-*- coding: utf-8 -*-
import Queue
import threading

from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.Error import *

from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.PluginManager import PluginManager

class SyncActor(threading.Thread):
    """This is Sync actor thread with cloud APIs that Plugins provide"""
    def __init__(self, name=None):
        super(SyncActor, self).__init__()
        if name:
            self.setName(name)
        self.msgQueue = Queue.Queue()

        self.operTable = {
                MSG_TYPE_T_FILE: lambda msg : self.handleFile(msg),
                MSG_TYPE_T_OPER: lambda msg : self.handleOper(msg),
                MSG_TYPE_T_RES : lambda msg : self.handleRes(msg),
                MSG_TYPE_T_CONF: lambda msg : self.handleConf(msg)
                }

        self.pluginManager = PluginManager.getManager()

        self.__threadStop = False

    def run(self):
        """Thread main function"""
        logging.info('[%s] is starting',self.getName())
        self.regQ()
        while not self.__threadStop:
            try:
                #Block until one message is received
                msg = self.msgQueue.get(True)
                res = self.operTable[msg.mType](msg)
                if res != E_OK:
                    logging.debug('[%s]: handle message %d failure', msg.mID)
            except Queue.Empty, e:
                logging.error('[%s]: Queue item is empty', self.getName())

    def stop(self):
        """stop Controller thread"""
        logging.debug('[%s] is stopping', self.getName())
        self.unregQ()
        self.__threadStop = True

    def regQ(self):
        """regsiter message queue to manager"""
        MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_SYNC_ACTOR, self.msgQueue)

    def unregQ(self):
        """regsiter message queue to manager"""
        MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_SYNC_ACTOR)

    def replyMsg(self, msg, result):
        """reply message with result"""
        rMsgQueue = MsgBus.getBus().findQ(msg.mUid)
        rMsgQueue.put(CloudMessage(msg.mType, msg.mID, MSG_UNIQUE_ID_T_SYNC_ACTOR, {0: result}))

    def handleFile(self, msg):
        """handle file operation"""
        if msg.mID == MSG_ID_T_FILE_CREATE:
            logging.debug('[%s]: Create file: %s', self.getName(), msg.mBody['path'])
            try:
                for p in self.pluginManager.getAllPlugins():
                    p.getAPI().uploadSingleFile(msg.mBody['path'])
            except urllib2.HTTPError, e:
                logging.error('[%s]: get HTTP error %s', self.getName(), str(e))
            finally:
                pass
        elif msg.mID == MSG_ID_T_FILE_DELETE:
            print "[%s]: Delete file: %s" % (self.getName(), msg.mBody["path"])
            try:
                for p in self.pluginManager.getAllPlugins():
                    p.getAPI().deleteSingleFile(msg.mBody['path'])
            except urllib2.HTTPError, e:
                logging.error('[%s]: get HTTP error %s', self.getName(), str(e))
            finally:
                pass

        return E_OK

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
