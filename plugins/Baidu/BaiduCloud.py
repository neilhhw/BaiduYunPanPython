#!/usr/bin/env python

import urllib
import urllib2
import json
import time
import Queue
import ConfigParser
import webbrowser


from poster.encode import multipart_encode
from poster.streaminghttp import register_openers

from threading import Thread

#from lib.common.MsgManager import *

#TODO: Add try, catch method
#TODO: Add common test json print out
#TODO: Extract some functions

access_token = ''
post_url = "https://c.pcs.baidu.com/rest/2.0/pcs/file"

upload_param = {'method': 'upload', 'ondup': 'newcopy', 'access_token': access_token}

def upload_file_to_cloud(from_path, to_path = None):
    """docstring for upload_file_to_cloud"""
    register_openers()
    if to_path == None:
        to_path = from_path
    upload_param['path'] = app_path + to_path
    full_url = post_url + '?'  + urllib.urlencode(upload_param)
    fp = open(from_path, "rb")
    datagen, headers = multipart_encode({'file': fp})
    req = urllib2.Request(full_url, datagen, headers)
    ret = urllib2.urlopen(req)
    print_cloud_result(ret)
    ret.close()
    fp.close()

def print_cloud_result(ret):
    if(ret == None):
        print "Load json error"
        return;
    ret_data = json.load(ret)
    for i in ret_data:
        if i == 'list':
            list_data = ret_data[i]
            for k in list_data:
                for j in k:
                    print j, k[j]
        else:
            print i, ret_data[i]

download_url = "https://d.pcs.baidu.com/rest/2.0/pcs/file"
download_param = {'method': 'download', 'access_token': access_token}

def download_file_from_cloud(from_path, to_path):
    """Download from_path in cloud to to_path"""
    out_fp = open(to_path, "wb")
    download_param['path'] = app_path + from_path
    in_fp = cloud_get(download_url, download_param)
    out_fp.write(in_fp.read())
    in_fp.close()
    out_fp.close()

dir_url = "https://pcs.baidu.com/rest/2.0/pcs/file"
dir_param = {'method': 'mkdir', 'access_token': access_token}

def mkdir_in_cloud(dir_name):
    """Make directory in Baidu YunPan"""
    dir_param['path'] = app_path + dir_name
    ret = cloud_post(dir_url, dir_param)
    print_cloud_result(ret)
    ret.close();


info_url = "https://pcs.baidu.com/rest/2.0/pcs/file"
info_param = {'method': 'meta', 'access_token': access_token}

def get_file_info_seperately(file_path):
    """Get file or dir meta information"""
    info_param['path'] = app_path + file_path
    ret = cloud_get(info_url, info_param)
    print_cloud_result(ret)
    ret.close();

def get_file_info_batch(file_path):
    """Get file or dir meta information batch"""
    info_param['path'] = app_path + file_path
    ret = cloud_post(info_url, info_param)
    print_cloud_result(ret)
    ret.close();


list_url = "https://pcs.baidu.com/rest/2.0/pcs/file"
list_param = {'method': 'list', 'access_token': access_token}

def list_file_in_cloud(dir_name, by = "", order = ""):
    """List file in dir_name in cloud"""
    list_param['path'] = app_path + dir_name
    #list_param['by'] = by
    #list_param['order'] = order
    ret = cloud_get(list_url, list_param)
    print_cloud_result(ret)
    ret.close();

#===================================================================================================
def cloud_get(url, data):
    """docstring for cloud_get"""
    url_data = urllib.urlencode(data)
    full_url = url + '?' + url_data
    print full_url
    #Enable Cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(full_url)
    return response

def cloud_post(url, param):
    """Common cloud post method"""
    full_url = url + '?' + urllib.urlencode(param)
    req = urllib2.Request(full_url)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = urllib2.urlopen(req)
    return response

