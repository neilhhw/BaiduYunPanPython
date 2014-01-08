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
        self.overlapped = OVERLAPPED()
        self.overlapped.hEvent = CreateEvent(None, 0, 0, None)
        self.wait_stop = CreateEvent(None, 0, 0, None)

    def run(self):
        """Thread entry"""
        print self.getName()
        while True:
            buf = AllocateReadBuffer(self.buf_size)

            ReadDirectoryChangesW(
                self.handle,
                buf,
                True,  # Always watch children
                self.mask,
                self.overlapped,
            )

            rc = WaitForMultipleObjects((self.wait_stop,
                                         self.overlapped.hEvent),
                                         0, INFINITE)
            if rc == WAIT_OBJECT_0:
                # Stop event
                break
            # if we continue, it means that we got some data, lets read it
            data = GetOverlappedResult(self.handle, self.overlapped, True)
            # lets ead the data and store it in the results
            events = FILE_NOTIFY_INFORMATION(buf, data)
            for action, path in events:
                print "Action: %s Path %s" % (ACTIONS_NAMES[action], path)

    def addWatch(self, path):
        """Add watcher for path"""
        self.handle = CreateFileW(
                path,
                FILE_LIST_DIRECTORY,
                FILE_SHARE_READ | FILE_SHARE_WRITE,
                None,
                OPEN_EXISTING,
                FILE_FLAG_BACKUP_SEMANTICS | FILE_FLAG_OVERLAPPED,
                None)

if __name__ == '__main__':
    f = FileSysMonitor()
    f.addWatch('.')
    f.start()
    try:
        while True:
            pass
    except KeyboardInterrupt:
        print "Press [Ctrl+C]"
