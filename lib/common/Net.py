#!/usr/bin/env python
#-*- coding:utf-8 -*-
import urllib
import urllib2

from poster.encode import multipart_encode
from poster.streaminghttp import StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler

proxyHandler = urllib2.ProxyHandler({'http': 'http://10.144.1.10:8080', 'https': 'https://10.144.1.10:8080'})

#==========Common Web operation
__handlers = []

def register_openers():
    """register some openers into urlib2"""
    #Enable media post, proxy, cookie
    __handlers = [StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler, urllib2.HTTPCookieProcessor]
    urllib2.install_opener(urllib2.build_opener(*__handlers))

def add_opener(opener):
    """add self-design opener intall handlers list"""
    __handlers.append(opener)

def cloud_get(url, data):
    """common cloud get method"""
    if __handlers == []:
        register_openers()
    full_url = url + '?' + urllib.urlencode(data)
    response = urllib2.urlopen(full_url)
    return response

def cloud_post(url, param):
    """common cloud post method"""
    if __handlers == []:
        register_openers()
    full_url = url + '?' + urllib.urlencode(param)
    req = urllib2.Request(full_url)
    response = urllib2.urlopen(req)
    return response

def cloud_multi_post(url, param, multi):
    """common cloud multipart post method"""
    if __handlers == []:
        register_openers()
    full_url = url + '?' + urllib.urlencode(param)
    datagen, headers = multipart_encode(multi)
    req = urllib2.Request(full_url, datagen, headers)
    response = urllib2.urlopen(req)
    return response
