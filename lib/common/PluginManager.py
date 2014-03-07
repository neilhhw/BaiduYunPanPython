#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import errno
import threading
import imp
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

    def reload(self, name):
        """reload plugin with name"""
        p = self.getPlugin(name)
        if p:
            p.unload()
            p.load()

    def unload(self, name):
        """unload plugin with name"""
        p = self.getPlugin(name)
        if p:
            self.__plugin_list.remove(p)
            p.unload()

    def getPlugin(self, name):
        """get plugin with name"""
        for p in self.__plugin_list:
            if name == p.name:
                return p
        return None

    def getAllPlugins(self):
        """get all loaded plugins"""
        return self.__plugin_list

    def loadPluginFromPath(self, path):
        """load plugin from special path"""
        if os.path.isfile(path):
            imp.load_source('', path)
            logging.debug('[%s] Loading plugin from path %s', 'PluginManager', path)

    def loadAllPlugins(self):
        """load all plugins from destant path"""
        p_paths = ConfManager.getManager().getPluginPaths()
        pluginList = ConfManager.getManager().getValue('common', 'plugins')

        for p in p_paths:
            logging.debug('loadAllPlugins from %s', p)
            #TODO: __import__ the module into our script
            try:
                dirs = os.listdir(p)
                for d in dirs:
                    tmp = '%s%s%s' % (p, os.sep, d)
                    if os.path.isdir(tmp):
                        module_name = 'UniFileSync.plugins.%s' % d
                        module_path = '%s%s%sPlugin.py' % (tmp, os.sep, d)
                        imp.load_source('', module_path)
                        pl = {'name': d, 'path': module_path}
                        if pl not in pluginList:
                            pluginList.append(pl)

            except OSError as exc:
                logging.error('loadAllPlugins listdir error %d', OSError.errno)

        ConfManager.getManager().setValue('common', 'plugins', pluginList)
        logging.debug('[%s]: loadAllPlugins save %s into configuration', 'PluginManager', pluginList)
        ConfManager.getManager().save()


    def unloadAllPlugins(self):
        """unload all plugins"""
        for p in self.__plugin_list:
            p.unload()

    def debug(self):
        """docstring for test"""
        for p in self.__plugin_list:
            logging.debug('load %s ...' % p.name)
