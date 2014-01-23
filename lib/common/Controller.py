#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import os
import Queue
import threading
import platform
import json

from UniFileSync.lib.common.Error import *
from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.SyncActor import SyncActor
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.PluginManager import PluginManager
from UniFileSync.lib.common.Net import (
        register_openers,
        set_proxy
        )

if platform.system() == 'Windows':
    from UniFileSync.lib.platform.windows.FSMonitor import WinFileSysMonitor as FileSysMonitor
elif platform.system() == 'Linux':
    from UniFileSync.lib.platform.linux.FSMonitor import LinuxFileSysMonitor as FileSysMonitor
else:
    pass


class Controller(threading.Thread):
    """UniFileSync Controller"""
    def __init__():
        """forbidden for constructor"""
        logging.error('[Controller]: __init__ is forbidden')

    __instance = None
    __lock     = threading.Lock()

    @staticmethod
    def getController():
        """get controller for Controller thread"""
        Controller.__lock.acquire()
        if not Controller.__instance:
            Controller.__instance = super(Controller, Controller).__new__(Controller)
            super(Controller, Controller).__init__(Controller.__instance)
            Controller.__instance.myInit()
        Controller.__lock.release()
        return Controller.__instance

    def myInit(self):
        self.msgQueue = Queue.Queue()
        self.__threadStop = False

        self.operTable = {
                         MSG_TYPE_T_FILE: lambda msg : self.handleFile(msg),
                         MSG_TYPE_T_OPER: lambda msg : self.handleOper(msg),
                         MSG_TYPE_T_RES : lambda msg : self.handleRes(msg),
                         MSG_TYPE_T_CONF: lambda msg : self.handleConf(msg)
                         }

    def regToMsgBus(self):
        """register queue to message bus"""
        MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_CONTROLLER, self.msgQueue)
        MsgBus.getBus().regReceiver(MSG_UNIQUE_ID_T_FS_MONITOR, MSG_UNIQUE_ID_T_CONTROLLER)
        MsgBus.getBus().regReceiver(MSG_UNIQUE_ID_T_SYNC_ACTOR, MSG_UNIQUE_ID_T_CONTROLLER)

    def unregFromMsgBus(self):
        """unregister queue to message bus"""
        MsgBus.getBus().unregQ(MSG_UNIQUE_ID_T_CONTROLLER)
        MsgBus.getBus().unregReceiver(MSG_UNIQUE_ID_T_FS_MONITOR, MSG_UNIQUE_ID_T_CONTROLLER)
        MsgBus.getBus().unregReceiver(MSG_UNIQUE_ID_T_SYNC_ACTOR, MSG_UNIQUE_ID_T_CONTROLLER)

    def run(self):
        """thread entry"""
        logging.info('[%s]: is starting', self.getName())
        self.regToMsgBus()

        #proxies = {'http': 'http://10.144.1.10:8080', 'https': 'https://10.144.1.10:8080'}
        #proxy ={'https': 'https://10.144.1.10:8080'}
        #set_proxy(proxy)
        register_openers()
        PluginManager.getManager().loadAllPlugins()

        self.sActor = SyncActor("SyncActor")
        self.sActor.start()

        self.fMonitor = FileSysMonitor("FSMonitor")
        self.fMonitor.addWatch(os.getcwd()+os.sep+'test')
        self.fMonitor.start()

        while not self.__threadStop:
            try:
                msg = self.msgQueue.get(True, 2)
                # Block until get one message
                if msg != None:
                    #logging.debug('[%s]: receives message ID: %d, Type: %d', self.getName(), msg.mID, msg.mType)
                    self.operTable[msg.mType](msg)
            except Queue.Empty:
                pass

    def stop(self):
        """stop Controller thread"""
        logging.info('[%s] is stopping', self.getName())
        self.unregFromMsgBus()
        self.__threadStop = True

    def handleFile(self, msg):
        """handle file operation"""
        pass

    def handleOper(self, msg):
        """handle file operation"""
        sMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_SYNC_ACTOR)
        fMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_FS_MONITOR)
        #mMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_CONTROLLER)

        if msg.mID == MSG_ID_T_OPER_STOP:
            logging.debug('[%s]: do stop', self.getName())
            if self.sActor.isAlive():
                sMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_CONTROLLER, {}))
                ack_msg = self.msgQueue.get(True)
                if ack_msg.mUid == MSG_UNIQUE_ID_T_SYNC_ACTOR and ack_msg.mID == MSG_ID_T_OPER_STOP:
                    if ack_msg.mBody['result'] == E_OK:
                        logging.debug('[%s]: stop sync actor OK', self.getName())
                    else:
                        logging.debug('[%s]: stop sync actor NOK=>%d', self.getName(), ack_msg.mBody['result'])
            if self.fMonitor.isAlive():
                fMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_CONTROLLER, {}))
                ack_msg = self.msgQueue.get(True)
                if ack_msg.mUid == MSG_UNIQUE_ID_T_FS_MONITOR and ack_msg.mID == MSG_ID_T_OPER_STOP:
                    if ack_msg.mBody['result'] == E_OK:
                        logging.debug('[%s]: stop file system monitor OK', self.getName())
                    else:
                        logging.debug('[%s]: stop file system monitor NOK=>%d', self.getName(), ack_msg.mBody['result'])

            self.replyMsg(msg, E_OK)
            self.stop()
        elif msg.mID == MSG_ID_T_OPER_ADD_WATCH:
            self.fMonitor.addWatch(msg.mBody['path'], msg.mBody['mask'])

    def replyMsg(self, msg, result):
        """reply message with result"""
        rMsgQueue = MsgBus.getBus().findQ(msg.mUid)
        rMsgQueue.put(CloudMessage(msg.mType, msg.mID, MSG_UNIQUE_ID_T_CONTROLLER, {'result': result}))
        #logging.debug('[%s]: replyMsg: ID=>%d, uID=>%d, result=>%d', self.getName(), msg.mID, msg.mUid, result)


    def handleRes(self, msg):
        """handle file operation"""
        pass

    def handleConf(self, msg):
        """handle file operation"""
        pass


