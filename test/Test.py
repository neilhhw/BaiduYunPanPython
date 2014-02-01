#!/usr/bin/env python
#-*- coding: utf-8 -*-
#import UniFileSync.lib.common.TestPlugin as TestPlugin
class B(object):
    """docstring for B"""
    def __init__(self):
        self.__test = 0

    @property
    def test(self):
        """docstring for test"""
        return self.__test


class A(B):
    """docstring for A"""
    def __init__(self):
        super(A, self).__init__()
        pass



if __name__ == '__main__':
    a = A()
    a.test = 2
    print a.test
