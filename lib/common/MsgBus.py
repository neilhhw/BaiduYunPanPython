#!/usr/bin/env python
#-*- coding: utf-8 -*-
import threading
from UniFileSync.lib.common.LogManager import logging

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

class MsgBus(object):
    """Message bus"""
    def __init__():
        """Forbid __init__(self)"""
        pass

    __instance = None
    __lock     = threading.Lock()
    __msg_table = {}
    __uni_ID_list = [MSG_UNIQUE_ID_T_CONTROLLER, MSG_UNIQUE_ID_T_SYNC_ACTOR, MSG_UNIQUE_ID_T_FS_MONITOR]

    @staticmethod
    def getBus():
        """Get Message Bus singlone instance"""
        MsgBus.__lock.acquire()
        if not MsgBus.__instance:
            MsgBus.__instance = super(MsgBus, MsgBus).__new__(MsgBus)
            super(MsgBus, MsgBus).__init__(MsgBus.__instance)
        MsgBus.__lock.release()
        return MsgBus.__instance

    def regQ(self, msgUniID, msgQueue):
        """register msg Queue"""
        self.__msg_table[msgUniID] = msgQueue

    def findQ(self, msgUniID):
        """find msg queue"""
        return self.__msg_table[msgUniID]

    def regUniID(self, msgUniID):
        """register new msg uni ID"""
        self.__uni_ID_list.append(msgUniID)

    def unregQ(self, msgUniID):
        """unregister msg queue"""
        self.__msg_table[msgUniID] = None
        self.__uni_ID_list.remove(msgUniID)
