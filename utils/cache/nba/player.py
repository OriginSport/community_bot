# coding=utf-8

from typing import List, Tuple, Dict

from django.conf import settings
import simplejson
import json
from collections import OrderedDict

from ..base import player_rclient


class CacheLiveNBAPlayerStats(object):
    KEY_TPL = 'LIVENBA:STATS:%s:BY_GAME_DATE:%s'
    _client = player_rclient

    @classmethod
    def _make_key(cls, date, stats):
        return cls.KEY_TPL% (stats, date)

    @classmethod
    def get(cls, date, *stats) -> Dict[str, Dict[int,int]]:
        pipe = player_rclient.pipeline()

        for stats_name in stats:
            if stats_name == 'fpts':
                if settings.USE_HUPU_CLOSE_FORMULA:
                    stats_name = 'HUPU_TC_PTS_%s' % stats_name
                else:
                    stats_name = 'OLD_TC_PTS_%s' % stats_name
            pipe.zrange(cls._make_key(date, stats_name), 0, -1, withscores=True)
        value = pipe.execute()
        data = {}
        for idx, name in enumerate(stats):
            data[name] = dict((int(player_id), int(score)) for player_id, score in value[idx])
        return data

class CacheLiveNBAPlayerPtsList(object):
    PLAYER_RANK_BY_GAME_DATE = 'LIVENBA:RANK:%s:BY_DATE:%s'  # zset
    RANK_OLD_TC_PTS_BY_GAME_DATE = 'LIVENBA:RANK:OLD_TC_PTS:BY_DATE:%s'  # zset
    _client = player_rclient

    @classmethod
    def _make_key(cls, date):
        formula_name = 'OLD_TC_PTS'
        if settings.USE_HUPU_CLOSE_FORMULA:
            formula_name = 'HUPU_TC_PTS'
        return cls.PLAYER_RANK_BY_GAME_DATE % (formula_name, date)

    @classmethod
    def get_by_game_date(cls, date: str) -> List[Tuple[int, int]]:
        """
        Returns:
            [(player_id, score), ...]
        """
        key = cls._make_key(date)
        return [(int(player_id), int(score))
                for player_id, score
                in cls._client.zrange(key, 0, -1, withscores=True)]


class CachePlayerBoxscoreList(object):
    _PLAYER_BOXSCORE_LIST_KEY = 'PGL:%s'
    _client = player_rclient

    @classmethod
    def _make_key(cls, player_id):
        return str(cls._PLAYER_BOXSCORE_LIST_KEY % (player_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._PLAYER_BOXSCORE_LIST_KEY % "*")

    @classmethod
    def add_player_boxscore(cls, player_id, game_id, t):
        key = cls._make_key(player_id)
        cls._client.zadd(key, game_id, t)

    @classmethod
    def get_player_boxscore_list(
            cls, player_id, offset=settings.DEFAULT_PLAYER_GAME_LIST_OFFSET):
        key = cls._make_key(player_id)
        return cls._client.zrange(key, 0, offset - 1, desc=True)

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)


class CachePlayerTCRank(object):
    _TC_RANK_KEY = 'TCRK'
    _client = player_rclient

    @classmethod
    def _make_key(cls):
        return str(cls._TC_RANK_KEY)

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._TC_RANK_KEY)

    @classmethod
    def add_player_pt(cls, player_id, pt):
        key = cls._make_key()
        cls._client.zadd(key, player_id, pt)

    @classmethod
    def get_player_pt_rank(cls, offset=-1):
        key = cls._make_key()
        return cls._client.zrange(key, 0, offset, desc=True)

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)


