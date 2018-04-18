#coding=utf-8

from django.conf import settings

from base import mcache


class EventDailyCheckIn(object):
    _USER_DAILY_CHECK_IN_KEY = 'EDCU:%s'
    _client = mcache

    @classmethod
    def _make_key(cls, user_id):
        return str(cls._USER_DAILY_CHECK_IN_KEY % (user_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._USER_DAILY_CHECK_IN_KEY % "*")

    @classmethod
    def set_user_daily_checkin_cache(cls, user_id, t, timeout=None):
        key = cls._make_key(user_id)
        cls._client.set(key, t, timeout)

    @classmethod
    def check_user_daily_checkin_cache(cls, user_id):
        key = cls._make_key(user_id)
        return cls._client.get(key)

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)
