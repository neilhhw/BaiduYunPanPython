#!/usr/bin/env python
# encoding:utf-8

import os
import time
import Queue

from pyinotify import WatchManager, Notifier, \
        ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY, \
        IN_ATTRIB, IN_MOVED_TO, IN_MOVED_FROM

from threading import Thread
from BaiduCloudDefines import CloudMessage, msgQueue, \
        FILE_CREATE, FILE_DELETE, FILE_ADD, FILE_RENAME, \
        FILE_MKDIR, FILE_MODIFY, OPER_STOP

class EventHandler(ProcessEvent):
    """事件处理"""
    def process_IN_CREATE(self, event):
        path = os.path.join(event.path, event.name)
        print   "[FSMonitor:]Create file: %s "  %  path
        msgQueue.put(CloudMessage(FILE_CREATE, path))

    def process_IN_DELETE(self, event):
        path = os.path.join(event.path, event.name)
        print   "[FSMonitor:]Delete file: %s "  %  path
        msgQueue.put(CloudMessage(FILE_DELETE, path))

    def process_IN_MODIFY(self, event):
        path = os.path.join(event.path, event.name)
        print   "[FSMonitor:]Modify file: %s "  %  path
        msgQueue.put(CloudMessage(FILE_MODIFY, path))

    def process_IN_ATTRIB(self, event):
        print   "[FSMonitor:]ATTRIB file: %s "  %   os.path.join(event.path,event.name)

    def process_IN_MOVED_TO(self, event):
        path = [os.path.join(event.path, event.name), event.src_pathname]
        print   "[FSMonitor:]MOVED TO file: %s  =>  %s " % (event.src_pathname , os.path.join(event.path,event.name))
        msgQueue.put(CloudMessage(FILE_RENAME, path))

def FSMonitor(path='.'):
        wm = WatchManager()
        mask = IN_DELETE | IN_CREATE | IN_MODIFY | IN_ATTRIB | IN_MOVED_TO | IN_MOVED_FROM
        notifier = Notifier(wm, EventHandler())
        wm.add_watch(path, mask,auto_add=True,rec=True)
        wm.add_watch('/home/neilhhw', mask,auto_add=True,rec=True)
        print 'now starting monitor %s'%(path)
        while True:
            try:
               notifier.process_events()
               if notifier.check_events():
                   notifier.read_events()
            except KeyboardInterrupt:
                notifier.stop()
                break

class FileSysMonitor(Thread):
    """File system monitor thread"""
    def __init__(self, name=None):
        super(FileSysMonitor, self).__init__()

        if name != None:
            self.setName(name)

        self.wm = WatchManager()
        self.mask = IN_DELETE | IN_CREATE | IN_MODIFY | IN_ATTRIB | IN_MOVED_TO
        self.notifier = Notifier(self.wm, EventHandler())

    def addWatch(self, path):
        """Add watch for path"""
        self.wm.add_watch(path, self.mask, auto_add=True, rec=True)
        print 'now starting monitor %s' % (path)

    def addMask(self, mask):
        """Add watcher mask"""
        self.mask = self.mask | mask

    def run(self):
        """Thread entry"""
        print self.getName()
        while True:
            if self.notifier.check_events(500):
                self.notifier.read_events()
                self.notifier.process_events()
            try:
                item = msgQueue.get(False)
                if item.action == OPER_STOP and item.filepath == self.getName():
                    self.stop()
                    print "[FSMonitor]: Stop this thread"
                    break;
            except Queue.Empty:
                pass

    def stop(self):
        """Stop watch"""
        self.notifier.stop()

if __name__ == "__main__":
    fsThread = FileSysMonitor("Thread-FSMonitor")
    fsThread.start()

    while True:
        try:
            item = msgQueue.get(True, 5)
            print "[FSMonitor TEST]: %s %s" % (str(item.action), item.filepath)
        except KeyboardInterrupt:
            fsThread.stop()
            break;
        except Queue.Empty:
            print "Queue is empty"
            time.sleep(5)


