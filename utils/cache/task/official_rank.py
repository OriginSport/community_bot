#coding=utf-8

from ..base import task_rclient


class FirstPrizeTimesVerify(object):
    _FIRST_PRIZE_TIMES_VERIFY_KEY = 'FPTV:%s'
    _client = task_rclient

    @classmethod
    def _make_key(cls, user_id):
        return str(cls._FIRST_PRIZE_TIMES_VERIFY_KEY % (user_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._FIRST_PRIZE_TIMES_VERIFY_KEY % "*")

    @classmethod
    def set_user_first_prize_times(cls, user_id, count):
        key = cls._make_key(user_id)
        cls._client.set(key, count)

    @classmethod
    def get_user_first_prize_times(cls, user_id):
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
