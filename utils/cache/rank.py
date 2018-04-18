#coding=utf-8

import datetime

from django.conf import settings

from base import rank_rclient


class RewardWeeklyRank(object):
    _RANK_KEY = 'RWKR:%s'
    _client = rank_rclient

    @classmethod
    def _make_key(cls, date):
        return str(cls._RANK_KEY % (date))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._RANK_KEY % "*")

    @classmethod
    def set_rank(cls, date, rank_list, timeout=None):
        if isinstance(date, datetime.datetime):
            date = date.strftime("%Y%m%d")
        key = cls._make_key(date)
        for t in rank_list:
            cls._client.zadd(key, t[0], t[1])

    @classmethod
    def get_rank(cls, date, limit=-1):
        if isinstance(date, datetime.datetime):
            date = date.strftime("%Y%m%d")
        key = cls._make_key(date)
        rank = cls._client.zrange(key, 0, limit, withscores=True)
        rank.reverse()
        return rank

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)


class RewardTotalRank(RewardWeeklyRank):
    _RANK_KEY = 'RTTR:%s'
    _client = rank_rclient


class WinRateTotalRank(RewardWeeklyRank):
    _RANK_KEY = 'WRTR:%s'
    _client = rank_rclient


def get_has_rank_date(r, t):
    while True:
        if RewardWeeklyRank.get_rank(t, 0):
            break
        t = t - datetime.timedelta(days=1)
    return t


def wrap_rank(today_rank, yesterday_rank):
    yesterday_rank_dic = {}
    for i, y in enumerate(yesterday_rank):
        yesterday_rank_dic[y[0]] = i

    from TeamCrushAPI.user.models import format_users_json
    users_json = format_users_json([r[0] for r in today_rank])

    new_rank = []

    for i, r in enumerate(today_rank):
        user_id = r[0]
        v = r[1]
        yr = yesterday_rank_dic.get(user_id, None)
        if yr == None:
            yr = None
        else:
            yr = yr - i
        new_rank.append({
            'user_id': user_id,
            'user': users_json.get(int(user_id)),
            'v': v,
            'offset': yr,
        })
    return new_rank


def get_reward_weekly_rank_cache(limit=settings.DEFAULT_RANK_LENGTH_LIMIT,
                                 t=None):
    if not t:
        t = datetime.datetime.now()

    t = get_has_rank_date(RewardWeeklyRank, t)
    today_rank = RewardWeeklyRank.get_rank(t)[:limit]

    yt = t - datetime.timedelta(days=1)
    yt = get_has_rank_date(RewardWeeklyRank, yt)
    yesterday_rank = RewardWeeklyRank.get_rank(yt)

    return wrap_rank(today_rank, yesterday_rank)


def get_reward_total_rank_cache(limit=settings.DEFAULT_RANK_LENGTH_LIMIT,
                                t=None):
    if not t:
        t = datetime.datetime.now()

    t = get_has_rank_date(RewardTotalRank, t)
    today_rank = RewardTotalRank.get_rank(t)[:limit]

    yt = t - datetime.timedelta(days=1)
    yt = get_has_rank_date(RewardTotalRank, yt)
    yesterday_rank = RewardTotalRank.get_rank(yt)

    return wrap_rank(today_rank, yesterday_rank)


def get_rate_total_rank_cache(limit=settings.DEFAULT_RANK_LENGTH_LIMIT, t=None):
    if not t:
        t = datetime.datetime.now()

    t = get_has_rank_date(WinRateTotalRank, t)
    today_rank = WinRateTotalRank.get_rank(t)[:limit]

    yt = t - datetime.timedelta(days=1)
    yt = get_has_rank_date(WinRateTotalRank, yt)
    yesterday_rank = WinRateTotalRank.get_rank(yt)

    return wrap_rank(today_rank, yesterday_rank)