class SnapshotPlayerSalary(object):
    KEY_PREFIX = 'SnapshotPlayerSalary'
    _client = player_rclient

    @classmethod
    def _make_key(cls):
        return '%s' % cls.KEY_PREFIX

    @classmethod
    def store(cls, salary_date, data: dict) -> int:
        if not salary_date:
            return 0
        if isinstance(data, dict):
            data = json.dumps(data)
        key = cls._make_key()
        return cls._client.hset(key, salary_date, data)

    @classmethod
    def exists(cls, salary_date) -> bool:
        if not salary_date:
            return False
        key = cls._make_key()
        return cls._client.hexists(key, salary_date)

    @classmethod
    def load(cls, salary_date) -> dict:
        if not salary_date:
            return {}
        key = cls._make_key()
        data = cls._client.hget(key, salary_date)
        if not data:
            return {}
        data = data.decode()
        return json.loads(data, object_pairs_hook=OrderedDict)


class SnapshotPlayerTeam(SnapshotPlayerSalary):
    KEY_PREFIX = 'SnapshotPlayerTeam'


class SnapshotPlayerStat(SnapshotPlayerSalary):
    KEY_PREFIX = 'SnapshotPlayerStat'


class CachePlayerSalary(object):
    _PLAYER_SALARY_KEY = 'PS:%s'
    _client = player_rclient

    @classmethod
    def _make_key(cls, player_id):
        return str(cls._PLAYER_SALARY_KEY % (player_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._PLAYER_SALARY_KEY % "*")

    @classmethod
    def set_player_salary(cls, player_id, salary):
        key = cls._make_key(player_id)
        cls._client.set(key, salary)

    @classmethod
    def get_player_salary(cls, player_id):
        key = cls._make_key(player_id)
        return cls._client.get(key)

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)

class CacheCurrentPlayerList(object):
    _CURRENT_PLAYER_LIST = 'CPL:%s'
    _client = player_rclient

    @classmethod
    def _make_key(cls, date):
        return str(cls._CURRENT_PLAYER_LIST % date)

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys("CPL:*")

    @classmethod
    def set_player_list(cls, date, player_list):
        key = cls._make_key(date)
        cls._client.setex(key, player_list, settings.DEFAULT_PLAYER_LIST_TIMEOUT)

    @classmethod
    def _get_player_list(cls, date, contest_id):
        from ttnba.contest.models import get_contest_obj
        obj = get_contest_obj(contest_id)
        player_list = obj.get_contest_player_list_json()

        return simplejson.dumps(player_list)

    @classmethod
    def get_player_list(cls, date, contest_id):
        key = cls._make_key(date)
        player_list = cls._client.get(key)
        if not player_list:
            player_list = cls._get_player_list(date, contest_id)
            cls.set_player_list(date, player_list)
        return player_list

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)

class NoInjuryCacheDailyPlayerList(object):
    _CACHE_TODAY_PLAYER_LIST = 'NICDPL:%s'
    _client = player_rclient

    @classmethod
    def _make_key(cls, date):
        return str(cls._CACHE_TODAY_PLAYER_LIST % date)

    @classmethod
    def set_player_list(cls, date, player_list):
        key = cls._make_key(date)
        cls._client.setex(key, player_list, settings.DEFAULT_PLAYER_LIST_TIMEOUT)

    @classmethod
    def _get_player_list(cls, date):
        players = CacheDailyPlayerList.get_player_list(date)
        players = json.loads(players)
        for p in players:
            if p['injury']:
                players.remove(p)

        return simplejson.dumps(players)

    @classmethod
    def get_player_list(cls, date):
        key = cls._make_key(date)
        player_list = cls._client.get(key)
        if isinstance(player_list, bytes):
            player_list = player_list.decode('utf-8')
        if player_list == '[]' or not player_list:
            player_list = cls._get_player_list(date)
            cls.set_player_list(date, player_list)
        return player_list

