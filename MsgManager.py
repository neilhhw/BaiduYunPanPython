#!/usr/bin/env python

#File Operation
MSG_ID_T_FILE_CREATE = 1
MSG_ID_T_FILE_DELETE = 2
MSG_ID_T_FILE_ADD    = 3
MSG_ID_T_FILE_RENAME = 4
MSG_ID_T_FILE_MKDIR  = 5
MSG_ID_T_FILE_MODIFY = 6

#Internal Operation
MSG_ID_T_OPER_STOP = 7

#Operation Result
E_OK            =  0
E_FAIL          = -1
E_UPLOAD_FAIL   = -2
E_API_ERR       = -3

#Message type
MSG_TYPE_T_FILE = 1
MSG_TYPE_T_OPER = 2
MSG_TYPE_T_RES  = 3
MSG_TYPE_T_CONF = 4

class CloudMessage():
    """message type for cloud"""
    def __init__(self, mType = None, mID = None, mTid, mBody = {}):
        self.mType = mType
        self.mID = mID
        self.mBody = mBody
        self.mTid = mTid


class MsgManager():
    """Message controller"""
    def __init__(self, msgTable={}):
        self.msgTable = msgTable

    def regQ(self, msgUniID, msgQueue):
        """register msg Queue"""
        self.msgTable[msgUniID] = msgQueue

    def findQ(self, msgUniID):
        """find msg queue"""
        return self.msgTable[msgUniID]

msgManager = MsgManager.MsgManager()
