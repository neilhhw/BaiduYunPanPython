#!/usr/bin/env python
#-*- coding: utf-8 -*-
import threading
from UniFileSync.lib.common.LogManager import logging

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

    def debug(self):
        """docstring for test"""
        for p in self.__plugin_list:
            logging.debug('load %s ...' % p.name)
