#!/usr/bin/env python
#-*- coding:utf-8 -*-
import urllib
import urllib2
import threading

from poster.encode import multipart_encode
from poster.streaminghttp import StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler

from UniFileSync.lib.common.LogManager import logging
from UniFileSync.lib.common.Error import *

#proxyHandler = urllib2.ProxyHandler({'http': 'http://10.144.1.10:8080', 'https': 'https://10.144.1.10:8080'})

#==========Common Web operation
__handlers = [StreamingHTTPHandler, StreamingHTTPRedirectHandler, StreamingHTTPSHandler, urllib2.HTTPCookieProcessor]
__lock = threading.Lock()

def register_openers():
    """register some openers into urlib2"""
    #Enable media post, proxy, cookie
    #logging.debug('%s', __handlers)
    res = E_OK
    try:
        urllib2.install_opener(urllib2.build_opener(*__handlers))
    except Exception, e:
        logging.error('[register_openers]: exception occurs %s', e)
        res = E_OPEN_FAIL
    finally:
        return res

def set_proxy(proxies, **kargs):
    """set proxy for global usage"""
    #TODO: Add user name, passsword in the future
    proxyHandler = urllib2.ProxyHandler(proxies)
    __lock.acquire()
    __handlers.append(proxyHandler)
    __lock.release()
    return register_openers()

def cloud_get(url, param):
    """common cloud get method"""
    full_url = url + '?' + urllib.urlencode(param)
    response = urllib2.urlopen(full_url)
    return response

def cloud_post(url, param):
    """common cloud post method"""
    full_url = url + '?' + urllib.urlencode(param)
    req = urllib2.Request(full_url)
    response = urllib2.urlopen(req)
    return response

def cloud_multi_post(url, param, multi):
    """common cloud multipart post method"""
    full_url = url + '?' + urllib.urlencode(param)
    datagen, headers = multipart_encode(multi)
    req = urllib2.Request(full_url, datagen, headers)
    response = urllib2.urlopen(req)
    return response
