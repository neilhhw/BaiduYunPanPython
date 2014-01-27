#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import Queue
import threading
import urllib2

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
        logging.info('[%s] is starting', self.getName())
        self.regToMsgBus()
        while not self.__threadStop:
            try:
                #Block until one message is received
                msg = self.msgQueue.get(True)
                res = self.operTable[msg.mType](msg)
                if res != E_OK:
                    logging.debug('[%s]: handle message %d failure', self.getName(), msg.mID)
            except Queue.Empty, e:
                logging.error('[%s]: Queue item is empty', self.getName())

    def stop(self):
        """stop Controller thread"""
        logging.info('[%s] is stopping', self.getName())
        self.unregFromMsgBus()
        self.__threadStop = True

    def regToMsgBus(self):
        """regsiter message queue to manager"""
        MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_SYNC_ACTOR, self.msgQueue)
        MsgBus.getBus().regReceiver(MSG_UNIQUE_ID_T_CONTROLLER, MSG_UNIQUE_ID_T_SYNC_ACTOR)
        MsgBus.getBus().regReceiver(MSG_UNIQUE_ID_T_FS_MONITOR, MSG_UNIQUE_ID_T_SYNC_ACTOR)

    def unregFromMsgBus(self):
        """regsiter message queue to manager"""
        MsgBus.getBus().unregQ(MSG_UNIQUE_ID_T_SYNC_ACTOR)
        MsgBus.getBus().unregReceiver(MSG_UNIQUE_ID_T_CONTROLLER, MSG_UNIQUE_ID_T_SYNC_ACTOR)
        MsgBus.getBus().unregReceiver(MSG_UNIQUE_ID_T_FS_MONITOR, MSG_UNIQUE_ID_T_SYNC_ACTOR)

    def replyMsg(self, msg, result, **kargs):
        """reply message with result"""
        rMsgQueue = MsgBus.getBus().findQ(msg.mUid)
        rMsgQueue.put(CloudMessage(msg.mType, msg.mID, MSG_UNIQUE_ID_T_SYNC_ACTOR, {'result': result}))

    def handleFile(self, msg):
        """handle file operation"""
        #TODO: improve below codes
        if msg.mID == MSG_ID_T_FILE_CREATE:
            logging.debug('[%s]: Create file: %s', self.getName(), msg.mBody['path'])
            for p in self.pluginManager.getAllPlugins():
                filePath = msg.mBody['path']
                syncPath = self.__getFileName(filePath)
                try:
                    logging.info('%s', p.getAPI().uploadSingleFile(filePath, syncPath))
                except urllib2.HTTPError as exc:
                    print exc
                    pass

        if msg.mID == MSG_ID_T_FILE_MODIFY:
            logging.debug('[%s]: Modify file: %s', self.getName(), msg.mBody['path'])
            for p in self.pluginManager.getAllPlugins():
                filePath = msg.mBody['path']
                syncPath = self.__getFileName(filePath)
                try:
                    logging.info('%s', p.getAPI().uploadSingleFile(filePath, syncPath, True))
                except urllib2.HTTPError as exc:
                    print exc
                    pass

        elif msg.mID == MSG_ID_T_FILE_DELETE:
            logging.debug('[%s]: Delete file: %s', self.getName(), msg.mBody['path'])
            for p in self.pluginManager.getAllPlugins():
                filePath = msg.mBody['path']
                syncPath = self.__getFileName(filePath)
                try:
                    logging.info('%s', p.getAPI().deleteSingleFile(syncPath))
                except urllib2.HTTPError as exc:
                    print exc
                    pass
        elif msg.mID == MSG_ID_T_FILE_LIST:
            logging.debug('[%s]: list path: %s', self.getName(), msg.mBody['path'])
            results = []
            for p in self.pluginManager.getAllPlugins():
                filePath = msg.mBody['path']
                try:
                    res = p.getAPI().lsInCloud(filePath)
                    logging.info('%s', res)
                    results.append({p.name: res})
                except urllib2.HTTPError as exc:
                    print exc
                    pass

            #TODO: need to improve
            if 'ack' in msg.mBody:
                if msg.mBody['ack']:
                    self.replyMsg(msg, results)

        elif msg.mID == MSG_ID_T_FILE_SYNC:
            logging.debug('[%s]: sync path: %s', self.getName(), msg.mBody['path'])
            localDir = msg.mBody['path']
            filelist = os.listdir(localDir)
            for p in self.pluginManager.getAllPlugins():
                for f in filelist:
                    if os.path.isfile(f):
                        logging.info('%s', p.getAPI().uploadSingleFile(localDir + os.sep + f, f))
                    elif os.path.isdir(f):
                        logging.info('%s', p.getAPI().mkdirInCloud(localDir + os.sep + f, f))

            #TODO: need to improve
            if 'ack' in msg.mBody:
                if msg.mBody['ack']:
                    self.replyMsg(msg, E_OK)

        return E_OK

    def __getFileName(self, fullPath):
        """get file name from full path"""
        index = fullPath.rfind(os.sep)
        if index != -1:
            return fullPath[index+1:]
        return fullPath

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
