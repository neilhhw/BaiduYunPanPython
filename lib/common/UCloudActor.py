#!/usr/bin/env python
#-*- coding: utf-8 -*-
from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.Error import *

from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.PluginManager import PluginManager
from UniFileSync.lib.common.UActor import UActor

class UCloudActor(UActor):
    """docstring for UCloudActor"""
    def __init__(self, name=None):
        super(UCloudActor, self).__init__(name)
        self.setMsgUid(MSG_UNIQUE_ID_T_CLOUD_ACTOR)
        self.pluginManager = PluginManager.getManager()

        self.addListener(MSG_UNIQUE_ID_T_CONTROLLER)
        self.addListener(MSG_UNIQUE_ID_T_FS_MONITOR)

        self.addHandler(MSG_TYPE_T_FILE, self.handleFile)
        self.addHandler(MSG_TYPE_T_OPER, self.handleOper)

        self.__fileActionTable = {
                MSG_ID_T_FILE_CREATE: self.handleFileCreate,
                MSG_ID_T_FILE_DELETE: self.handleFileDelete,
                MSG_ID_T_FILE_MODIFY: self.handleFileModify,
                MSG_ID_T_FILE_MKDIR: self.handleFileMkdir,
                MSG_ID_T_FILE_LIST: self.handleFileList,
                MSG_ID_T_FILE_SYNC: self.handleFileSync,
                MSG_ID_T_FILE_RENAME: self.handleFileRename,
                }

    def run(self):
        """UCloudActor entry"""
        super(UCloudActor, self).run()
        while self.isRunning:
            self.msgLoop()

    def handleFile(self, msg):
        """docstring for handleFile"""
        if msg.header.mid not in self.__fileActionTable:
            return E_INVILD_PARAM
        self.__fileActionTable[msg.header.mid](msg)

    def handleOper(self, msg):
        """docstring for handleOper"""
        if msg.header.mid == MSG_ID_T_OPER_STOP:
            if msg.header.ack:
                self.replyResult(msg, E_OK)
            self.stop()

    def handleFileCreate(self, msg):
        """docstring for handleFileDelete"""
        logging.debug('[%s]: handleFileCreate: %s, watch dir %s', self.getName(), msg.body['path'], msg.body['watch_dir'])
        pass

    def handleFileDelete(self, msg):
        """docstring for handleFileDelete"""
        logging.debug('[%s]: handleFileDelete: %s, watch dir %s', self.getName(), msg.body['path'], msg.body['watch_dir'])
        pass

    def handleFileModify(self, msg):
        """docstring for handleFileModify"""
        logging.debug('[%s]: handleFileModify: %s, watch dir %s', self.getName(), msg.body['path'], msg.body['watch_dir'])
        pass

    def handleFileMkdir(self, msg):
        """docstring for handleFileMkdir"""
        logging.debug('[%s]: handleFileMkdir: %s', self.getName(), msg.body['dir_path'])
        pass

    def handleFileList(self, msg):
        """docstring for handleFileList"""
        logging.debug('[%s]: handleFileList: %s', self.getName(), msg.body['path'])
        res = E_OK
        data = None

        for p in self.pluginManager.getAllPlugins():
            res, data = p.getAPI().lsInCloud(msg.body['path'])

        if msg.header.ack:
            self.replyResult(msg, res)
        return res, data

    def handleFileSync(self, msg):
        """docstring for handleFileSync"""
        logging.debug('[%s]: handleFileSync: %s', self.getName(), msg.body['path'])
        return E_OK

    def handleFileRename(self, msg):
        """docstring for handleFileRename"""
        logging.debug('[%s]: handleFileRename: %s=>%s', self.getName(), msg.body['src_path'], msg.body['path'])
        filePath = msg.body['path']
        isdir = msg.body['isdir']

        res = E_OK
        for p in self.pluginManager.getAllPlugins():
            if isdir:
                #res = p.getAPI().mkdirInCloud(path)
                pass
            else:
                #res = p.getAPI().uploadSingleFile(filePath, syncPath)
                pass

        if msg.header.ack:
            self.replyResult(msg, res)
        return res
