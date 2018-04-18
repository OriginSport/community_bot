# coding=utf-8

from .base import mcache, counter_rclient
from typing import Union
import json


class MemcacheCounter(object):
    def __init__(self, name):
        self.key = 'MCR:' + name

    def get_count(self):
        value = mcache.get(self.key)
        if value is None:
            return 0
        else:
            return value

    def set_count(self, value):
        mcache.set(self.key, value)

    def delete_count(self):
        mcache.delete(self.key)

    count = property(get_count, set_count, delete_count)

    def increment(self, incr=1):
        value = mcache.get(self.key)
        if value:
            mcache.set(self.key, incr + int(value))
        else:
            mcache.set(self.key, incr)


class RedisCounter(object):
    def __init__(self, name):
        self.key = 'RCR:' + name

    def get_count(self):
        value = counter_rclient.get(self.key)
        if value is None:
            return 0
        else:
            return int(value)

    def set_count(self, value):
        counter_rclient.set(self.key, '%s' % value)

    def delete_count(self):
        counter_rclient.delete(self.key)

    count = property(get_count, set_count, delete_count)

    def increment(self, incr=1):
        return int(counter_rclient.incr(self.key, incr))


user_id_counter = RedisCounter('user_id')

contest_id_counter = RedisCounter('contest_id')


def get_new_contest_id() -> int:
    return contest_id_counter.increment()


class RedisHashCounter(object):
    key = None
    expire = 0
    key_prefix = 'RHCR:'

    def __init__(self, name, expire: int = 0):
        self.key = self.key_prefix + name
        self.expire = expire

    def get_count(self, slug: str) -> int:
        value = counter_rclient.hget(self.key, slug)
        if value is None:
            return 0
        else:
            return int(value)

    def set_expire(self):
        counter_rclient.expire(self.key, self.expire)

    def set_count(self, slug: str, value: int):
        counter_rclient.hset(self.key, slug, '%s' % value)
        if self.expire:
            self.set_expire()

    def delete_count(self, slug: str):
        counter_rclient.hdel(self.key, slug)

    count = property(get_count, set_count, delete_count)

    def increment(self, slug: str, incr: int = 1) -> int:
        value = int(counter_rclient.hincrby(self.key, slug, incr))
        if self.expire:
            self.set_expire()
        return value


class RedisHashStore(RedisHashCounter):
    key_prefix = 'SNAKE:RESULT:DATE:'
    expire = 60 * 60 * 24 * 10

    def set_json(self, slug: str, value: dict):
        if not value:
            return
        try:
            value = json.dumps(value)
        except:
            return
        counter_rclient.hset(self.key, slug, value)
        if self.expire:
            self.set_expire()

    def get_json(self, slug: str) -> dict:
        rt = counter_rclient.hget(self.key, slug)
        if not rt:
            return {}
        rt = rt.decode()
        try:
            data = json.loads(rt)
            return data
        except:
            return {}