def start_controller(param):
    """start controller thread"""
    c = Controller.getController()
    if not c.isAlive():
        c.setName(param['name'])
        #c.setDaemon(False)
        c.start()
        return E_OK

    return E_OK

def stop_controller(param):
    """stop controller thread"""
    if Controller.getController() == None or not Controller.getController().isAlive():
        return E_INVILD_PARAM
    MSG_UNIQUE_ID_T_TEST = 5
    MsgBus.getBus().regUniID(MSG_UNIQUE_ID_T_TEST)
    msgQueue = Queue.Queue()
    MsgBus.getBus().regQ(MSG_UNIQUE_ID_T_TEST, msgQueue)
    cMsgQueue = MsgBus.getBus().findQ(MSG_UNIQUE_ID_T_CONTROLLER)
    cMsgQueue.put(CloudMessage(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_TEST, {}))
    msg = msgQueue.get(True)
    return E_OK

def proxy_handler(param):
    """proxy handler"""
    set_proxy(param)
    return E_OK


if __name__ == '__main__':
    import socket
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(('localhost', 8089))
    sock.listen(5)

    actionTable = {
            'start': lambda param: start_controller(param),
            'stop':  lambda param: stop_controller(param),
            'proxy': lambda param: proxy_handler(param)
            }

    try:
        logging.info('[UniFileSync]: start server...')
        while True:
            connection, address = sock.accept()
            try:
                connection.settimeout(5)
                buf = connection.recv(1024)
                req = json.loads(buf)
                logging.debug('[UniFileSync]: action %s, param %s', req['cmd'], req['param'])
                if req['cmd'] in actionTable:
                    res = actionTable[req['cmd']](req['param'])
                    d = {'cmd': 'ack', 'param': {}, 'res': res}
                    connection.send(json.dumps(d))
                    if req['cmd'] == 'stop':
                        logging.info('[UniFileSync]: stop server...')
                        break;
            except socket.timeout:
                logging.info('[UniFileSync]: socket time out from %s', address)
                connection.close()
            except KeyboardInterrupt, e:
                raise e
    except KeyboardInterrupt:
        logging.info('[UniFileSync Controller]: Press Ctrl+C')
        stop_controller()
