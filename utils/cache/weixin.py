#coding=utf-8

from base import mcache
from ..rest.wxoauth import get_access_token, get_jsapi_ticket


def get_cache_access_token():
    key = 'wx:access_token'
    access_token = mcache.get(key)
    if not access_token:
        info = get_access_token()
        access_token = info['access_token']
        timeout = int(info['expires_in']) - 1000
        if timeout < 0:
            timeout = 100
        mcache.set(key, access_token, timeout)
    return access_token


def get_cache_jsapi_ticket():
    key = 'wx:jsapi_ticket'
    access_token = get_cache_access_token()
    ticket = mcache.get(key)
    if not ticket:
        info = get_jsapi_ticket(access_token)
        ticket = info['ticket']
        timeout = int(info['expires_in']) - 1000
        if timeout < 0:
            timeout = 100
        mcache.set(key, ticket, timeout)
    return ticket
