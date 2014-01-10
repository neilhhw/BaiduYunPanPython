#!/usr/bin/env python
#-*- coding: utf-8 -*-

import urllib
import urllib2
import Queue

from poster.encode import multipart_encode
from poster.streaminghttp import StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler

from threading import Thread

from UniFileSync.lib.common.MsgBus import *
from UniFileSync.lib.common.Error import *

proxyHandler = urllib2.ProxyHandler({'http': 'http://10.144.1.10:8080', 'https': 'https://10.144.1.10:8080'})

#==========Common Web operation
def register_openers():
    """register some openers into urlib2"""
    #Enable media post, proxy, cookie
    handlers = [StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler, proxyHandler, urllib2.HTTPCookieProcessor]
    urllib2.install_opener(urllib2.build_opener(*handlers))

def cloud_get(url, data):
    """common cloud get method"""
    full_url = url + '?' + urllib.urlencode(data)
    response = urllib2.urlopen(full_url)
    return response

def cloud_post(url, param):
    """Common cloud post method"""
    full_url = url + '?' + urllib.urlencode(param)
    req = urllib2.Request(full_url)
    response = urllib2.urlopen(req)
    return response

class SyncCloudActor(Thread):
    """This is a thread for Baidu Yun Pan"""
    def __init__(self, name=None):
        super(SyncCloudActor, self).__init__()
        if name != None:
            self.setName(name)
        self.msgQueue = Queue.Queue()

        self.operTable = {
                MSG_TYPE_T_FILE: lambda msg : self.handleFile(msg),
                MSG_TYPE_T_OPER: lambda msg : self.handleOper(msg),
                MSG_TYPE_T_RES : lambda msg : self.handleRes(msg),
                MSG_TYPE_T_CONF: lambda msg : self.handleConf(msg)
                }

        self.bAPI = BaiduCloudAPI("conf.ini")
        self.accessToken = self.bAPI.getAccessToken()

    def run(self):
        """Thread main function"""
        print self.getName()
        while True:
            try:
                msg = self.msgQueue.get(True)
                res = self.operTable[msg.mType](msg)
                if res == -1:
                    break
            except Queue.Empty, e:
                print "[SyncCloudActor]: Item empty" + str(e)


    def regQ(self):
        """regsiter message queue to manager"""
        msgBus.regQ(MSG_UNIQUE_ID_T_BAIDU_ACTOR, self.msgQueue)

    def replyMsg(self, msg, result):
        """reply message with result"""
        rMsgQueue = msgBus.findQ(msg.mUid)
        rMsgQueue.put(CloudMessage(msg.mType, msg.mID, MSG_UNIQUE_ID_T_BAIDU_ACTOR, {0: result}))

    def handleFile(self, msg):
        """handle file operation"""
        if msg.mID == MSG_ID_T_FILE_CREATE:
            print "[%s]: Create file: %s" % (self.getName(), msg.mBody["path"])
            try:
                print self.bAPI.uploadSingleFile(msg.mBody["path"])
            except urllib2.HTTPError, e:
                print e
            finally:
                pass
        elif msg.mID == MSG_ID_T_FILE_DELETE:
            print "[%s]: Delete file: %s" % (self.getName(), msg.mBody["path"])
            try:
                print self.bAPI.deleteSingleFile(msg.mBody["path"])
            except urllib2.HTTPError, e:
                print e
            finally:
                pass

        return 0

    def handleOper(self, msg):
        """handle file operation"""
        if msg.mID == MSG_ID_T_OPER_STOP:
            self.replyMsg(msg, E_OK)
            print "[%s] Stop" % self.getName()
            return -1

        return 0

    def handleRes(self, msg):
        """handle file operation"""
        return 0

    def handleConf(self, msg):
        """handle file operation"""
        return 0


if __name__ == '__main__':
    import UniFileSync.lib.common.LogManager
    import logging
    logging.debug('Test 2')

