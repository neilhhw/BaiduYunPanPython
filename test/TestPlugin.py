#!/usr/bin/env python
#-*- coding: utf-8 -*-

from UniFileSync.lib.common.Plugin import Plugin, ClouldAPI

class TestPlugin(Plugin):
    """docstring for TestPlugin"""
    def __init__(self, name):
        super(TestPlugin, self).__init__(name)

    def load(self):
        """docstring for load"""
        super(TestPlugin, self).load()
        self.installAPI(TestAPI())

class TestAPI(ClouldAPI):
    """docstring for TestAPI"""
    def __init__(self):
        super(TestAPI, self).__init__()

ta = TestPlugin('TestPlugin')
ta.active()
ta.getAPI()

