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
        logging.debug('%s is loading', self.name)
        return True

    def unload(self):
        """Plugin unload"""
        logging.debug('%s is unloading', self.name)
        return True

    def active(self):
        """Make plugin active"""
        self.manager.loadPlugin(self)
        logging.debug(self.name + ' is active')
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
    def __init__(self, name=None):
        super(ClouldAPI, self).__init__()
        self.name = name

    def applyAccess(self):
        """docstring for applyAccess"""
        return True

    def getToken(self):
        """docstring for getToken"""
        return True

    def uploadSingleFile(self, filePath, syncPath=None):
        """upload single file to net disk"""
        return True

    def downloadSingleFile(self, filePath, syncPath=None):
        """download single file from net disk"""
        return True

    def deleteSingleFile(self, filePath, syncPath=None):
        """delete single file from net disk"""
        return True

    def mkdirInCloud(self, dirPath):
        """make dir in net disk"""
        return True

    def lsInCloud(self, dirPath):
        """list files in dirPath in cloud"""
        return True



