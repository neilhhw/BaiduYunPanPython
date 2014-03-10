#!/usr/bin/env python
#-*- coding:utf-8 -*-
import socket
import json
import platform
import Queue

from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.UActor import UActor
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.UCloudActor import UCloudActor
from UniFileSync.lib.common.Net import set_proxy, register_openers
from UniFileSync.lib.common.PluginManager import PluginManager
from UniFileSync.lib.common.ConfManager import ConfManager

if platform.system() == 'Windows':
    from UniFileSync.lib.platform.windows.UFSMonitor import WinFileSysMonitor as FileSysMonitor
elif platform.system() == 'Linux':
    from UniFileSync.lib.platform.linux.UFSMonitor import LinuxFileSysMonitor as FileSysMonitor
else:
    pass

class UServer(UActor):
    """UniFileSync server"""
    def __init__(self, name=None):
        super(UServer, self).__init__(name)
        self.setMsgUid(MSG_UNIQUE_ID_T_CONTROLLER)

        #self.addListener(MSG_UNIQUE_ID_T_CLOUD_ACTOR)

        self.addHandler('start', self.startHandler)
        self.addHandler('stop', self.stopHandler)
        self.addHandler('proxy', self.proxyHandler)
        self.addHandler('watch', self.watchHandler)
        self.addHandler('list', self.listHandler)
        self.addHandler('sync', self.syncHandler)
        self.addHandler('info', self.infoHandler)

        self.__startActors = []
        self.__callbackList = []

        self.cActor = UCloudActor('Cloud Actor')
        self.fsMonitor = FileSysMonitor('File Sys Monitor')

        self.isEnableSocket = False

        self.configure()


    def addCallBack(self, callback):
        """add call back function for UServer"""
        self.__callbackList.append(callback)

    def enableSocket(self):
        """enable socket as net server"""
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.isEnableSocket = True

    def startHandler(self, param):
        """start handler for actors"""
        logging.debug('[%s]: startHandler with parm %s', self.getName(), param);

        if param['name']:
            name = param['name'].lower()
        else:
            name = ''
        res = E_OK


        if name == 'all' or name == '':
            if self.cActor.isRunning or self.fsMonitor.isRunning:
                return E_ACTOR_ALIVE, None
            self.cActor.start()
            self.__startActors.append(self.cActor)
            self.fsMonitor.start()
            self.__startActors.append(self.fsMonitor)
        elif name == 'monitor':
            if self.fsMonitor.isRunning:
                return E_ACTOR_ALIVE, None
            self.fsMonitor.start()
            self.__startActors.append(self.fsMonitor)
        elif name == 'cloud':
            if self.cActor.isRunning:
                return E_ACTOR_ALIVE, None
            self.cActor.start()
            self.__startActors.append(self.cActor)
        else:
            logging.error('[%s]: startHandler with name %s error', self.getName(), param['name'])
            res = E_INVILD_PARAM

        return res, None

    def stopHandler(self, param):
        """stop handler for actors"""
        logging.debug('[%s]: stopHandler with parm %s', self.getName(), param);

        if param['name']:
            name = param['name'].lower()
        else:
            name = ''

        res = E_ACTOR_DEAD

        if name == 'all' or name == '':
            #The msg is broadcase
            msg = self.initMsg(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, None, True)
            self.notifyListeners(msg)

            for a in self.__startActors:
                rmsg = self.getMsg(2)
                if rmsg:
                    res = rmsg.body['result']

            logging.info('[UniFileSync]: stop server...')
            self.stop()
        elif name == 'monitor':
            if not self.fsMonitor.isRunning:
                res = E_ACTOR_DEAD
            msg = self.initMsg(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_FS_MONITOR, True)
            self.msgBus.send(msg)
            rmsg = self.getMsg(2)
            if rmsg:
                res = rmsg.body['result']
        elif name == 'cloud':
            if not self.cActor.isRunning:
                res = E_ACTOR_DEAD
            msg = self.initMsg(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_CLOUD_ACTOR, True)
            self.msgBus.send(msg)
            rmsg = self.getMsg(2)
            if rmsg:
                res = rmsg.body['result']
        else:
            logging.error('[%s]: stopHandler with name %s error', self.getName(), param['name'])
            res = E_INVILD_PARAM

        return res, None

    def proxyHandler(self, param):
        """proxy handler for actors"""
        logging.debug('[%s]: proxyHandler with parm %s', self.getName(), param);
        res = E_PROXY_ERR
        res = set_proxy(param)
        return res, None

    def watchHandler(self, param):
        """watch handler for actors"""
        logging.debug('[%s]: watchHandler with parm %s', self.getName(), param);
        msg = self.initMsg(MSG_TYPE_T_OPER, MSG_ID_T_OPER_ADD_WATCH, MSG_UNIQUE_ID_T_FS_MONITOR, True)
        msg.body = param
        self.msgBus.send(msg)
        rmsg = self.getMsg(2)
        res = E_WATCH_ERR
        if rmsg:
            res = rmsg.body['result']
        return res, None

    def listHandler(self, param):
        """list handler for actors"""
        logging.debug('[%s]: listHandler with parm %s', self.getName(), param);
        msg = self.initMsg(MSG_TYPE_T_FILE, MSG_ID_T_FILE_LIST, MSG_UNIQUE_ID_T_CLOUD_ACTOR, True)
        msg.body = param
        self.msgBus.send(msg)
        res = E_API_ERR
        data = None
        rmsg = self.getMsg(None)

        if rmsg:
            res = rmsg.body['result']
            data = rmsg.body['data']

        return res, data

    def syncHandler(self, param):
        """sync handler for actors"""
        logging.debug('[%s]: syncHandler with parm %s', self.getName(), param);
        msg = self.initMsg(MSG_TYPE_T_FILE, MSG_ID_T_FILE_SYNC, MSG_UNIQUE_ID_T_CLOUD_ACTOR, True)
        msg.body['path'] = param['path']
        self.msgBus.send(msg)
        rmsg = self.getMsg(2)
        res = E_API_ERR
        if rmsg:
            res = rmsg.body['result']

        return res, None

    def infoHandler(self, param):
        """get information of cloud"""
        logging.debug('[%s]: infoHandler with parm %s', self.getName(), param);
        msg = self.initMsg(MSG_TYPE_T_FILE, MSG_ID_T_FILE_INFO, MSG_UNIQUE_ID_T_CLOUD_ACTOR, True)
        msg.body = param
        self.msgBus.send(msg)
        rmsg = self.getMsg(None)
        res = E_API_ERR
        data = "Cloud API Error"
        if rmsg:
            if 'result' in rmsg.body:
                res = rmsg.body['result']
            if 'data' in rmsg.body:
                data = rmsg.body['data']
        return res, data


    def run(self):
        """UServer entry"""
        super(UServer, self).run()
        #TODO: below should be set by ConfManager

        if self.isEnableSocket:
            self.sock.bind(('localhost', 8089))
            self.sock.listen(5)

            while self.isRunning:
                try:
                    conn, addr = self.sock.accept()
                    try:
                        conn.settimeout(5)
                        buf = conn.recv(1024) #TODO: should be also in ConfManager
                        req = json.loads(buf)
                        logging.debug('[UniFileSync]: action %s, param %s', req['action'], req['param'])
                        #TODO: make it common for function usage
                        res, data = self.getHandler(req['action'])(req['param'])
                        ret = {'action': req['action'], 'param': {'data': data}, 'res': res, 'type': 'ack'}
                        conn.send(json.dumps(ret))
                    except socket.timeout:
                        logging.info('[UniFileSync]: socket time out from %s', addr)
                    except KeyError, e:
                        logging.error('[%s]: Key Error with param %s', self.getName(), req['param'])
                    finally:
                        conn.close()
                except KeyboardInterrupt:
                    print 'Press Ctrl+C'
                    self.stop()
        else:
            self.msgLoop()


    def msgLoop(self):
        """message loop for server"""
        res = E_OK
        data = None
        while self.isRunning:
            try:
                msg = self.msgQueue.get(True)
                if msg and msg.header.mtype:
                    res, data = self.getHandler(msg.header.mtype)(msg.body)
                    if msg.header.ack:
                        for c in self.__callbackList:
                            c({'result': res, 'data': data})

            except Queue.Empty, e:
                logging.error('[%s]: msgLoop timeout with empty item', self.getName())
            finally:
                pass



    def stop(self):
        """Userver stop"""
        super(UServer, self).stop()
        PluginManager.getManager().unloadAllPlugins()
        if self.isEnableSocket:
            self.sock.close()

    def configure(self):
        """server self configure when it is started"""
        register_openers()
        PluginManager.getManager().loadAllPlugins()
        confManager = ConfManager.getManager()
        proxy = confManager.getValue('common', 'network')

        if proxy['proxy'] != "" and proxy['proxy'] != None:
            param = {'http': 'http://%s' % proxy['proxy'], 'https': 'https://%s' % proxy['proxy'] }
            set_proxy(param)
            logging.debug('[%s]: set proxy server %s', self.getName(), proxy['proxy'])

if __name__ == '__main__':
    us = UServer()
    us.setName('UniFileSync Server')
    us.enableSocket()
    us.run()

