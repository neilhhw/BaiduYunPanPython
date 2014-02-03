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
        res = self.__fileActionTable[msg.header.mid](msg.body)
        self.replyResult(msg, res)

    def handleOper(self, msg):
        """docstring for handleOper"""
        if msg.header.mid == MSG_ID_T_OPER_STOP:
            self.replyResult(msg, E_OK)
            self.stop()

    def handleFileCreate(self, param):
        """docstring for handleFileDelete"""
        logging.debug('[%s]: handleFileCreate: %s, watch dir %s', self.getName(), param['path'], param['watch_dir'])
        pass

    def handleFileDelete(self, param):
        """docstring for handleFileDelete"""
        logging.debug('[%s]: handleFileDelete: %s, watch dir %s', self.getName(), param['path'], param['watch_dir'])
        pass

    def handleFileModify(self, param):
        """docstring for handleFileModify"""
        logging.debug('[%s]: handleFileModify: %s, watch dir %s', self.getName(), param['path'], param['watch_dir'])
        pass

    def handleFileMkdir(self, param):
        """docstring for handleFileMkdir"""
        logging.debug('[%s]: handleFileMkdir: %s', self.getName(), param['dir_path'])
        pass

    def handleFileList(self, param):
        """docstring for handleFileList"""
        logging.debug('[%s]: handleFileList: %s', self.getName(), param['path'])
        pass

    def handleFileSync(self, param):
        """docstring for handleFileSync"""
        logging.debug('[%s]: handleFileSync: %s', self.getName(), param['path'])
        return E_OK
