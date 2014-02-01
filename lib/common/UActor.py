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
        self.__msgBus = MsgBus.getBus()
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

    def addListener(self, mUid):
        """add listner for target uid"""
        self.__lList.append(mUid)
        self.__msgBus.addListener(mUid, self.mUid)

    def msgLoop(self):
        """message loop for processing message"""
        while self.__isRunning:
            try:
                msg = self.__msgQueue.get(True)
                if msg and msg.header.mtype:
                    self.__operTable[msg.header.mtype](msg)
            except Queue.Empty, e:
                raise e
            finally:
                pass

    def procMsg(self, timeout=0):
        """process message within timeout"""
        try:
            msg = self.__msgQueue.get(True, timeout)
        except Queue.Empty:
            logging.error('[%s]: procMsg timeout in %d with empty item', self.getName(), timeout)
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
        self.msgUid = msgUid
        self.__msgBus.regUniID(msgUid)

    def replyResult(self, msg, result):
        """common reply result method"""
        rUid = msg.header.sUid
        sUid = self.__msgUid
        msg.header.sUid = sUid
        msg.header.rUid = rUid
        msg.body = {'result': result}

        logging.debug('[%s]: replyResult to Uid %d with result %s', self.getName(), rUid, result)
        self.__msgBus.send(msg)

    def notifyListeners(self, msg):
        """notify listeners for what occurs"""
        logging.debug('[%s]: notifyListeners', self.getName())
        if not msg.header.rUid:
            self.__msgBus.broadcast(msg)
        else:
            self.__msgBus.send(msg)
