#!/usr/bin/env python

import os
import urllib
import urllib2
import json
from poster.encode import multipart_encode
from poster.streaminghttp import register_openers


info="https://pcs.baidu.com/rest/2.0/pcs/quota?method=info&access_token=3.b752352253e1bd4c3e77b34079af90ad.2592000.1381061912.2969659025-1297832"

access_token = "3.b752352253e1bd4c3e77b34079af90ad.2592000.1381061912.2969659025-1297832"
app_path = "/apps/YunPan_Python/"

#TODO: Add try, catch method
#TODO: Add common test json print out
#TODO: Extract some functions

def cloud_get(url, data):
    """docstring for cloud_get"""
    url_data = urllib.urlencode(data)
    full_url = url + '?' + url_data
    #print full_url
    #Enable Cookie
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    response = opener.open(full_url)
    return response

def cloud_post(url, param):
    """Common cloud post method"""
    full_url = url + '?' + urllib.urlencode(param)
    req = urllib2.Request(full_url)
    opener = urllib2.build_opener(urllib2.HTTPCookieProcessor())
    try:
        response = urllib2.urlopen(req)
    except urllib2.HTTPError:
        print 'Http Error'
        return None
    return response

quota_url = "https://pcs.baidu.com/rest/2.0/pcs/quota"

quota_data = {}
quota_data['method'] = 'info'
quota_data['access_token'] = access_token

def get_cloud_info():
    f = cloud_get(quota_url, quota_data)
    print_cloud_result(f)
    f.close()

post_url = "https://c.pcs.baidu.com/rest/2.0/pcs/file"

upload_param = {'method': 'upload', 'ondup': 'newcopy', 'access_token': access_token}

def upload_file_to_cloud(file_name):
    """docstring for upload_file_to_cloud"""
    register_openers()
    upload_param['path'] = app_path + file_name
    full_url = post_url + '?'  + urllib.urlencode(upload_param)
    fp = open(file_name, "rb")
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

def download_file_from_cloud(file_name):
    """docstring for download_file_from_cloud"""
    out_fp = open(file_name, "wb")
    download_param['path'] = app_path + file_name
    in_fp = cloud_get(download_url, download_param)
    out_fp.write(in_fp.read())
    in_fp.close()
    out_fp.close()

dir_url = "https://pcs.baidu.com/rest/2.0/pcs/file"
dir_param = {'method': 'mkdir', 'access_token': access_token}

def mkdir_in_cloude(dir_name):
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


if __name__ == '__main__':
    #get_cloud_info()
    #upload_file_to_cloud("test.txt")
    #download_file_from_cloud("test0.txt")
    #mkdir_in_cloude('test')
    get_file_info_seperately("test.txt");
    #get_file_info_batch("test")
    #list_file_in_cloud("")
