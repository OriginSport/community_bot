#coding=utf-8

from .base import mcache


class SpamCache(object):
    _SPAM_KEY = 'SPAM:%s'
    _client = mcache

    @classmethod
    def _make_key(cls, _type, user_id):
        return str(cls._SPAM_KEY % ('%s:%s' % (_type, user_id)))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._SPAM_KEY % "*")

    @classmethod
    def set_spam_cache(cls, _type, user_id, timeout=None):
        key = cls._make_key(_type, user_id)
        cls._client.set(key, "*", timeout)

    @classmethod
    def check_spam_cache(cls, _type, user_id):
        key = cls._make_key(_type, user_id)
        return cls._client.get(key)

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)
