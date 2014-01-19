#!/usr/bin/env python
#-*- coding: utf-8 -*-
import ConfigParser
import json
import webbrowser

from UniFileSync.lib.common.Plugin import Plugin, ClouldAPI
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.Net import *

class BaiduPlugin(Plugin):
    """Baidu Cloud Plugin"""
    def __init__(self, name):
        super(BaiduPlugin, self).__init__(name)
        self.cf = ConfigParser.ConfigParser()
        self.confName = name + '.ini'
        self.cf.read(self.confName)

    def load(self):
        """Baidu Plugin load"""
        super(BaiduCloudAPI, self).load()
        self.installAPI(BaiduCloudAPI('BaiduCloudAPI'))
        self.installConf(self.cf)
        register_openers()

    def unload(self):
        """Baidu Plugin unload"""
        super(BaiduCloudAPI, self).unload()
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

    def uploadSingleFile(self, filePath, syncPath=None):
        """upload single file to Baidu Yun Pan"""
        param = {'method': 'upload', 'ondup': 'newcopy', 'access_token': self.cf.get("BaiduCloud", "access_token")}
        if syncPath == None:
            syncPath = filePath
        param['path'] = self.cf.get("BaiduCloud", "app_path") + "/" + syncPath
        fp = open(filePath)
        ret_fp = cloud_multi_post(self.cf.get("BaiduCloud", "upload_url"), param, {'file': fp})
        data = json.load(ret_fp)
        ret_fp.close()
        fp.close()
        return data

    def downloadSingleFile(self, filePath, syncPath):
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


baiduPlugin = BaiduPlugin('BaiduPlugin')
baiduPlugin.active()
