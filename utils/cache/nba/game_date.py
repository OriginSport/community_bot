import datetime
from ..base import cache_rclient


def check_date(date_str) -> bool:
    try:
        datetime.datetime.strptime(date_str, '%Y-%m-%d')
        return True
    except Exception as ex:
        return False


_game_dates = None

class NBAGameDateCache(object):

    KEY = 'ALL_NBA_GAME_DATE'
    _client = cache_rclient

    @classmethod
    def store(cls, game_dates_str: str):
        return cls._client.set(cls.KEY, game_dates_str)

    @classmethod
    def load(cls) -> list:
        global _game_dates
        if _game_dates:
            return _game_dates

        value = cls._client.get(cls.KEY)
        if not value:
            return []
        _game_dates = value.decode().split(',')

        return _game_dates

    @classmethod
    def get_previous_game_date(cls, base_date) -> str:
        assert check_date(base_date)
        game_dates = cls.load()
        if not game_dates:
            return ''
        for date in sorted(game_dates, reverse=True):
            if date < base_date:
                assert check_date(date)
                return date
        return ''

    @classmethod
    def is_contest_game_date(cls, date) -> bool:
        assert check_date(date)
        game_dates = cls.load()
        return date in game_dates

    @classmethod
    def get_next_game_date(cls, base_date) -> str:
        assert check_date(base_date)
        game_dates = cls.load()
        if not game_dates:
            return ''
        for date in sorted(game_dates):
            if date > base_date:
                assert check_date(date)
                return date
        return ''
