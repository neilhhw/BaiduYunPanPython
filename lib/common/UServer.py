#!/usr/bin/env python
#-*- coding:utf-8 -*-
import socket
import json
import platform

from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.UActor import UActor
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.UCloudActor import UCloudActor
from UniFileSync.lib.common.Net import set_proxy

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

        self.__startActors = []

        self.cActor = UCloudActor('Cloud Actor')
        self.fsMonitor = FileSysMonitor('File Sys Monitor')


    def startHandler(self, param):
        """start handler for actors"""
        logging.debug('[%s]: startHandler with parm %s', self.getName(), param);

        if param['name']:
            name = param['name'].lower()
        else:
            name = ''
        res = E_OK

        if name == 'all' or name == '':
            self.cActor.start()
            self.__startActors.append(self.cActor)
            self.fsMonitor.start()
            self.__startActors.append(self.fsMonitor)
        elif name == 'monitor':
            self.fsMonitor.start()
            self.__startActors.append(self.fsMonitor)
        elif name == 'cloud':
            self.cActor.start()
            self.__startActors.append(self.cActor)
        else:
            logging.error('[%s]: startHandler with name %s error', self.getName(), param['name'])
            res = E_INVILD_PARAM

        return res

    def stopHandler(self, param):
        """stop handler for actors"""
        logging.debug('[%s]: stopHandler with parm %s', self.getName(), param);

        if param['name']:
            name = param['name'].lower()
        else:
            name = ''
        res = E_OK

        if name == 'all' or name == '':
            #The msg is broadcase
            msg = self.initMsg(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, None, True)
            self.notifyListeners(msg)

            for a in self.__startActors:
                rmsg = self.getMsg(2)
                if rmsg and rmsg.body['result'] != E_OK:
                    res = rmsg.body['result']

            logging.info('[UniFileSync]: stop server...')
            self.stop()
        elif name == 'monitor':
            msg = self.initMsg(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_FS_MONITOR, True)
            self.msgBus.send(msg)
            rmsg = self.getMsg(2)
            if rmsg and rmsg.body['result'] != E_OK:
                res = rmsg.body['result']
        elif name == 'cloud':
            msg = self.initMsg(MSG_TYPE_T_OPER, MSG_ID_T_OPER_STOP, MSG_UNIQUE_ID_T_CLOUD_ACTOR, True)
            self.msgBus.send(msg)
            rmsg = self.getMsg(2)
            if rmsg and rmsg.body['result'] != E_OK:
                res = rmsg.body['result']
        elif name == 'server':
            logging.info('[UniFileSync]: stop server...')
            self.stop()
        else:
            logging.error('[%s]: stopHandler with name %s error', self.getName(), param['name'])
            res = E_INVILD_PARAM

        return res

    def proxyHandler(self, param):
        """proxy handler for actors"""
        logging.debug('[%s]: proxyHandler with parm %s', self.getName(), param);
        res = E_OK
        set_proxy(param)
        return res

    def watchHandler(self, param):
        """watch handler for actors"""
        logging.debug('[%s]: watchHandler with parm %s', self.getName(), param);
        msg = self.initMsg(MSG_TYPE_T_OPER, MSG_ID_T_OPER_ADD_WATCH, MSG_UNIQUE_ID_T_FS_MONITOR, True)
        msg.body = param
        self.msgBus.send(msg)
        rmsg = self.getMsg(2)
        if rmsg and rmsg.body['result'] != E_OK:
            res = rmsg.body['result']
        return res

    def listHandler(self, param):
        """list handler for actors"""
        logging.debug('[%s]: listHandler with parm %s', self.getName(), param);
        msg = self.initMsg(MSG_TYPE_T_FILE, MSG_ID_T_FILE_LIST, MSG_UNIQUE_ID_T_CLOUD_ACTOR, True)
        msg.body = param
        self.msgBus.send(msg)
        rmsg = self.getMsg(2)
        res = E_OK
        data = None
        if rmsg and rmsg.body['result'] != E_OK:
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
        res = E_OK
        if rmsg and rmsg.body['result'] != E_OK:
            res = rmsg.body['result']
        return res

    def run(self):
        """UServer entry"""
        super(UServer, self).run()
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        #TODO: below should be set by ConfManager
        sock.bind(('localhost', 8089))
        sock.listen(5)

        while self.isRunning:
            conn, addr = sock.accept()
            try:
                conn.settimeout(5)
                buf = conn.recv(1024) #TODO: should be also in ConfManager
                req = json.loads(buf)
                logging.debug('[UniFileSync]: action %s, param %s', req['action'], req['param'])
                res, data = self.getHandler(req['action'])(req['param'])
                ret = {'action': req['action'], 'param': {'data': data}, 'res': res, 'type': 'ack'}
                conn.send(json.dumps(ret))
            except socket.timeout:
                logging.info('[UniFileSync]: socket time out from %s', addr)
                conn.close()
            finally:
                pass

    def stop(self):
        """Userver stop"""
        super(UServer, self).stop()

if __name__ == '__main__':
    us = UServer()
    us.setName('UniFileSync Server')
    us.run()

