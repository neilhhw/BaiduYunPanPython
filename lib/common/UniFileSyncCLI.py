#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import socket
import json

from UniFileSync.lib.common.Error import *

'''
json format for communication
{
    "cmd": "start",
    "param":
    {
        "name": "Controller",
        ""
    }
    "res": E_OK
}


'''

def main():
    """main CLI for UniFileSync"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print sys.argv[2]

    sock.connect(('localhost', 8089))
    req = {'cmd': sys.argv[1], 'res': E_OK, 'param': json.loads(sys.argv[2])}
    d = json.dumps(req)
    sock.send(d)
    buf = sock.recv(1024)
    print json.loads(buf)

if __name__ == '__main__':
    main()
