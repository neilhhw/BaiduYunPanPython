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
MSG_ID_T_FILE_INFO   = 8

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
MSG_UNIQUE_ID_T_SYNC_ACTOR      = 1 #TODO: remove it later
MSG_UNIQUE_ID_T_CLOUD_ACTOR      = 1
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
    need    ack
Body:
    {
        'XXX': 'XXX'
    }

"""

class UMsgHeader():
    """message header"""
    def __init__(self, mtype, mid, rUid, sUid, ack):
        self.mtype = mtype
        self.mid = mid
        self.rUid = rUid
        self.sUid = sUid
        self.ack = ack

class UMsg():
    """message for UniFileSync usage"""
    def __init__(self, mtype = -1, mid = -1, rUid = -1, sUid = -1, ack = False, body = {}):
        self.header = UMsgHeader(mtype, mid, rUid, sUid, ack)
        self.body = body

class UMsgBus(object):
    """Message bus"""
    def __init__():
        """Forbid __init__(self)"""
        pass

    __instance = None
    __lock     = threading.Lock()
    __queue_table = {}
    __uni_ID_list = []
    __lis_table = {}

    @staticmethod
    def getBus():
        """Get Message Bus singlone instance"""
        UMsgBus.__lock.acquire()
        if not UMsgBus.__instance:
            UMsgBus.__instance = super(UMsgBus, UMsgBus).__new__(UMsgBus)
            super(UMsgBus, UMsgBus).__init__(UMsgBus.__instance)
        UMsgBus.__lock.release()
        return UMsgBus.__instance

    def regQ(self, msgUniID, msgQueue):
        """register msg Queue"""
        if  msgUniID not in self.__uni_ID_list:
            logging.error('regQ failure due to no Unique Message ID registered')
            return E_INVILD_PARAM
        UMsgBus.__lock.acquire()
        self.__queue_table[msgUniID] = msgQueue
        UMsgBus.__lock.release()
        return E_OK

    def findQ(self, msgUniID):
        """find msg queue"""
        if msgUniID in self.__queue_table:
            return self.__queue_table[msgUniID]
        return None

    def regUniID(self, msgUniID):
        """register new msg uni ID"""
        if msgUniID not in self.__uni_ID_list:
            UMsgBus.__lock.acquire()
            self.__uni_ID_list.append(msgUniID)
            UMsgBus.__lock.release()
            return E_OK
        logging.error('regUniID failure due to Unique Message ID %d already registered', msgUniID)
        return E_INVILD_PARAM

    def unregQ(self, msgUniID):
        """unregister msg queue"""
        UMsgBus.__lock.acquire()
        self.__queue_table[msgUniID] = None
        self.__uni_ID_list.remove(msgUniID)
        UMsgBus.__lock.release()

    def addListener(self, msgUniID, lMsgUniID):
        """register listener to related msg unique ID"""
        UMsgBus.__lock.acquire()
        if msgUniID not in self.__lis_table:
            self.__lis_table[msgUniID] = []
        if lMsgUniID not in self.__lis_table[msgUniID]:
            self.__lis_table[msgUniID].append(lMsgUniID)
        UMsgBus.__lock.release()

    def rmListener(self, msgUniID, lMsgUniID):
        """unregister listener from related msg unique ID"""
        if msgUniID not in self.__lis_table:
            return E_INVILD_PARAM
        if lMsgUniID not in self.__lis_table[msgUniID]:
            return E_INVILD_PARAM
        UMsgBus.__lock.acquire()
        self.__lis_table[msgUniID].remove(lMsgUniID)
        UMsgBus.__lock.release()
        return E_OK

    def getListeners(self, msgUniID):
        """get receivers that needs notify"""
        if msgUniID not in self.__lis_table:
            return []
        return self.__lis_table[msgUniID]

    def broadcast(self, msg):
        """broadcast message to all listeners"""
        sUid = msg.header.sUid
        for l in self.getListeners(sUid):
            q = self.findQ(l)
            if q:
                q.put(msg)
            else:
                logging.error('[UMsgBus]: broadcast: find sUid %d listener %d queue failure', msg.header.sUid, l)

    def send(self, msg):
        """send message to related msg Queue"""
        q = self.findQ(msg.header.rUid)
        if q:
            q.put(msg)
        else:
            logging.error('[UMsgBus]: send: find rUid %d queue failure', msg.header.rUid)



#==================================================================================
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
    __queue_table = {}
    __uni_ID_list = [MSG_UNIQUE_ID_T_CONTROLLER, MSG_UNIQUE_ID_T_SYNC_ACTOR, MSG_UNIQUE_ID_T_FS_MONITOR]
    __lis_table = {MSG_UNIQUE_ID_T_CONTROLLER: [MSG_UNIQUE_ID_T_SYNC_ACTOR, MSG_UNIQUE_ID_T_FS_MONITOR]}

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
        self.__queue_table[msgUniID] = msgQueue
        MsgBus.__lock.release()
        return E_OK

    def findQ(self, msgUniID):
        """find msg queue"""
        return self.__queue_table[msgUniID]

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
        self.__queue_table[msgUniID] = None
        self.__uni_ID_list.remove(msgUniID)
        MsgBus.__lock.release()

    def regReceiver(self, msgUniID, recMsgUniID):
        """register receiver to related msg unique ID"""
        MsgBus.__lock.acquire()
        if msgUniID not in self.__lis_table:
            self.__lis_table[msgUniID] = []
        if recMsgUniID not in self.__lis_table[msgUniID]:
            self.__lis_table[msgUniID].append(recMsgUniID)
        MsgBus.__lock.release()

    def getReceivers(self, msgUniID):
        """get receivers that needs notify"""
        if msgUniID not in self.__lis_table:
            return []
        return self.__lis_table[msgUniID]

    def unregReceiver(self, msgUniID, recMsgUniID):
        """unregister receiver from related msg unique ID"""
        if msgUniID not in self.__lis_table:
            return E_INVILD_PARAM
        if recMsgUniID not in self.__lis_table[msgUniID]:
            return E_INVILD_PARAM
        MsgBus.__lock.acquire()
        self.__lis_table[msgUniID].remove(recMsgUniID)
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

