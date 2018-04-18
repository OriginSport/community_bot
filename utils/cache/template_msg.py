#coding=utf-8

from base import mcache


class DailyContestSendCache(object):
    _DAIYLY_CONTEST_SEND_KEY = 'DCSK:%s'
    _client = mcache

    @classmethod
    def _make_key(cls, user_id):
        return str(cls._DAIYLY_CONTEST_SEND_KEY % (user_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._DAIYLY_CONTEST_SEND_KEY % "*")

    @classmethod
    def set_daily_contest_send_cache(cls, user_id, t, timeout=None):
        key = cls._make_key(user_id)
        cls._client.set(key, t, timeout)

    @classmethod
    def check_daily_contest_send_cache(cls, user_id):
        key = cls._make_key(user_id)
        return cls._client.get(key)

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)
