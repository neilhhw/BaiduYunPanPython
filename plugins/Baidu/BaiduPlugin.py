#!/usr/bin/env python
#-*- coding: utf-8 -*-
import ConfigParser
import json
import webbrowser
import os
import io
import time
import urllib2

from UniFileSync.lib.common.Plugin import Plugin, ClouldAPI
from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.Net import (
        cloud_get,
        cloud_multi_post,
        cloud_post
        )

from UniFileSync.lib.common.Error import *

class BaiduPlugin(Plugin):
    """Baidu Cloud Plugin"""
    def __init__(self, name):
        super(BaiduPlugin, self).__init__(name)
        self.cf = ConfigParser.ConfigParser()
        self.confName = name + '.ini'
        self.dirName = os.path.dirname(__file__)
        self.api = BaiduCloudAPI('BaiduCloudAPI')

    def load(self):
        """Baidu Plugin load"""
        super(BaiduPlugin, self).load()
        self.installAPI(self.api)
        self.cf.read(self.dirName+os.sep+self.confName)
        self.api.installConf(self.cf)

    def unload(self):
        """Baidu Plugin unload"""
        super(BaiduPlugin, self).unload()
        self.uninstallAPI()
        self.cf.write(open(self.dirName+os.sep+self.confName, 'w'))


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

    def refreshToken(self):
        """Refresh access token"""
        super(BaiduCloudAPI, self).refreshToken()
        api_url = self.cf.get("BaiduCloud", "openapi_url") + "/token"
        logging.debug('[BaiduPlugin]: refreshToken: URL=>% s', api_url)
        param = {"grant_type": "refresh_token", "refresh_token": self.cf.get("BaiduCloud", "refresh_token"),
                 "client_id": self.cf.get("BaiduCloud", "api_key"),
                 "client_secret": self.cf.get("BaiduCloud", "secret_key")}
        try:
            ret_fp = cloud_post(api_url, param)
            data = json.load(ret_fp)

            logging.debug('[BaiduPlugin]: getToken: access_token=>%s, refresh_token=>%s', data["access_token"], data["refresh_token"])

            self.cf.set("BaiduCloud", "access_token", data["access_token"])
            self.cf.set("BaiduCloud", "refresh_token", data["refresh_token"])
            self.cf.set("BaiduCloud", "session_key", data["session_key"])
            self.cf.set("BaiduCloud", "session_secret", data["session_secret"])
            self.cf.set("BaiduCloud", "scope", data["scope"])

            ret_fp.close()
        except ValueError, e:
            logging.error('[%s]: refreshToken JSON load error %s', e)
        except urllib2.HTTPError, e:
            emsg = e.read()
            logging.error('[%s]: HTTP error=>%d, result=>%s', self.getName(), e.code, emsg)
            edata = json.loads(emsg)
            error = {'http': e.code, 'code': edata['error'], 'description': edata['error_description']}
            self.errorHandler(error)

    def getCloudInfo(self):
        url = self.cf.get("BaiduCloud", "pcs_url") + "/quota"
        param = {"method": "info", "access_token": self.cf.get("BaiduCloud", "access_token")}

        res = E_API_ERR
        data = "getCloudInfo failure"

        try:
            print url
            f = cloud_get(url, param)
            data = json.load(f)
            res = E_OK
            f.close()
        except ValueError, e:
            logging.error('[%s]: getCloudInfo JSON load error %s', e)
            res = E_VALUE_ERR
        except urllib2.HTTPError, e:
            self.pcsErrorHandler(e)
            res = E_API_ERR
        return res, self.parseResult(data)

    def uploadSingleFile(self, filePath, syncPath, isReplace=False):
        """upload single file to Baidu Yun Pan"""
        super(BaiduCloudAPI, self).uploadSingleFile(filePath, syncPath, isReplace)
        onDup = 'newcopy'
        if isReplace:
            onDup = 'overwrite'
        param = {'method': 'upload', 'ondup': onDup, 'access_token': self.cf.get("BaiduCloud", "access_token")}
        param['path'] = self.cf.get("BaiduCloud", "app_path") + "/" + syncPath

        res = E_API_ERR

        try:
            fp = open(filePath)
            ret_fp = cloud_multi_post(self.cf.get("BaiduCloud", "upload_url"), param, {'file': fp})
            res = json.load(ret_fp)
            ret_fp.close()
            fp.close()
        except urllib2.HTTPError, e:
            self.pcsErrorHandler(e)
            res = E_API_ERR
        except ValueError, e:
            logging.error('[%s]: uploadSingleFile JSON load error %s', e)
            res = E_VALUE_ERR

        return self.parseResult(res)

    def downloadSingleFile(self, filePath, syncPath=None):
        """download single file from Baidu Cloud"""
        super(BaiduCloudAPI, self).downloadSingleFile(filePath, syncPath)

    def deleteSingleFile(self, filePath, syncPath=None):
        """delete singel file or folder"""
        super(BaiduCloudAPI, self).deleteSingleFile(filePath, syncPath)
        param = {'method': 'delete', 'access_token': self.cf.get("BaiduCloud", "access_token")}
        param['path'] = self.cf.get('BaiduCloud', 'app_path') + '/' + filePath
        url = self.cf.get('BaiduCloud', 'pcs_url') + '/file'

        res = E_API_ERR
        try:
            f = cloud_post(url, param)
            res = json.load(f)
            f.close()
        except urllib2.HTTPError, e:
            self.pcsErrorHandler(e)
            res = E_API_ERR
        except ValueError, e:
            logging.error('[%s]: uploadSingleFile JSON load error %s', e)
            res = E_VALUE_ERR

        return self.parseResult(res)

    def lsInCloud(self, filePath):
        """list dir in cloud"""
        super(BaiduCloudAPI, self).lsInCloud(filePath)
        param = {'method': 'list', 'access_token': self.cf.get("BaiduCloud", "access_token")}
        param['path'] = self.cf.get('BaiduCloud', 'app_path') + '/' + filePath
        url = self.cf.get('BaiduCloud', 'pcs_url') + '/file'

        data = {}
        res = E_API_ERR

        try:
            f = cloud_post(url, param)
            data = json.load(f)
            #logging.debug('[%s]: data %s', self.getName(), data)
            f.close()
            res = E_OK
        except urllib2.HTTPError, e:
            self.pcsErrorHandler(e)
            res = E_API_ERR
        except ValueError, e:
            logging.error('[%s]: lsInCloud JSON load error %s', e)
            res = E_VALUE_ERR

        return res, self.parseResult(data)

    def mkdirInCloud(self, dirPath):
        """make dir in cloud"""
        super(BaiduCloudAPI, self).mkdirInCloud(dirPath)
        param = {'method': 'mkdir', 'access_token': self.cf.get('BaiduCloud', 'access_token')}
        param['path'] = self.cf.get('BaiduCloud', 'app_path') + '/' + dirPath
        url = self.cf.get('BaiduCloud', 'pcs_url') + '/file'

        res = E_API_ERR
        try:
            f = cloud_post(url, param)
            res = json.load(f)
            f.close()
        except urllib2.HTTPError, e:
            self.pcsErrorHandler(e)
            res = E_API_ERR
        except ValueError, e:
            logging.error('[%s]: lsInCloud JSON load error %s', e)
            res = E_VALUE_ERR

        return self.parseResult(res)

    def mvInCloud(self, toPath, fromPath):
        """move in cloud"""
        super(BaiduCloudAPI, self).mvInCloud(toPath, fromPath)

    def parseResult(self, data):
        """parse result to make it convient to read"""
        super(BaiduCloudAPI, self).parseResult(data)

        res = E_API_ERR

        try:
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
                logging.debug('[%s]: File list result\n%s', self.getName(), res)

            elif 'quota' in data:
                """
                    Quota: %dGB
                    Used: %dKB
                """
                quota = data['quota'] / (1024*1024*1024)
                used = data['used'] / (1024*1024)

                res = "Quota: %sGB, Used: %sKB" % (quota, used)

            elif 'fs_id' in data:
                #file operation is OK
                res = E_OK

            elif 'request_id' in data:
                res = E_OK

        except TypeError, e:
            pass

        return res

    def errorHandler(self, error):
        """docstring for errorHandler"""
        super(BaiduCloudAPI, self).errorHandler(error)
        if error['http'] == 401:
            if error['code'] == 111:
                #This is access token expires
                self.refreshToken()
            elif error['code'] == 110:
                #This is access token invaid
                pass
        elif error['http'] == 400:
            if error['code'] == 'invalid_grant':
                #Get or refresh token error
                pass
            elif error['code'] == 'expired_token':
                #Token expired
                pass

    def pcsErrorHandler(self, e):
        """pcs error handler"""
        emsg = e.read()
        logging.error('[%s]: HTTP error=>%d, result=>%s', self.getName(), e.code, emsg)
        edata = json.loads(emsg)
        error = {'http': e.code, 'code': edata['error_code']}
        self.errorHandler(error)

baiduPlugin = BaiduPlugin('BaiduPlugin')
baiduPlugin.active()
#print baiduPlugin.getAPI().getCloudInfo()
