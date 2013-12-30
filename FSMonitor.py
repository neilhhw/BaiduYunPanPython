#!/usr/bin/env python
# encoding:utf-8

import os
import time
import Queue

from pyinotify import WatchManager, Notifier, \
        ProcessEvent, IN_DELETE, IN_CREATE, IN_MODIFY, \
        IN_ATTRIB, IN_MOVED_TO, IN_MOVED_FROM

from threading import Thread
from MsgManager import *

class EventHandler(ProcessEvent):
    def my_init(self, **kargs):
        """according to doc"""
        self.msgQueue = kargs["queue"]

    """事件处理"""
    def process_IN_CREATE(self, event):
        path = os.path.join(event.path, event.name)
        print   "[FSMonitor]: Create file: %s "  %  path
        self.msgQueue.put(CloudMessage(MSG_TYPE_T_FILE, MSG_ID_T_FILE_CREATE, MSG_UNIQUE_ID_T_FS_MONITOR, {"path": path}))

    def process_IN_DELETE(self, event):
        path = os.path.join(event.path, event.name)
        print   "[FSMonitor]: Delete file: %s "  %  path
        self.msgQueue.put(CloudMessage(MSG_TYPE_T_FILE, MSG_ID_T_FILE_DELETE, MSG_UNIQUE_ID_T_FS_MONITOR, {"path": path}))

    def process_IN_MODIFY(self, event):
        path = os.path.join(event.path, event.name)
        print   "[FSMonitor]: Modify file: %s "  %  path
        self.msgQueue.put(CloudMessage(MSG_TYPE_T_FILE, MSG_ID_T_FILE_MODIFY, MSG_UNIQUE_ID_T_FS_MONITOR, {"path": path}))

    def process_IN_ATTRIB(self, event):
        print   "[FSMonitor]: ATTRIB file: %s "  %   os.path.join(event.path,event.name)

    def process_IN_MOVED_TO(self, event):
        print   "[FSMonitor]: MOVED TO file: %s  =>  %s " % (event.src_pathname , os.path.join(event.path,event.name))
        self.msgQueue.put(CloudMessage(MSG_TYPE_T_FILE, MSG_ID_T_FILE_RENAME, MSG_UNIQUE_ID_T_FS_MONITOR,
                                        {"src": event.src_pathname, "dest": event.path}))

    def process_IN_MOVED_FROM(self, event):
        """docstring for process_IN_MOVED_FROM"""
        pass

class FileSysMonitor(Thread):
    """File system monitor thread"""
    def __init__(self, name=None):
        super(FileSysMonitor, self).__init__()

        if name != None:
            self.setName(name)

        self.msgQueue = Queue.Queue()
        self.wm = WatchManager()
        self.mask = IN_DELETE | IN_CREATE | IN_MODIFY | IN_ATTRIB | IN_MOVED_TO | IN_MOVED_FROM

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
        self.bActorMsgQueue = msgManager.findQ(MSG_UNIQUE_ID_T_BAIDU_ACTOR)
        self.notifier = Notifier(self.wm, EventHandler(None, queue = self.bActorMsgQueue))

        while True:
            if self.notifier.check_events(1000):
                self.notifier.read_events()
                self.notifier.process_events()
            try:
                msg = self.msgQueue.get(False)
                if msg.mType == MSG_TYPE_T_OPER:
                    if msg.mID == MSG_ID_T_OPER_STOP:
                        print "[%s]: Stop" % self.getName()
                        self.replyMsg(msg, E_OK)
                        self.stop()
                        break
                else:
                    print "[FSMonitor]: Not accept other type 0x%X message:" % msg.mType
            except Queue.Empty:
                pass

    def replyMsg(self, msg, result):
        """reply message with result"""
        rMsgQueue = msgManager.findQ(msg.mUid)
        rMsgQueue.put(CloudMessage(msg.mType, msg.mID, MSG_UNIQUE_ID_T_FS_MONITOR, {0: result}))

    def stop(self):
        """Stop watch"""
        self.notifier.stop()

    def getMsgQueue(self):
        """Get current thread message queue"""
        return self.msgQueue

    def regQ(self):
        """Register its message queue to manager"""
        msgManager.regQ(MSG_UNIQUE_ID_T_FS_MONITOR, self.msgQueue)

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


