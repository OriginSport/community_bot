#coding=utf-8

import simplejson

from base import rank_rclient


class LeagueRank(object):
    _RANK_KEY = 'LER:%s'
    _FULL_RANK_KEY = 'LFER:%s'
    _client = rank_rclient

    @classmethod
    def _make_key(cls, league_id):
        return str(cls._RANK_KEY % (league_id))

    @classmethod
    def _make_full_key(cls, league_id):
        return str(cls._FULL_RANK_KEY % (league_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._RANK_KEY % "*")

    @classmethod
    def set_full_rank(cls, league_id, participant_rank_list, timeout=None):
        key = cls._make_full_key(league_id)
        cls._client.delete(key)
        cls._client.set(key, simplejson.dumps(participant_rank_list))

    @classmethod
    def get_full_rank(cls, league_id):
        key = cls._make_full_key(league_id)
        data = cls._client.get(key)
        if data:
            return simplejson.loads(data)

    @classmethod
    def set_rank(cls, league_id, participant_rank_list, timeout=None):
        key = cls._make_key(league_id)
        cls._client.delete(key)
        for index, t in enumerate(participant_rank_list):
            cls._client.zadd(key, t[0], index)

    @classmethod
    def get_rank(cls, league_id, limit=-1):
        key = cls._make_key(league_id)
        rank = cls._client.zrange(key, 0, limit, withscores=False)
        rank.reverse()
        return rank

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)
