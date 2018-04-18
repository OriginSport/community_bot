#coding=utf-8

from .base import cache_rclient

SOLO_RESULT_RED_POINT = "SRRP:%s"


def write_solo_result_redpoint(user_id, solo_id, limit=None):
    key = SOLO_RESULT_RED_POINT % user_id
    cache_rclient.lpush(key, solo_id)
    if limit:
        cache_rclient.ltrim(key, 0, limit - 1)


def get_solo_result_redpoint(user_id, limit, start=0):
    key = SOLO_RESULT_RED_POINT % user_id
    l = cache_rclient.lrange(key, 0, limit)
    return [x.decode() for x in l]


def del_solo_result_redpoint(user_id, solo_id):
    key = SOLO_RESULT_RED_POINT % user_id
    cache_rclient.lrem(key, solo_id, 0)
    return get_solo_result_redpoint(user_id, 10)
