# -*- coding: utf-8 *-*
from threading import Thread

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

# map between windows events and pyinotify
'''ACTIONS = {
    1: IN_CREATE,
    2: IN_DELETE,
    3: IN_MODIFY,
    4: IN_MOVED_FROM,
    5: IN_MOVED_TO,
}
'''

# a map of the actions to names so that we have better logs.
ACTIONS_NAMES = {
    1: 'IN_CREATE',
    2: 'IN_DELETE',
    3: 'IN_MODIFY',
    4: 'IN_MOVED_FROM',
    5: 'IN_MOVED_TO',
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

class FileSysMonitor(Thread):
    """File system monitor for windows"""
    def __init__(self, name=None):
        super(FileSysMonitor, self).__init__()
        if name != None:
            self.setName(name)

        #self.msgQueue = Queue.Queue()
        self.mask = FILESYSTEM_MONITOR_MASK
        self.buf_size = 0x100
        self.comKey = 0
        self.watchList = []
        self.watchPath = []
        self.ioComPort = None
        self.overlapped = OVERLAPPED()
        self.overlapped.hEvent = CreateEvent(None, 0, 0, None)
        self.threadStop = False

    def run(self):
        """Thread entry"""
        print self.getName()

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

            #print 'Thread run @ port 0x%X' % self.ioComPort
            ec, data_len, comKey, overlapped = GetQueuedCompletionStatus(self.ioComPort, 1000)
            #print "%d %d %d" % (ec, data_len, comKey)
            #print overlapped
            #if not ec:
                # Stop event
            #    break
            # if we continue, it means that we got some data, lets read it
            # lets ead the data and store it in the results
            events = FILE_NOTIFY_INFORMATION(buffers[comKey], data_len)
            for action, path in events:
                print "Action: %s Path %s" % (ACTIONS_NAMES[action], self.watchPath[comKey] + '\\' + path)

    def addWatch(self, path, mask=None):
        """Add watcher for path"""
        handle = CreateFileW(
                path,
                FILE_LIST_DIRECTORY,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OVERLAPPED,
                None)

        self.ioComPort = CreateIoCompletionPort(handle, self.ioComPort, self.comKey, 0)
        if mask != None:
            self.mask = mask
        self.watchList.append(handle)
        self.watchPath.append(path)
        self.comKey += 1

    def stop(self):
        """stop current thread"""
        self.threadStop = True
        for handle in self.watchList:
            CloseHandle(handle)

if __name__ == '__main__':
    f = FileSysMonitor('FSMonitor-Test')
    f.addWatch('D:\\')
    f.addWatch('C:\\')
    f.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print "Press [Ctrl+C]"
        f.stop()
