#!/usr/bin/env python
#-*- coding: utf-8 -*-
from UniFileSync.lib.common.PluginManager import PluginManager
from UniFileSync.lib.common.LogManager import logging

class Plugin(object):
    """UniFileSync Plugin class"""
    def __init__(self, name):
        super(Plugin, self).__init__()
        self.name = name
        self.manager = PluginManager.getManager()
        self.__API = None

    def load(self):
        """Plugin load"""
        logging.info('[%s] is loading', self.name)

    def unload(self):
        """Plugin unload"""
        logging.info('[%s] is unloading', self.name)

    def active(self):
        """Make plugin active"""
        self.manager.loadPlugin(self)
        logging.info(self.name + ' is active')
        return True

    def getAPI(self):
        """get plugin cloud API"""
        if not self.__API:
            logging.error(self.name + ' does not have any cloud API')
        return self.__API

    def installAPI(self, api):
        """install cloud API to plugin"""
        self.__API = api

    def uninstallAPI(self):
        """uninstall Plugin related API"""
        self.__API = None

#===========================Plug-in Class for SYNC API =====================
class ClouldAPI(object):
    """This is common API for cloud sync
       Plug in should extract this class
    """
    def __init__(self, name):
        super(ClouldAPI, self).__init__()
        self.name = name

    def applyAccess(self):
        """docstring for applyAccess"""
        logging.debug('[%s]: applyAccess', self.name)

    def getToken(self):
        """docstring for getToken"""
        logging.debug('[%s]: getToken', self.name)

    def refreshToken(self):
        """refresh token method"""
        logging.debug('[%s]: refreshToken', self.name)

    def uploadSingleFile(self, filePath, syncPath, isReplace=False):
        """upload single file to net disk"""
        logging.debug('[%s]: uploadSingleFile %s => %s, is replace? %d', self.name, filePath, syncPath, isReplace)

    def downloadSingleFile(self, filePath, syncPath=None):
        """download single file from net disk"""
        logging.debug('[%s]: downloadSingleFile %s', self.name, filePath)

    def deleteSingleFile(self, filePath, syncPath=None):
        """delete single file from net disk"""
        logging.debug('[%s]: deleteSingleFile %s', self.name, filePath)

    def mkdirInCloud(self, dirPath):
        """make dir in net disk"""
        logging.debug('[%s]: mkdirInCloud %s', self.name, dirPath)

    def mvInCloud(self, toPath, fromPath):
        """move in net disk"""
        logging.debug('[%s]: mvInCloud %s=>%s', self.name, fromPath, toPath)

    def lsInCloud(self, filePath):
        """list files in filePath in cloud"""
        logging.debug('[%s]: lsInCloud %s', self.name, filePath)

    def parseResult(self, data):
        """parse plugin result"""
        logging.debug('[%s]: parseResult %s...', self.name, data)

    def errorHandler(self, error):
        """error handler"""
        logging.debug('[%s]: errorHandler error\n%s', self.name, error)

    def getName(self):
        """get API name"""
        return self.name

    def getCloudInfo(self):
        """get cloud disk information"""
        logging.debug('[%s]: getCloudInfo...', self.name)

