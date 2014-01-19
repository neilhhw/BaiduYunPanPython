#!/usr/bin/env python
# encoding:utf-8

import threading
import os

from UniFileSync.lib.common.FSMonitor import (
        FileSysMonitor,
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
        path = os.path.join(event.path, event.name)
        self.fsMonitor.notify(FILE_CREATE, path)

    def process_IN_DELETE(self, event):
        path = os.path.join(event.path, event.name)
        self.fsMonitor.notify(FILE_DELETE, path)

    def process_IN_MODIFY(self, event):
        path = os.path.join(event.path, event.name)
        self.fsMonitor.notify(FILE_MODIFY, path)

    def process_IN_ATTRIB(self, event):
        logging.debug('[%s]: ATTRIB file: %s', self.fsMonitor.getName(), os.path.join(event.path,event.name))

    def process_IN_MOVED_TO(self, event):
        self.fsMonitor.notify(FILE_MOVED_TO, os.path.join(event.path, event.name), os.path.join(event.path, event.src_pathname))

    def process_IN_MOVED_FROM(self, event):
        """docstring for process_IN_MOVED_FROM"""
        pass

class LinuxFileSysMonitor(FileSysMonitor):
    """File system monitor thread"""
    def __init__(self, name=None):
        super(LinuxFileSysMonitor, self).__init__(name)
        self.defaultMask = IN_DELETE | IN_CREATE | IN_MODIFY | IN_MOVED_TO | IN_MOVED_FROM
        self.wm = WatchManager()
        self.__lock = threading.Lock()

    def addWatch(self, path, mask=None):
        """Add watch for path"""
        super(LinuxFileSysMonitor, self).addWatch(path, mask)
        if not mask:
            mask = self.defaultMask
        self.wm.add_watch(path, mask, auto_add=True, rec=True)

    def run(self):
        """Thread entry"""
        super(LinuxFileSysMonitor, self).run()
        self.notifier = Notifier(self.wm, EventHandler(None, fsMonitor = self))

        while not self.threadStop:
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
