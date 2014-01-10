#!/usr/bin/env python
#-*- coding: utf-8 -*-

#File Operation
MSG_ID_T_FILE_CREATE = 1
MSG_ID_T_FILE_DELETE = 2
MSG_ID_T_FILE_ADD    = 3
MSG_ID_T_FILE_RENAME = 4
MSG_ID_T_FILE_MKDIR  = 5
MSG_ID_T_FILE_MODIFY = 6

#Internal Operation
MSG_ID_T_OPER_STOP = 7

#Message type
MSG_TYPE_T_FILE = 1
MSG_TYPE_T_OPER = 2
MSG_TYPE_T_RES  = 3
MSG_TYPE_T_CONF = 4

#Message Unique ID
MSG_UNIQUE_ID_T_CONTROLLER      = 0
MSG_UNIQUE_ID_T_SYNC_ACTOR      = 1
MSG_UNIQUE_ID_T_FS_MONITOR      = 2

class CloudMessage():
    """message type for cloud"""
    def __init__(self, mType = None, mID = None, mUid = None, mBody = {}):
        self.mType = mType
        self.mID = mID
        self.mBody = mBody
        self.mUid = mUid

class MsgBus():
    """Message bus"""
    def __init__(self, msgTable={}):
        self.msgTable = msgTable
        self.uniIDList =[MSG_UNIQUE_ID_T_CONTROLLER, MSG_UNIQUE_ID_T_SYNC_ACTOR, MSG_UNIQUE_ID_T_FS_MONITOR]

    def regQ(self, msgUniID, msgQueue):
        """register msg Queue"""
        self.msgTable[msgUniID] = msgQueue

    def findQ(self, msgUniID):
        """find msg queue"""
        return self.msgTable[msgUniID]

    def regUniID(self, msgUniID):
        """register new msg uni ID"""
        self.uniIDList.append(msgUniID)

#This bus is for uniFileSync only
fileSyncMsgBus = MsgBus()
