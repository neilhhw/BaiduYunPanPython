#!/usr/bin/env python
# encoding:utf-8

import threading
import os

from UniFileSync.lib.common.UFSMonitor import (
        UFSMonitor,
        FILE_CREATE,
        FILE_DELETE,
        FILE_MODIFY,
        FILE_MOVED_FROM,
        FILE_MOVED_TO)

from UniFileSync.lib.common.LogManager import logging

from pyinotify import WatchManager, Notifier, \
        ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY, \
        IN_ATTRIB, IN_MOVED_TO, IN_MOVED_FROM

class EventHandler(ProcessEvent):
    def my_init(self, **kargs):
        """according to doc"""
        self.fsMonitor = kargs["fsMonitor"]

    """事件处理"""
    def process_IN_CREATE(self, event):
        #path = os.path.join(event.path, event.name)
        self.fsMonitor.notify(FILE_CREATE, event.path, event.name)

    def process_IN_DELETE(self, event):
        #path = os.path.join(event.path, event.name)
        self.fsMonitor.notify(FILE_DELETE, event.path, event.name)

    def process_IN_MODIFY(self, event):
        #path = os.path.join(event.path, event.name)
        #self.fsMonitor.notify(FILE_MODIFY, path)
        self.fsMonitor.notify(FILE_MODIFY, event.path, event.name)

    def process_IN_ATTRIB(self, event):
        logging.debug('[%s]: ATTRIB file: %s', self.fsMonitor.getName(), os.path.join(event.path,event.name))

    def process_IN_MOVED_TO(self, event):
        logging.debug('[%s]: name=>%s, path=>%s, src_pathname=>%s', event.name, event.path, event.src_pathname)
        self.fsMonitor.notify(FILE_MOVED_TO, event.path, event.name, event.src_pathname)

    def process_IN_MOVED_FROM(self, event):
        """docstring for process_IN_MOVED_FROM"""
        pass

class LinuxFileSysMonitor(UFSMonitor):
    """File system monitor thread"""
    def __init__(self, name=None):
        super(LinuxFileSysMonitor, self).__init__(name)
        self.defaultMask = IN_DELETE | IN_CREATE | IN_MODIFY | IN_MOVED_TO | IN_MOVED_FROM
        self.wm = WatchManager()
        self.__lock = threading.Lock()

    def addWatch(self, path, mask=0):
        """Add watch for path"""
        super(LinuxFileSysMonitor, self).addWatch(path, mask)
        if mask == 0:
            mask = self.defaultMask
        self.wm.add_watch(path, mask, auto_add=True, rec=True)

    def run(self):
        """Thread entry"""
        super(LinuxFileSysMonitor, self).run()
        self.notifier = Notifier(self.wm, EventHandler(None, fsMonitor = self))

        while self.isRunning:
            self.processMsg(1)
            if self.notifier.check_events(1000):
                self.notifier.read_events()
                self.notifier.process_events()

    def stop(self):
        """Stop watch"""
        super(LinuxFileSysMonitor, self).stop()
        self.notifier.stop()

if __name__ == '__main__':
    f = LinuxFileSysMonitor('FSMonitor-Test')
    #f.addWatch('D:\\')
    f.addWatch(os.getcwd())
    f.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print "Press [Ctrl+C]"
        f.stop()
