#!/usr/bin/env python
#-*- coding:utf-8 -*-

import Queue
import threading

from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.MsgBus import *


class UActor(threading.Thread):
    """common actor class for UniFileSync"""
    def __init__(self, actorName=None):
        super(UActor, self).__init__()
        self.__actorName = actorName
        self.__msgQueue = Queue.Queue()
        self.__isRunning = False
        self.__msgUid = -1
        self.__operTable = {}
        self.__msgBus = UMsgBus.getBus()
        self.__lList = []

        if actorName:
            self.setName(actorName)

    @property
    def isRunning(self):
        """checking is actor is running"""
        return self.__isRunning

    @property
    def msgUid(self):
        """return msg unique ID"""
        return self.__msgUid

    @property
    def msgQueue(self):
        """return msg queue"""
        return self.__msgQueue

    @property
    def msgBus(self):
        """return current message bus instance"""
        return self.__msgBus

    def run(self):
        """actor entry"""
        logging.debug('[%s]: is running', self.getName())
        self.__msgBus.regQ(self.__msgUid, self.__msgQueue)
        self.__isRunning = True

    def stop(self):
        """actor stop"""
        logging.debug('[%s]: is stopping', self.getName())
        for l in self.__lList:
            self.__msgBus.rmListener(l, self.msgUid)
        self.__msgBus.unregQ(self.__msgUid)
        self.__isRunning = False

    def addHandler(self, action, handler):
        """add handler for related action in operation table"""
        self.__operTable[action] = handler

    def getHandler(self, action):
        """get handler for action"""
        return self.__operTable[action]

    def addListener(self, mUid):
        """add listner for target uid"""
        self.__lList.append(mUid)
        self.__msgBus.addListener(mUid, self.msgUid)

    def msgLoop(self):
        """message loop for processing message"""
        while self.__isRunning:
            try:
                msg = self.__msgQueue.get(True)
                if msg and msg.header.mtype:
                    self.__operTable[msg.header.mtype](msg)
            except Queue.Empty, e:
                logging.error('[%s]: msgLoop timeout in %d with empty item', self.getName(), timeout)
            finally:
                pass

    def getMsg(self, timeout=0):
        """process message within timeout"""
        msg = None
        try:
            msg = self.__msgQueue.get(True, timeout)
        except Queue.Empty:
            logging.error('[%s]: getMsg timeout in %d with empty item', self.getName(), timeout)
        finally:
            pass

        return msg

    def processMsg(self, timeout=0):
        """docstring for processMsg"""
        try:
            msg = self.__msgQueue.get(True, timeout)
            if msg and msg.header.mtype:
                self.__operTable[msg.header.mtype](msg)
        except Queue.Empty:
            #logging.debug('[%s]: processMsg timeout in %d with empty item', self.getName(), timeout)
            pass
        finally:
            pass

    def getName(self):
        """get actor name"""
        return self.__actorName

    def setName(self, name):
        """set actor name"""
        self.__actorName = name
        super(UActor, self).setName(name)

    def initMsg(self, mtype, mid, rUid=None, ack=False):
        """init message for common usage"""
        return UMsg(mtype, mid, rUid, self.__msgUid, ack, {})

    def setMsgUid(self, msgUid):
        """set current msg uid"""
        self.__msgUid = msgUid
        self.__msgBus.regUniID(msgUid)

    def replyResult(self, msg, result):
        """common reply result method"""
        rUid = msg.header.sUid
        rmsg = self.initMsg(msg.header.mtype, msg.header.mid, rUid)
        rmsg.body = {'result': result}

        logging.debug('[%s]: replyResult to Uid %d with result %s', self.getName(), rUid, result)
        self.__msgBus.send(rmsg)

    def notifyListeners(self, msg):
        """notify listeners for what occurs"""
        logging.debug('[%s]: notifyListeners', self.getName())
        if not msg.header.rUid:
            self.__msgBus.broadcast(msg)
        else:
            self.__msgBus.send(msg)

