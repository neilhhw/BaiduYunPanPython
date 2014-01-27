#!/usr/bin/env python
#-*- coding: utf-8 -*-
import ConfigParser
import json
import webbrowser
import os
import io
import time

from UniFileSync.lib.common.Plugin import Plugin, ClouldAPI
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.Net import (
        cloud_get,
        cloud_multi_post,
        cloud_post
        )

class BaiduPlugin(Plugin):
    """Baidu Cloud Plugin"""
    def __init__(self, name):
        super(BaiduPlugin, self).__init__(name)
        self.cf = ConfigParser.ConfigParser()
        self.confName = name + '.ini'
        dirName = os.path.dirname(__file__)
        self.cf.read(dirName+'/'+self.confName)
        self.api = BaiduCloudAPI('BaiduCloudAPI')

    def load(self):
        """Baidu Plugin load"""
        super(BaiduPlugin, self).load()
        self.installAPI(self.api)
        self.api.installConf(self.cf)

    def unload(self):
        """Baidu Plugin unload"""
        super(BaiduPlugin, self).unload()
        self.uninstallAPI()
        self.cf.write(open(self.confName, 'w'))


class BaiduCloudAPI(ClouldAPI):
    """Baidu Cloud API"""
    def __init__(self, name):
        super(BaiduCloudAPI, self).__init__(name)
        self.cf = None

    def installConf(self, conf):
        """install configuration parser"""
        self.cf = conf

    def applyAccess(self):
        """apply baidu access to netdisk"""
        super(BaiduCloudAPI, self).applyAccess()
        api_url = self.cf.get("BaiduCloud", "openapi_url") + "/device/code"
        param = {"client_id": self.cf.get("BaiduCloud", "api_key"), "response_type": "device_code", "scope": "basic netdisk"}
        logging.debug('[BaiduPlugin]: applyAccess: URL=> %s, API key=> %s', api_url, self.cf.get("BaiduCloud", "api_key"))
        ret_fp = cloud_get(api_url, param)
        data = json.load(ret_fp)
        webbrowser.open(data["verification_url"])
        print "Please enter your user code %s into open web page" % data["user_code"]
        print "Please note it will expires in %d s" % data["expires_in"]
        ret_fp.close();

        self.cf.set("BaiduCloud", "dev_code", data["device_code"])

    def getToken(self):
        """Get access Token from Baidu API"""
        super(BaiduCloudAPI, self).getToken()
        api_url = self.cf.get("BaiduCloud", "openapi_url") + "/token"
        logging.debug('[BaiduPlugin]: getToken: URL=>% s', api_url)
        param = {"grant_type": "device_token", "code": self.cf.get("BaiduCloud", "dev_code"),
                 "client_id": self.cf.get("BaiduCloud", "api_key"),
                 "client_secret": self.cf.get("BaiduCloud", "secret_key")}
        ret_fp = cloud_get(api_url, param)
        data = json.load(ret_fp)
        logging.debug('[BaiduPlugin]: getToken: access_token=>%s, refresh_token=>%s', data["access_token"], data["refresh_token"])
        ret_fp.close()

        self.cf.set("BaiduCloud", "access_token", data["access_token"])
        self.cf.set("BaiduCloud", "refresh_token", data["refresh_token"])
        self.cf.set("BaiduCloud", "session_key", data["session_key"])
        self.cf.set("BaiduCloud", "session_secret", data["session_secret"])
        self.cf.set("BaiduCloud", "scope", data["scope"])

    def getCloudInfo(self):
        url = self.cf.get("BaiduCloud", "pcs_url") + "/quota"
        param = {"method": "info", "access_token": self.cf.get("BaiduCloud", "access_token")}
        f = cloud_get(url, param)
        data = json.load(f)
        f.close()
        return data

    def uploadSingleFile(self, filePath, syncPath, isReplace=False):
        """upload single file to Baidu Yun Pan"""
        super(BaiduCloudAPI, self).uploadSingleFile(filePath, syncPath, isReplace)
        onDup = 'newcopy'
        if isReplace:
            onDup = 'overwrite'
        param = {'method': 'upload', 'ondup': onDup, 'access_token': self.cf.get("BaiduCloud", "access_token")}
        param['path'] = self.cf.get("BaiduCloud", "app_path") + "/" + syncPath
        fp = open(filePath)
        ret_fp = cloud_multi_post(self.cf.get("BaiduCloud", "upload_url"), param, {'file': fp})
        data = json.load(ret_fp)
        ret_fp.close()
        fp.close()
        return data

    def downloadSingleFile(self, filePath, syncPath=None):
        """download single file from Baidu Cloud"""
        super(BaiduCloudAPI, self).downloadSingleFile(filePath, syncPath)

    def deleteSingleFile(self, filePath, syncPath=None):
        """delete singel file or folder"""
        super(BaiduCloudAPI, self).deleteSingleFile(filePath, syncPath)
        param = {'method': 'delete', 'access_token': self.cf.get("BaiduCloud", "access_token")}
        param['path'] = self.cf.get('BaiduCloud', 'app_path') + '/' + filePath
        url = self.cf.get('BaiduCloud', 'pcs_url') + '/file'
        f = cloud_post(url, param)
        data = json.load(f)
        f.close()
        return data

    def lsInCloud(self, filePath):
        """list dir in cloud"""
        super(BaiduCloudAPI, self).lsInCloud(filePath)
        param = {'method': 'list', 'access_token': self.cf.get("BaiduCloud", "access_token")}
        param['path'] = self.cf.get('BaiduCloud', 'app_path') + '/' + filePath
        url = self.cf.get('BaiduCloud', 'pcs_url') + '/file'
        f = cloud_post(url, param)
        data = json.load(f)
        f.close()
        return self.parseResult(data)

    def mkdirInCloud(self, dirPath):
        """make dir in cloud"""
        super(BaiduCloudAPI, self).mkdirInCloud(dirPath)
        param = {'method': 'mkdir', 'access_token': self.cf.get('BaiduCloud', 'access_token')}
        param['path'] = self.cf.get('BaiduCloud', 'app_path') + '/' + dirPath
        url = self.cf.get('BaiduCloud', 'pcs_url') + '/file'
        f = cloud_post(url, param)
        data = json.load(f)
        f.close()
        return self.parseResult(data)


    def parseResult(self, data):
        """parse result to make it convient to read"""
        res = None
        super(BaiduCloudAPI, self).parseResult(data)
        if 'list' in data:
            """
            Directory of $DIRPATH

            $TIME   <$ISDIR>   $SIZE   $PATH

            """
            strIO = io.StringIO()
            files = data['list']

            strIO.write(u'\nDirectory of %s\n' % (self.cf.get('BaiduCloud', 'app_path')))
            for f in files:
                mtime = time.ctime(f['mtime'])
                path = f['path']
                size = f['size']
                isdir = f['isdir']
                if isdir:
                    strIO.write(u'%s\t%s\t%d\t%s\n' % (mtime, '<DIR>', size, path))
                else:
                    strIO.write(u'%s\t\t%d\t%s\n' % (mtime, size, path))

            res = strIO.getvalue()
            strIO.close()
        else:
            res = data

        return res


baiduPlugin = BaiduPlugin('BaiduPlugin')
baiduPlugin.active()
#print baiduPlugin.getAPI().getCloudInfo()
