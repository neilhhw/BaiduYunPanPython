#!/usr/bin/env python
#-*- coding:utf-8 -*-

import sys
import socket
import json
import argparse

from UniFileSync.lib.common.Error import *

'''

    UniFileSyncCLI


    action          start, restart, stop, watch, list, sync

    -n --name       thread name
    -p --proxy      specify proxy server
    -d --dir        specify a watch dir
    -l --load       load specify plugin
    -v --version    version of UniFileSyncCLI
    -s --save       save configuration

'''

'''
json format for communication
{
    "type": "request" or "ack",     request = 1, ack = 2
    "action": "start",
    "param":
    {
        "name": "Controller",
        ""
    }
    "res": E_OK
}


'''

class CLIArgument(object):
    """CLI argument class"""
    pass

def handle_params(c):
    """handle params and return a dict as above"""
    params = {}
    params['save'] = c.save

    if c.action == 'start':
        params['name'] = c.name
    elif c.action == 'stop':
        params['name'] = c.name
    elif c.action == 'proxy':
        if c.proxy:
            params['http'] = 'http://%s'%(c.proxy)
            params['https'] = 'https://%s'%(c.proxy)
    elif c.action in ('watch', 'list', 'sync'):
        if c.dir:
            params['path'] = c.dir

    return params

def main():
    """main CLI for UniFileSync"""
    parser = argparse.ArgumentParser(prog='UniFileSyncCLI',
                description='UniFileSync Command Line Interface',
                )
    parser.add_argument('action', nargs='?', help='start, restart, stop, watch, sync, list, proxy')

    parser.add_argument('-n', '--name', nargs='?', help='specify a name')
    parser.add_argument('-p', '--proxy', nargs='?', help='specify proxy server')
    parser.add_argument('-d', '--dir', nargs='?', help='specify a path')
    parser.add_argument('-l', '--load', nargs='?', help='load specify plugin')
    parser.add_argument('-v', '--version', nargs='?', help='version of UniFileSyncCLI')
    parser.add_argument('-s', '--save', nargs='?', help='save UniFileSync configuration')

    c = CLIArgument()
    parser.parse_args(namespace=c)

    if not c.action:
        parser.print_help()
        return

    req = {'type': 'request','action': c.action, 'param': handle_params(c)}

    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8089))

    d = json.dumps(req)

    sock.send(d)

    buf = sock.recv(1024)
    r = json.loads(buf)

    if r['param'] != None and r['param'] != {}:
        if 'data' in r['param']:
            if r['param']['data']:
                print r['param']['data']
        else:
            pass

    if r['action'] == c.action and r['res'] == E_OK:
        print 'Excute successfully'
    elif r['action'] == c.action and type(r['res']) != int:
        for res in r['res']:
            print res
    else:
        print 'Excute error %d' % (r['res'])

if __name__ == '__main__':
    main()
