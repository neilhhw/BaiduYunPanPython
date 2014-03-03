#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import io

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
                MSG_ID_T_FILE_INFO: self.handleFileInfo,
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

        res = E_API_ERR
        result = {}

        syncPath = msg.body['path']
        if msg.body['watch_dir'] == "":
            filePath = syncPath
        filePath = msg.body['watch_dir'] + os.sep +msg.body['path']

        for p in self.pluginManager.getAllPlugins():
            res = p.getAPI().uploadSingleFile(filePath, syncPath)
            result[p.name] = [res]

        res, d = self.parseResult(result)

        if msg.header.ack:
            self.replyResult(msg, res, data=d)

    def handleFileDelete(self, msg):
        """docstring for handleFileDelete"""
        logging.debug('[%s]: handleFileDelete: %s, watch dir %s', self.getName(), msg.body['path'], msg.body['watch_dir'])

        res = E_API_ERR
        result = {}

        filePath = msg.body['path']

        for p in self.pluginManager.getAllPlugins():
            res = p.getAPI().deleteSingleFile(filePath)
            result[p.name] = [res]

        res, d = self.parseResult(result)

        if msg.header.ack:
            self.replyResult(msg, res, data=d)

    def handleFileModify(self, msg):
        """docstring for handleFileModify"""
        logging.debug('[%s]: handleFileModify: %s, watch dir %s', self.getName(), msg.body['path'], msg.body['watch_dir'])

        res = E_API_ERR
        result = {}

        syncPath = msg.body['path']
        if msg.body['watch_dir'] == "":
            filePath = syncPath
        filePath = msg.body['watch_dir'] + os.sep +msg.body['path']

        for p in self.pluginManager.getAllPlugins():
            res = p.getAPI().uploadSingleFile(filePath, syncPath, True)
            result[p.name] = [res]

        res, d = self.parseResult(result)

        if msg.header.ack:
            self.replyResult(msg, res, data=d)

    def handleFileMkdir(self, msg):
        """docstring for handleFileMkdir"""
        logging.debug('[%s]: handleFileMkdir: %s', self.getName(), msg.body['dir_path'])
        pass

    def handleFileList(self, msg):
        """docstring for handleFileList"""
        logging.debug('[%s]: handleFileList: %s', self.getName(), msg.body['path'])
        res = E_API_ERR
        d = ''
        result = {}

        for p in self.pluginManager.getAllPlugins():
            res, d = p.getAPI().lsInCloud(msg.body['path'])
            result[p.name] = [res, d]

        res, d = self.parseResult(result)

        if msg.header.ack:
            self.replyResult(msg, res, data=d)

    def handleFileSync(self, msg):
        """docstring for handleFileSync"""
        logging.debug('[%s]: handleFileSync: %s', self.getName(), msg.body['path'])
        return E_OK

    def handleFileInfo(self, msg):
        """handle get cloud information"""
        logging.debug('[%s]: handleFileInfo: %s', self.getName(), msg.body)

        res = E_API_ERR
        d = ""
        result = {}

        for p in self.pluginManager.getAllPlugins():
            res, d = p.getAPI().getCloudInfo()
            result[p.name] = [res, d]

        res, d = self.parseResult(result)

        if msg.header.ack:
            self.replyResult(msg, res, data=d)

    def handleFileRename(self, msg):
        """docstring for handleFileRename"""
        logging.debug('[%s]: handleFileRename: %s=>%s', self.getName(), msg.body['src_path'], msg.body['path'])
        filePath = msg.body['path']
        isdir = msg.body['isdir']

        res = E_API_ERR
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

    def parseResult(self, result):
        """parse result to return"""
        res = E_OK
        d = {}
        strIO = io.StringIO()

        for k, v in result.iteritems():
            """
            <$PLUGIN_NAME>: $RESULT
             $DATA
            """
            if v[0] != E_OK:
                res = v[0]
            strIO.write(u'\n%s: %s\n' % (k, ERR_STR_TABLE[v[0]]))

            if len(v) > 1:
                strIO.write(u'%s' % v[1])

        d = strIO.getvalue()
        strIO.close()
        logging.debug('[%s]: parseResult%s\n', self.getName(), d)

        return res, d
