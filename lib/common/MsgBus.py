#!/usr/bin/env python
#-*- coding: utf-8 -*-
import threading
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.Error import *

#File Operation
MSG_ID_T_FILE_CREATE = 1
MSG_ID_T_FILE_DELETE = 2
MSG_ID_T_FILE_MODIFY = 3
MSG_ID_T_FILE_RENAME = 4
MSG_ID_T_FILE_MKDIR  = 5
MSG_ID_T_FILE_LIST   = 6
MSG_ID_T_FILE_SYNC   = 7

#Internal Operation
MSG_ID_T_OPER_STOP      = 0
MSG_ID_T_OPER_ADD_WATCH = 1

#Message type
MSG_TYPE_T_FILE = 1
MSG_TYPE_T_OPER = 2
MSG_TYPE_T_RES  = 3
MSG_TYPE_T_CONF = 4

#Message Unique ID
MSG_UNIQUE_ID_T_CONTROLLER      = 0
MSG_UNIQUE_ID_T_SYNC_ACTOR      = 1
MSG_UNIQUE_ID_T_FS_MONITOR      = 2


#==============================================================================
#TODO: need below improve
"""
Message type is below
Header:
    message type
    message ID
    receiver UID
    sender  UID
Body:
    {
        'XXX': 'XXX'
    }

"""

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
    __rec_table = {MSG_UNIQUE_ID_T_CONTROLLER: [MSG_UNIQUE_ID_T_SYNC_ACTOR, MSG_UNIQUE_ID_T_FS_MONITOR]}

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
        if  msgUniID not in self.__uni_ID_list:
            logging.error('regQ failure due to no Unique Message ID registered')
            return E_INVILD_PARAM
        MsgBus.__lock.acquire()
        self.__msg_table[msgUniID] = msgQueue
        MsgBus.__lock.release()
        return E_OK

    def findQ(self, msgUniID):
        """find msg queue"""
        return self.__msg_table[msgUniID]

    def regUniID(self, msgUniID):
        """register new msg uni ID"""
        if msgUniID not in self.__uni_ID_list:
            MsgBus.__lock.acquire()
            self.__uni_ID_list.append(msgUniID)
            MsgBus.__lock.release()
            return E_OK
        logging.error('regUniID failure due to Unique Message ID %d already registered', msgUniID)
        return E_INVILD_PARAM

    def unregQ(self, msgUniID):
        """unregister msg queue"""
        MsgBus.__lock.acquire()
        self.__msg_table[msgUniID] = None
        self.__uni_ID_list.remove(msgUniID)
        MsgBus.__lock.release()

    def regReceiver(self, msgUniID, recMsgUniID):
        """register receiver to related msg unique ID"""
        MsgBus.__lock.acquire()
        if msgUniID not in self.__rec_table:
            self.__rec_table[msgUniID] = []
        if recMsgUniID not in self.__rec_table[msgUniID]:
            self.__rec_table[msgUniID].append(recMsgUniID)
        MsgBus.__lock.release()

    def getReceivers(self, msgUniID):
        """get receivers that needs notify"""
        if msgUniID not in self.__rec_table:
            return {}
        return self.__rec_table[msgUniID]

    def unregReceiver(self, msgUniID, recMsgUniID):
        """unregister receiver from related msg unique ID"""
        if msgUniID not in self.__rec_table:
            return E_INVILD_PARAM
        if recMsgUniID not in self.__rec_table[msgUniID]:
            return E_INVILD_PARAM
        MsgBus.__lock.acquire()
        self.__rec_table[msgUniID].remove(recMsgUniID)
        MsgBus.__lock.release()
        return E_OK

    #FIXME: improve below as UActor
    def send(self, target, msg):
        """send message to related msg Queue"""
        q = self.findQ(target)
        if q:
            q.put(msg)

    def wait(self, me, target, timeout=None):
        """wait for response"""
        q = self.findQ(me)
        m = None
        if q:
            m = q.get(True, timeout)
            if m.mUid != target:
                m = None
        return m

    def reply(self, msg):
        """reply message to related msg Queue"""
        q = self.findQ(msg.mUid)
        if q:
            q.put(msg)
