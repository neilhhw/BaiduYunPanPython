#!/usr/bin/env python
#-*- coding: utf-8 -*-
import os
import logging

from UniFileSync.lib.common.ConfManager import ConfManager

logging.basicConfig(level=logging.DEBUG,
                format='%(asctime)s %(filename)s[line:%(lineno)d] %(levelname)s %(message)s',
                datefmt='%a, %d %b %Y %H:%M:%S',
                filename= ConfManager.getManager().getUserLogPath() + os.sep + 'UniFileSync.log',
                filemode= 'a')

#################################################################################################
#定义一个StreamHandler，将INFO级别或更高的日志信息打印到标准错误，并将其添加到当前的日志处理对象#
console = logging.StreamHandler()
console.setLevel(logging.DEBUG)
formatter = logging.Formatter('%(asctime)s %(filename)s: %(levelname)-8s %(message)s')
console.setFormatter(formatter)
logging.getLogger('').addHandler(console)
################################################################################################
