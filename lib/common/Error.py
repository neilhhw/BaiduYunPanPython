#!/usr/bin/env python
#-*- coding: utf-8 -*-

#Operation Result
E_OK            =  0
E_PERM          = -1
E_UPLOAD_FAIL   = -2
E_API_ERR       = -3
E_OPEN_FAIL     = -4
E_INVILD_PARAM  = -5
E_VALUE_ERR     = -6
E_ACTOR_ALIVE   = -7
E_ACTOR_DEAD    = -8
E_WATCH_ERR     = -9
E_PROXY_ERR     = -10

ERR_STR_TABLE = {
    E_OK: 'OK',
    E_PERM: 'Permission denied',
    E_UPLOAD_FAIL: 'Upload failure',
    E_API_ERR: 'API error',
    E_OPEN_FAIL: 'Open failure',
    E_INVILD_PARAM: 'Invalid parameter',
    E_ACTOR_ALIVE: 'Actor is alive',
    E_VALUE_ERR: 'Value error',
    E_ACTOR_DEAD: 'Actor is dead',
    E_WATCH_ERR: 'Filesystem watch error',
    E_PROXY_ERR: 'Proxy error'
}
