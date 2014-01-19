#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os, errno
import threading
import ConfigParser

from UniFileSync.lib.common.LogManager import logging

class ConfManager(object):
    """Configuration Manager for UniFileSync"""
    def __init__():
        ''' No __init__ is allowed '''
        pass

    __instance = None
    __lock     = threading.Lock()
    __parser   = ConfigParser.ConfigParser()

    userHome   = os.path.expanduser('~')
    userPluginPath = userHome + '/.UniFileSync/plugin/'
    scriptHome = os.path.dirname(os.path.dirname(os.path.dirname(os.path.realpath(__file__))))
    scripPluginPath = scriptHome + '/plugin/'
    confPath   = scriptHome+'/conf/'
    confName   = 'UniFileSync.ini'

    @staticmethod
    def getManager():
        """Get Plugin Manager instance"""
        ConfManager.__lock.acquire()
        if not ConfManager.__instance:
            ConfManager.__instance = super(ConfManager, ConfManager).__new__(ConfManager)
            super(ConfManager, ConfManager).__init__(ConfManager.__instance)
            ConfManager.__parser.read(ConfManager.confPath+ConfManager.confName)
            ConfManager.__instance.mkdir(ConfManager.userPluginPath)
        ConfManager.__lock.release()
        return ConfManager.__instance

    def getValue(self, key):
        """get config value from key"""
        return ConfManager.__parser.get('UniFileSync', key)

    def setValue(self, key, value):
        """set value to current key"""
        ConfManager.__parser.set('UniFileSync', key, value)

    def getScriptHome(self):
        """get scrip path"""
        return ConfManager.scriptHome

    def getConfPath(self):
        """get configuration path"""
        return ConfManager.confPath

    def getPluginPaths(self):
        """get plugin path"""
        return [ConfManager.scripPluginPath, ConfManager.userPluginPath]

    def mkdir(self, path):
        """mkdir for UniFileSync self defined"""
        try:
            os.makedirs(path)
        except OSError as exc:
            if exc.errno == errno.EEXIST and os.path.isdir(path):
                pass
            else: raise

if __name__ == '__main__':
    print '%s' % ConfManager.getManager().getPluginPaths()
