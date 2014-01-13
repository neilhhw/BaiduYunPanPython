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

    def load(self):
        """Plugin load"""
        return True

    def unload(self):
        """Plugin unload"""
        return True

    def active(self):
        """Make plugin active"""
        self.manager.loadPlugin(self)
        logging.debug(self.name + ' is active')
        return True
