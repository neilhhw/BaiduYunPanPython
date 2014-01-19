#!/usr/bin/env python
#-*- coding: utf-8 -*-
import threading
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.ConfManager import ConfManager

class PluginManager(object):
    """Plugin Manager"""
    def __init__():
        pass

    __instance = None
    __lock     = threading.Lock()
    __plugin_list = []

    @staticmethod
    def getManager():
        """Get Plugin Manager instance"""
        PluginManager.__lock.acquire()
        if not PluginManager.__instance:
            PluginManager.__instance = super(PluginManager, PluginManager).__new__(PluginManager)
            super(PluginManager, PluginManager).__init__(PluginManager.__instance)
        PluginManager.__lock.release()
        return PluginManager.__instance

    def register(self, plugin):
        """register plugin to manager"""
        self.__plugin_list.append(plugin)
        logging.debug(plugin.name + ' registers to PluginManager')

    def loadPlugin(self, plugin):
        """active related plugin"""
        self.register(plugin)
        plugin.load()

    def reload(self, plugin):
        """reload plugin"""
        plugin.unload()
        plugin.load()

    def getPlugin(self, name):
        """get plugin with name"""
        for p in self.__plugin_list:
            if name == p.name:
                return p
        return None

    def getAllPlugins(self):
        """get all loaded plugins"""
        return self.__plugin_list

    def loadAllPlugins(self):
        """load all plugins from destant path"""
        p_paths = ConfManager.getManager().getPluginPaths()
        for p in p_paths:
            logging.debug('loadAllPlugins from %s', p)
            #TODO: __import__ the module into our script

    def debug(self):
        """docstring for test"""
        for p in self.__plugin_list:
            logging.debug('load %s ...' % p.name)
