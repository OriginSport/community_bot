#coding=utf-8

from ..base import task_rclient


class LoginTimesVerify(object):
    _LOGIN_TIMES_VERIFY_KEY = 'LTV:%s'
    _client = task_rclient

    @classmethod
    def _make_key(cls, user_id):
        return str(cls._LOGIN_TIMES_VERIFY_KEY % (user_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._LOGIN_TIMES_VERIFY_KEY % "*")

    @classmethod
    def set_user_login_times(cls, user_id, count):
        key = cls._make_key(user_id)
        cls._client.set(key, count)

    @classmethod
    def get_user_login_times(cls, user_id):
        key = cls._make_key(user_id)
        count = cls._client.get(key)
        if count:
            return int(count)
        return 0

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)


class LastLoginDateCache(object):
    _LAST_LOGIN_DATE_KEY = 'LLD:%s'
    _client = task_rclient

    @classmethod
    def _make_key(cls, user_id):
        return str(cls._LAST_LOGIN_DATE_KEY % (user_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._LAST_LOGIN_DATE_KEY % "*")

    @classmethod
    def set_user_last_login_time(cls, user_id, t):
        key = cls._make_key(user_id)
        cls._client.set(key, t)

    @classmethod
    def get_user_last_login_time(cls, user_id):
        key = cls._make_key(user_id)
        return cls._client.get(key)

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)
