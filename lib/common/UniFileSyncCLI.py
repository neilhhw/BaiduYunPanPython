#!/usr/bin/env python
#-*- coding:utf-8 -*-
import sys
import socket


def main():
    """main CLI for UniFileSync"""
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.connect(('localhost', 8089))

    sock.send('%s: %s' % (sys.argv[1], sys.argv[2]))
    print sock.recv(1024)

if __name__ == '__main__':
    main()
