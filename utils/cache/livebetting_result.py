from collections import namedtuple

from .base import livebetting_rclient

BettingParams = namedtuple('BettingParams',
                           ('stats_key', 'game_id', 'quarter', 'player_1_id',
                            'player_1_tid', 'player_2_id', 'player_2_tid'))

BettingParams.__doc__ = """
    ('stats_key', 'game_id', 'quarter', 'player_1_id','player_1_tid', 'player_2_id', 'player_2_tid')
"""


class LiveBettingResult(object):
    """Get LiveBetting Instance Result

     result depends ttlivenba service.

    usage::

        LiveBettingsResult(CommonBet()).result

    """

    _FIRST_TEAM_KEY_TPL = 'LIVENBA:FIRST:TEAM:{quarter}:{stats_key}'  # hset(game_id, team_id)
    _MOST_TEAM_KEY_TPL = 'LIVENBA:MOST:TEAM:{quarter}:{stats_key}'  # hset(game_id, team_id)

    _FIRST_PLAYER_KEY_TPL = 'LIVENBA:FIRST:PLAYER:{quarter}:{stats_key}'  # hset(game_id, player_id)
    _MOST_PLAYER_KEY_TPL = 'LIVENBA:MOST:PLAYER:{quarter}:{stats_key}:{game_id}'  # zadd(score, player_id)

    _client = livebetting_rclient

    betting_params = None
    commonbet_obj = None
    func = None  # func(commonbet_obj)

    def _make_key(self, key_tpl: str, **kwargs):
        return key_tpl.format(**kwargs)

    def __init__(self, commonbet_obj):
        assert hasattr(commonbet_obj, 'category_id')
        assert hasattr(commonbet_obj, 'game_id')

        category_id = commonbet_obj.category_id

        self.commonbet_obj = commonbet_obj
        self.betting_params = self._get_bettingparams(commonbet_obj)
        self.func = self.result_func_mapper.get(category_id, None)

    def get_result(self):
        return self.func()

    @property
    def result(self):
        return self.get_result()

    @property
    def result_func_mapper(self):
        return {
            1: self._most_team_of,
            2: self._first_team_of,
            3: self._first_team_of,
            4: self._first_team_of,
            5: self._most_player_of,
            6: self._most_player_of,
            7: self._most_team_of,
            8: self._most_player_of,
            9: self._most_team_of,
            10: self._first_team_of,
            11: self._most_team_of,
            12: self._most_team_of,
            13: self._most_player_of,
        }

    def _most_team_of(self):
        quarter = self.betting_params.quarter
        stats_key = self.betting_params.stats_key

        key = self._make_key(
            self._MOST_TEAM_KEY_TPL, quarter=quarter, stats_key=stats_key)
        game_id = self.betting_params.game_id
        result = self._client.hget(key, game_id)
        return int(result) if result else None

    def _first_team_of(self):
        quarter = self.betting_params.quarter
        stats_key = self.betting_params.stats_key

        key = self._make_key(
            self._FIRST_TEAM_KEY_TPL, quarter=quarter, stats_key=stats_key)
        game_id = self.betting_params.game_id
        result = self._client.hget(key, game_id)
        return int(result) if result else None

    def _most_player_of(self):
        """if scores are the same, hls always win(player_2)
        player_1 is vls
        player_2 is hls
        """
        quarter = self.betting_params.quarter
        stats_key = self.betting_params.stats_key
        game_id = self.betting_params.game_id

        key = self._make_key(
            self._MOST_PLAYER_KEY_TPL,
            quarter=quarter,
            stats_key=stats_key,
            game_id=game_id)

        player_1_id = self.betting_params.player_1_id
        player_1_tid = self.betting_params.player_1_tid
        player_1_score = self._client.zscore(key, player_1_id)
        player_1_score = int(player_1_score) if player_1_score else 0

        player_2_id = self.betting_params.player_2_id
        player_2_tid = self.betting_params.player_2_tid
        player_2_score = self._client.zscore(key, player_2_id)
        player_2_score = int(player_2_score) if player_2_score else 0

        if not player_1_score and not player_2_score:
            return None

        result = player_1_id if player_1_score > player_2_score else player_2_id
        return int(result)

    def _get_bettingparams(self, commonbet_obj):
        category = commonbet_obj.category

        stats_key = category.data_dimension.lower()
        if category.team_player.upper() == 'TEAM' \
            and category.data_dimension.upper() == 'PTS':

            stats_key = 's'

        game_id = commonbet_obj.game_id
        quarter = category.end_time[0]

        if category.team_player == 'PLAYER':
            player_1_id = commonbet_obj.option_1_player.id
            player_1_tid = commonbet_obj.option_1_player.tid
            player_2_id = commonbet_obj.option_2_player.id
            player_2_tid = commonbet_obj.option_2_player.tid
        else:
            player_1_id = player_1_tid = player_2_id = player_2_tid = None

        return BettingParams(stats_key, game_id, quarter, player_1_id,
                             player_1_tid, player_2_id, player_2_tid)
