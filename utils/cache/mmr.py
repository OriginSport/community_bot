#coding=utf-8

from base import mmr_rclient


class UserLastMMRCache(object):
    _KEY = 'ULMMR:%s'
    _client = mmr_rclient

    @classmethod
    def _make_key(cls, user_id):
        return str(cls._KEY % (user_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._KEY % "*")

    @classmethod
    def set_mmr(cls, user_id, mmr, timeout=None):
        key = cls._make_key(user_id)
        cls._client.set(key, str(mmr))

    @classmethod
    def get_mmr(cls, user_id):
        key = cls._make_key(user_id)
        return cls._client.get(key)

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)