class BaiduCloudAPI():
    """Baidu Cloud API class"""
    def __init__(self, confName):
        self.confName = confName
        self.cf = ConfigParser.ConfigParser()
        self.cf.read(self.confName)
        register_openers()

    def applyBaiduAccess(self):
        """apply baidu access to netdisk"""
        print "[API KEY]: %s=>%s" % ("api_key", self.cf.get("BaiduCloud", "api_key"))
        print "[DEV CODE URL]: %s=>%s" % ("openapi_url", self.cf.get("BaiduCloud", "openapi_url"))
        api_url = self.cf.get("BaiduCloud", "openapi_url") + "/device/code"
        param = {"client_id": self.cf.get("BaiduCloud", "api_key"), "response_type": "device_code", "scope": "basic netdisk"}
        ret_fp = cloud_get(api_url, param)
        data = json.load(ret_fp)
        webbrowser.open(data["verification_url"])
        print "Please enter your user code %s into open web page" % data["user_code"]
        print "Please note it will expires in %d s" % data["expires_in"]
        ret_fp.close();

        #Save devce code to ini
        '''
        data = {}
        data["device_code"] = "41bea915b5dc81e2370d5b061e6a659c"
        '''
        self.cf.set("BaiduCloud", "dev_code", data["device_code"])
        self.saveConf()

    def applyAccessToken(self):
        """Get access Token from Baidu API"""
        api_url = self.cf.get("BaiduCloud", "openapi_url") + "/token"
        print "API URL " + api_url
        param = {"grant_type": "device_token", "code": self.cf.get("BaiduCloud", "dev_code"),
                 "client_id": self.cf.get("BaiduCloud", "api_key"),
                 "client_secret": self.cf.get("BaiduCloud", "secret_key")}
        ret_fp = cloud_get(api_url, param)
        data = json.load(ret_fp)
        print data
        ret_fp.close()

        self.cf.set("BaiduCloud", "access_token", data["access_token"])
        self.cf.set("BaiduCloud", "refresh_token", data["refresh_token"])
        self.cf.set("BaiduCloud", "session_key", data["session_key"])
        self.cf.set("BaiduCloud", "session_secret", data["session_secret"])
        self.cf.set("BaiduCloud", "scope", data["scope"])

        self.saveConf()


    def saveConf(self):
        """save conf to yaml file"""
        self.cf.write(open(self.confName, "w"))

    def getAccessToken(self):
        """Get Baidu API access token"""
        return self.cf.get("BaiduCloud", "access_token")

    def getCloudInfo(self):
        url = self.cf.get("BaiduCloud", "pcs_url") + "/quota"
        param = {"method": "info", "access_token": self.cf.get("BaiduCloud", "access_token")}
        f = cloud_get(url, param)
        data = json.load(f)
        f.close()
        return data

    def uploadSingleFile(self, from_path, to_path=None):
        """upload single file to Baidu Yun Pan"""
        param = {'method': 'upload', 'ondup': 'newcopy', 'access_token': self.cf.get("BaiduCloud", "access_token")}
        if to_path == None:
            to_path = from_path
        param['path'] = self.cf.get("BaiduCloud", "app_path") + "/" + to_path
        url = self.cf.get("BaiduCloud", "upload_url") + '?'  + urllib.urlencode(param)
        fp = open(from_path)
        datagen, headers = multipart_encode({'file': fp})
        #print datagen, headers
        headers['User-Agent'] = 'Mozilla/4.0 (compatible; MSIE 5.5; Windows NT)'
        req = urllib2.Request(url, datagen, headers)
        req.unverifiable = True
        ret_fp = urllib2.urlopen(req)
        data = json.load(ret_fp)
        ret_fp.close()
        fp.close()
        return data

    def downloadSingleFile(self, from_path, to_path):
        """download single file from Baidu Cloud"""
        pass

    def deleteSingleFile(self, path):
        """delete singel file or folder"""
        param = {'method': 'delete', 'access_token': self.cf.get("BaiduCloud", "access_token")}
        param['path'] = self.cf.get('BaiduCloud', 'app_path') + '/' + path
        url = self.cf.get('BaiduCloud', 'pcs_url') + '/file'
        f = cloud_post(url, param)
        data = json.load(f)
        f.close()
        return data

#===================================================================================================

class BaiduCloudActor(Thread):
    """This is a thread for Baidu Yun Pan"""
    def __init__(self, name=None):
        super(BaiduCloudActor, self).__init__()
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
                print "[BaiduCloudActor]: Item empty" + str(e)


    def regQ(self):
        """regsiter message queue to manager"""
        msgManager.regQ(MSG_UNIQUE_ID_T_BAIDU_ACTOR, self.msgQueue)

    def replyMsg(self, msg, result):
        """reply message with result"""
        rMsgQueue = msgManager.findQ(msg.mUid)
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
    #get_cloud_info()
    #upload_file_to_cloud("test.txt")
    #download_file_from_cloud("git1.jpg", "1.jpg")
    #mkdir_in_cloud('test')
    #get_file_info_seperately("git1.jpg");
    #get_file_info_batch("test")
    #list_file_in_cloud("")
    #b = BaiduCloudAPI("conf.ini")
    #b.applyBaiduAccess()
    #b.applyAccessToken()
    import os
    path = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    os.sys.path.insert(0, path)
    from lib.common.MsgManager import *
    b = BaiduCloudActor()
    b.handleFile(CloudMessage(MSG_TYPE_T_FILE, MSG_ID_T_FILE_DELETE, MSG_UNIQUE_ID_T_BAIDU_ACTOR, {'path': 'conf.ini'}))
