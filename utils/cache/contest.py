# coding=utf-8

import datetime

from .base import rank_rclient
from .base import cache_rclient


class ContestRank(object):
    _RANK_KEY = 'CTTR:%s'
    _client = rank_rclient

    @classmethod
    def _make_key(cls, contest_id):
        return str(cls._RANK_KEY % (contest_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._RANK_KEY % "*")

    @classmethod
    def set_rank(cls, contest_id, participant_rank_list, timeout=None):
        key = cls._make_key(contest_id)
        cls._client.delete(key)
        for index, t in enumerate(participant_rank_list):
            cls._client.zadd(key, t, index)

    @classmethod
    def get_rank(cls, contest_id, limit=-1):
        key = cls._make_key(contest_id)
        rank = cls._client.zrange(key, 0, limit, withscores=False)
        rank.reverse()
        return rank

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)


class CurrentContest(object):
    _CURRENT_CONTEST_KEY = 'CCONTEST'
    _client = cache_rclient

    @classmethod
    def _make_key(cls):
        return str(cls._CURRENT_CONTEST_KEY)

    @classmethod
    def set_id(cls, contest_id):
        return cls._client.set(cls._make_key(), contest_id)

    @classmethod
    def get_id(cls):
        return cls._client.get(cls._make_key())


class ContestSalaryDate(object):
    KEY_PREFIX = 'ContestSalaryDate'
    _client = rank_rclient

    @classmethod
    def _make_key(cls):
        return '%s:by_contest_date' % cls.KEY_PREFIX

    @classmethod
    def check_date(cls, date) -> bool:
        if not date:
            return False
        try:
            datetime.datetime.strptime(date, '%Y-%m-%d')
            return True
        except Exception as ex:
            return False

    @classmethod
    def set(cls, contest_date, salary_date) -> int:
        key = cls._make_key()
        if not cls.check_date(contest_date) and cls.check_date(salary_date):
            raise ValueError('date is invalid')
        return cls._client.hset(key, contest_date, salary_date)

    @classmethod
    def get(cls, contest_date) -> str:
        key = cls._make_key()
        value = cls._client.hget(key, contest_date)
        if not value:
            return ''
        value = value.decode()
        if not cls.check_date(value):
            return ''
        return value

    @classmethod
    def get_all(cls) -> dict:
        key = cls._make_key()
        values = cls._client.hgetall(key)
        return values


class ContestCurrentSalaryDate(object):
    _SALARY_DATE_KEY = 'CCSDate'
    _client = rank_rclient

    @classmethod
    def _make_key(cls):
        return str(cls._SALARY_DATE_KEY)

    @classmethod
    def set_current_date(cls, date):
        key = cls._make_key()
        if isinstance(date, datetime.datetime):
            date = date.strftime("%Y-%m-%d")
        cls._client.set(key, date)

    @classmethod
    def get_current_date(cls):
        key = cls._make_key()
        return cls._client.get(key)


class ContestDraft(object):
    _client = cache_rclient
    KEY_PREFIX = 'CONTEST_DRAFT:'
    key = None

    def __init__(self, slug):
        self.key = self.KEY_PREFIX + slug

    def store(self, user_id, value):
        return self._client.hset(self.key, user_id, value)

    def load(self, user_id) -> str:
        value = self._client.hget(self.key, user_id)
        if not value:
            return ''
        value = value.decode()
        return value

    def remove(self, user_id):
        return self._client.hdel(self.key, user_id)


class ContestCanJoin(object):
    _ContestCanJoinKey = 'ContestCanJoin'
    _client = cache_rclient

    @classmethod
    def _make_key(cls):
        return str(cls._ContestCanJoinKey)

    @classmethod
    def get_contest(cls, slug: str) -> int:
        """
        :return: contest_id
        """
        key = cls._make_key()
        contest_id = cls._client.hget(key, slug)
        return int(contest_id) if contest_id else None

    @classmethod
    def update_contest(cls, slug: str, contest_id: int):
        key = cls._make_key()
        cls._client.hset(key, slug, contest_id)

    @classmethod
    def remove_contest(cls, slug: str):
        key = cls._make_key()
        cls._client.hdel(key, slug)

    @classmethod
    def get_all_contests(cls):
        key = cls._make_key()
        values = cls._client.hgetall(key)
        if not values:
            return {}
        return {k.decode(): v.decode() for k, v in values.items() if k and v}


CONTEST_RESULT_RED_POINT = "CRRP:%s"


def write_contest_result_redpoint(user_id, contest_id, limit=None):
    key = CONTEST_RESULT_RED_POINT % user_id
    cache_rclient.lpush(key, contest_id)
    if limit:
        cache_rclient.ltrim(key, 0, limit - 1)


def get_contest_result_redpoint(user_id, limit, start=0):
    key = CONTEST_RESULT_RED_POINT % user_id
    l = cache_rclient.lrange(key, 0, limit)
    return [x.decode() for x in l]


def del_contest_result_redpoint(user_id, contest_id):
    key = CONTEST_RESULT_RED_POINT % user_id
    cache_rclient.lrem(key, contest_id, 0)
    return get_contest_result_redpoint(user_id, 10)
