#!/usr/bin/env python

import sys
import os
import signal

from BaiduCloud import BaiduCloudActor
from FSMonitor  import FileSysMonitor
from BaiduCloudDefines import msgQueue, CloudMessage, OPER_STOP

def signal_handler(signal, frame):
    """signal handler for any signal"""
    print "[Main]: Press Ctrl+C"
    msgQueue.put(CloudMessage(OPER_STOP, "BaiduCloudActor"))
    msgQueue.put(CloudMessage(OPER_STOP, "FSMonitor"))

def main():
    """This is the main entry for Baidu Cloud Disk"""
    signal.signal(signal.SIGINT, signal_handler)
    cActor = BaiduCloudActor("BaiduCloudActor")
    fMonitor = FileSysMonitor("FSMonitor")
    fMonitor.addWatch(os.getcwd())
    fMonitor.start()
    cActor.start()
    signal.pause()

if __name__ == '__main__':
    main()
