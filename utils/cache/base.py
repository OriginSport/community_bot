#coding=utf-8

import memcache
from redis import Redis

from django.conf import settings

mcache_client = memcache.Client(settings.MEMCACHED_CACHE_SERVERS)


class MemCache(object):

    def __init__(self, client):
        self.client = client

    def get(self, key):
        return self.client.get(str(key))

    def set(self, key, value, timeout):
        self.client.set(str(key), value, timeout)

    def get_multi(self, keys):
        return self.client.get_multi([str(k) for k in keys])

    def delete(self, key):
        self.client.delete(str(key))

    def incr(self, key, increment):
        self.client.incr(key, increment)


mcache = MemCache(mcache_client)
counter_rclient = Redis(
    host=settings.COUNTER_REDIS_SERVER,
    port=settings.COUNTER_REDIS_PORT,
    password=settings.COUNTER_REDIS_PAS,
    db=0)
player_rclient = Redis(
    host=settings.COUNTER_REDIS_SERVER,
    port=settings.COUNTER_REDIS_PORT,
    password=settings.COUNTER_REDIS_PAS,
    db=0)
task_rclient = Redis(
    host=settings.COUNTER_REDIS_SERVER,
    port=settings.COUNTER_REDIS_PORT,
    password=settings.COUNTER_REDIS_PAS,
    db=0)
rank_rclient = Redis(
    host=settings.COUNTER_REDIS_SERVER,
    port=settings.COUNTER_REDIS_PORT,
    password=settings.COUNTER_REDIS_PAS,
    db=0)
mmr_rclient = Redis(
    host=settings.COUNTER_REDIS_SERVER,
    port=settings.COUNTER_REDIS_PORT,
    password=settings.COUNTER_REDIS_PAS,
    db=0)
cache_rclient = Redis(
    host=settings.COUNTER_REDIS_SERVER,
    port=settings.COUNTER_REDIS_PORT,
    password=settings.COUNTER_REDIS_PAS,
    db=0)
publish_rclient = Redis(
    host=settings.COUNTER_REDIS_SERVER,
    port=settings.COUNTER_REDIS_PORT,
    password=settings.COUNTER_REDIS_PAS,
    db=0)

livebetting_rclient = Redis(
    host=settings.COUNTER_REDIS_SERVER,
    port=settings.COUNTER_REDIS_PORT,
    password=settings.COUNTER_REDIS_PAS,
    db=0)
