#!/usr/bin/env python

import sys
import os
import signal
import Queue

from BaiduCloud import BaiduCloudActor
from FSMonitor  import FileSysMonitor

from MsgManager import *

def signal_handler(signal, frame):
    """signal handler for any signal"""
    print "[Main]: Press Ctrl+C"
    msgQueue = msgManager.findQ(MSG_UNIQUE_ID_T_MAIN)
    msgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_MAIN, {}))

def handleFile(msg):
    """handle file operation"""
    pass

def handleOper(msg):
    """handle file operation"""
    bMsgQueue = msgManager.findQ(MSG_UNIQUE_ID_T_BAIDU_ACTOR)
    fMsgQueue = msgManager.findQ(MSG_UNIQUE_ID_T_FS_MONITOR)
    mMsgQueue = msgManager.findQ(MSG_UNIQUE_ID_T_MAIN)

    if msg.mID == MSG_ID_T_OPER_STOP:
        bMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_MAIN, {}))
        fMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_MAIN, {}))

        '''
        msg = mMsgQueue.get(True, 2)
        if msg.mUid == MSG_UNIQUE_ID_T_BAIDU_ACTOR and msg.mID == MSG_ID_T_OPER_STOP:
            if msg.mBody[0] == E_OK:
                print "Stop BaiduCloudActor OK"
            else:
                print "Stop BaiduCloudActor NOK: 0x%X" % msg.mBody[0]

        msg = mMsgQueue.get(True, 2)
        if msg.mUid == MSG_UNIQUE_ID_T_FS_MONITOR and msg.mID == MSG_ID_T_OPER_STOP:
            if msg.mBody[0] == E_OK:
                print "Stop FSMonitor OK"
            else:
                print "Stop FSMonitor NOK: 0x%X" % msg.mBody[0]

        '''
        sys.exit(-1)

def handleRes(msg):
    """handle file operation"""
    pass

def handleConf(msg):
    """handle file operation"""
    pass

operTable = {
        MSG_TYPE_T_FILE: lambda msg : handleFile(msg),
        MSG_TYPE_T_OPER: lambda msg : handleOper(msg),
        MSG_TYPE_T_RES : lambda msg : handleRes(msg),
        MSG_TYPE_T_CONF: lambda msg : handleConf(msg)
        }

def main():
    """This is the main entry for Baidu Cloud Disk"""
    msgQueue = Queue.Queue()
    msgManager.regQ(MSG_UNIQUE_ID_T_MAIN, msgQueue)
    signal.signal(signal.SIGINT, signal_handler)
    cActor = BaiduCloudActor("BaiduCloudActor")
    cActor.regQ()
    fMonitor = FileSysMonitor("FSMonitor")
    fMonitor.regQ()
    fMonitor.addWatch(os.getcwd())
    fMonitor.start()
    cActor.start()

    while True:
        try:
            msg = msgQueue.get(True, 2)
            if msg != None:
                operTable[msg.mType](msg)
        except Queue.Empty:
            pass

if __name__ == '__main__':
    main()