class CacheDailyPlayerList(object):
    _CACHE_TODAY_PLAYER_LIST = 'CDPL:%s'
    _client = player_rclient

    @classmethod
    def _make_key(cls, date):
        return str(cls._CACHE_TODAY_PLAYER_LIST % date)

    @classmethod
    def set_player_list(cls, date, player_list):
        key = cls._make_key(date)
        cls._client.setex(key, player_list, settings.DEFAULT_PLAYER_LIST_TIMEOUT)

    @classmethod
    def _get_player_list(cls, date):
        from ttnba.nba.models import NBATeam, NBAGame
        games = NBAGame.objects.filter(is_active=True, game_date=date).all()
        teams = []
        player_list = []
        for game in games:
            teams.append(game.away_team)
            teams.append(game.home_team)
        for team in teams:
            queryset = team.qq_current_player
            queryset = queryset.filter(is_active=True).all()
            for p in queryset:
                if p.player:
                    player_list.append(p.player.get_salary_json(date))

        return simplejson.dumps(player_list)

    @classmethod
    def get_player_list(cls, date):
        key = cls._make_key(date)
        player_list = cls._client.get(key)
        if isinstance(player_list, bytes):
            player_list = player_list.decode('utf-8')
        if player_list == '[]' or not player_list:
            player_list = cls._get_player_list(date)
            cls.set_player_list(date, player_list)
        return player_list

class CacheTeamPlayerList(object):
    _TEAM_PLAYER_LIST_KEY = 'TPL:%s:%s'
    _client = player_rclient

    @classmethod
    def _make_key(cls, team_slug, date):
        return str(cls._TEAM_PLAYER_LIST_KEY % (team_slug, date))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys("TPL:*")

    @classmethod
    def set_team_player_list(cls, team_slug, date, player_list):
        key = cls._make_key(team_slug, date)
        cls._client.setex(key, player_list,
                          settings.DEFAULT_PLAYER_LIST_TIMEOUT)

    @classmethod
    def _get_team_player_from_model(cls, team_slug, date):
        from ttnba.nba.models import NBATeam
        team = NBATeam.objects.get(ta=team_slug)
        player_list = []

        queryset = team.qq_current_player

        queryset = queryset.filter(is_active=True).all()
        for p in queryset:
            if p.player:
                player_list.append(p.player.get_salary_json(date))
        return simplejson.dumps(player_list)

    @classmethod
    def get_team_player_list(cls, team_slug, date, force_reload=False):
        key = cls._make_key(team_slug, date)
        if settings.DEBUG:
            return cls._get_team_player_from_model(team_slug, date)
        player_list = cls._client.get(key)
        if not player_list:
            player_list = cls._get_team_player_from_model(team_slug, date)
            cls.set_team_player_list(team_slug, date, player_list)
        return player_list

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)

class CurrentSuperPlayer(object):
    _CurrentSuperPlayerKey= 'CurrentSuperPlayer'
    _client = player_rclient

    @classmethod
    def _make_key(cls):
        return str(cls._CurrentSuperPlayerKey)

    @classmethod
    def get_player(cls, date: str) -> int:
        key = cls._make_key()
        player_id = cls._client.hget(key, date)
        if not player_id or player_id == b'None':
            return cls.set_player(date)
        return int(player_id)

    @classmethod
    def set_player(cls, date: str):
        from ttnba.nba.models import NBATeam, NBAGame, PlayerCategory
        game = NBAGame.objects.filter(is_active=True, game_date=date).order_by('id').first()
        team = game.home_team
        queryset = team.qq_current_player
        queryset = queryset.filter(is_active=True).order_by('id').all()
        id = None
        for p in queryset:
            if p.player:
                pc = PlayerCategory.objects.filter(is_active=True, player=p.player).first()
                if pc and pc.category == 'SUPER':
                    id = str(p.player.id)

        if not id:
            for p in queryset:
                p = queryset[0]
                if p.player:
                    id = str(p.player.id)

        key = cls._make_key()
        cls._client.hset(key, date, id)

        return int(id)

    @classmethod
    def remove_player(cls, date: str):
        key = cls._make_key()
        cls._client.hdel(key, date)
