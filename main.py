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
    msgQueue = msgManager.findQ(0)
    msgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, 0, {}))

def handleFile(msg):
    """handle file operation"""
    pass

def handleOper(msg):
    """handle file operation"""
    bMsgQueue = msgManager.findQ(BaiduCloudActor.ident)
    fMsgQueue = msgManager.findQ(FSMonitor.ident)
    mMsgQueue = msgManager.findQ(0)

    if msg.mID == MSG_ID_T_OPER_STOP:
        bMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, 0, {}))
        fMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, 0, {}))

        msg = mMsgQueue.get(True, 2)
        if msg.mTid == BaiduCloudActor.ident and msg.mID == MSG_ID_T_OPER_STOP:
            if msg.mBody[0] == E_OK:
                print "Stop BaiduCloudActor OK"
            else
                print "Stop BaiduCloudActor NOK: 0x%X" % msg.mBody[0]

        msg = mMsgQueue.get(True, 2)
        if msg.mTid == FSMonitor.ident and msg.mID == MSG_ID_T_OPER_STOP:
            if msg.mBody[0] == E_OK:
                print "Stop BaiduCloudActor OK"
            else
                print "Stop BaiduCloudActor NOK: 0x%X" % msg.mBody[0]

        sys.exit(-1)

def handleRes(msg):
    """handle file operation"""
    pass

def handleConf(msg):
    """handle file operation"""
    pass

operTable = {
        MSG_TYPE_T_FILE, lambda msg : handleFile(msg)
        MSG_TYPE_T_OPER, lambda msg : handleOper(msg)
        MSG_TYPE_T_RES , lambda msg : handleRes(msg)
        MSG_TYPE_T_CONF, lambda msg : handleConf(msg)

        }

def main():
    """This is the main entry for Baidu Cloud Disk"""
    msgQueue = Queue.Queue()
    msgManager.regQ(0, msgQueue)
    signal.signal(signal.SIGINT, signal_handler)
    cActor = BaiduCloudActor("BaiduCloudActor")
    fMonitor = FileSysMonitor("FSMonitor")
    fMonitor.addWatch(os.getcwd())
    fMonitor.start()
    cActor.start()

    while True:
        msg = msgQueue.get(True)
        operTable[msg.mType](msg)


if __name__ == '__main__':
    main()
