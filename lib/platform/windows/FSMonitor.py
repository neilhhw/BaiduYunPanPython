#!/usr/bin/env python
# -*- coding: utf-8 *-*

from UniFileSync.lib.common.FSMonitor import (
        FileSysMonitor,
        FILE_CREATE,
        FILE_DELETE,
        FILE_MODIFY,
        FILE_MOVED_FROM,
        FILE_MOVED_TO)

from UniFileSync.lib.common.LogManager import logging

from pywintypes import OVERLAPPED
from win32api import CloseHandle
from win32con import (
    FILE_SHARE_READ,
    FILE_SHARE_WRITE,
    FILE_FLAG_BACKUP_SEMANTICS,
    FILE_NOTIFY_CHANGE_FILE_NAME,
    FILE_NOTIFY_CHANGE_DIR_NAME,
    FILE_NOTIFY_CHANGE_ATTRIBUTES,
    FILE_NOTIFY_CHANGE_SIZE,
    FILE_NOTIFY_CHANGE_LAST_WRITE,
    FILE_NOTIFY_CHANGE_SECURITY,
    OPEN_EXISTING)

from win32file import (
    AllocateReadBuffer,
    CreateFileW,
    CreateIoCompletionPort,
    GetQueuedCompletionStatus,
    GetOverlappedResult,
    ReadDirectoryChangesW,
    FILE_FLAG_OVERLAPPED,
    FILE_NOTIFY_INFORMATION)

from win32event import (
    CreateEvent,
    INFINITE,
    SetEvent,
    WaitForMultipleObjects,
    WAIT_OBJECT_0)

# map between windows events to common FSMonitor
ACTIONS = {
    1: FILE_CREATE,
    2: FILE_DELETE,
    3: FILE_MODIFY,
    4: FILE_MOVED_FROM,
    5: FILE_MOVED_TO,
}

# constant found in the msdn documentation:
# http://msdn.microsoft.com/en-us/library/ff538834(v=vs.85).aspx
FILE_LIST_DIRECTORY = 0x0001
FILE_NOTIFY_CHANGE_LAST_ACCESS = 0x00000020
FILE_NOTIFY_CHANGE_CREATION = 0x00000040

FILESYSTEM_MONITOR_MASK = FILE_NOTIFY_CHANGE_FILE_NAME | \
    FILE_NOTIFY_CHANGE_DIR_NAME | \
    FILE_NOTIFY_CHANGE_ATTRIBUTES | \
    FILE_NOTIFY_CHANGE_SIZE | \
    FILE_NOTIFY_CHANGE_LAST_WRITE | \
    FILE_NOTIFY_CHANGE_SECURITY | \
    FILE_NOTIFY_CHANGE_LAST_ACCESS

class WinFileSysMonitor(FileSysMonitor):
    """File system monitor for windows"""
    def __init__(self, name=None):
        super(WinFileSysMonitor, self).__init__(name)
        self.mask = FILESYSTEM_MONITOR_MASK
        self.buf_size = 0x100
        self.comKey = 0
        self.watchList = []
        self.watchPath = []
        self.ioComPort = None
        self.overlapped = OVERLAPPED()
        self.overlapped.hEvent = CreateEvent(None, 0, 0, None)

    def run(self):
        """Thread entry"""
        super(WinFileSysMonitor, self).run()

        while not self.threadStop:
            buffers = []
            for handle in self.watchList:
                buf = AllocateReadBuffer(self.buf_size)
                ReadDirectoryChangesW(
                        handle,
                        buf,
                        True,  # Always watch children
                        self.mask,
                        self.overlapped
                        )
                buffers.append(buf)

            ec, data_len, comKey, overlapped = GetQueuedCompletionStatus(self.ioComPort, 1000)
            #logging.debug('[%s]: GetQueuedCompletionStatus: error: %d, data length: %d, key %d', self.getName(), ec, data_len, comKey)
            #print "%d %d %d" % (ec, data_len, comKey)
            #print overlapped
            #if not ec:
                # Stop event
            #    break
            # if we continue, it means that we got some data, lets read it
            # lets ead the data and store it in the results
            if ec != 0:
                continue

            events = FILE_NOTIFY_INFORMATION(buffers[comKey], data_len)
            for action, path in events:
                #print '[%s]: action %d, %s' %(self.getName(), action, path)
                #full_path = self.watchPath[comKey] + '\\' + path
                self.notify(ACTIONS[action], self.watchPath[comKey]+path)
            buffers[comKey] = None


    def addWatch(self, path, mask=None):
        """Add watcher for path"""
        super(WinFileSysMonitor, self).addWatch(path, mask)
        handle = CreateFileW(
                path,
                FILE_LIST_DIRECTORY,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OVERLAPPED,
                None)

        self.ioComPort = CreateIoCompletionPort(handle, self.ioComPort, self.comKey, 0)
        if mask:
            self.mask = mask
        self.watchList.append(handle)
        self.watchPath.append(path)
        self.comKey += 1

    def stop(self):
        """stop current thread"""
        super(WinFileSysMonitor, self).stop()
        for handle in self.watchList:
            CloseHandle(handle)

if __name__ == '__main__':
    import os
    f = WinFileSysMonitor('FSMonitor-Test')
    f.addWatch('D:\\')
    f.addWatch('C:\\')
    f.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print "Press [Ctrl+C]"
        f.stop()
