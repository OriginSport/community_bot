#coding=utf-8

from django.conf import settings

from .base import rank_rclient


class UserLastestChoice(object):
    _RANK_KEY = 'ULC:%s'
    _client = rank_rclient

    @classmethod
    def _make_key(cls, user_id):
        return str(cls._RANK_KEY % (user_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._RANK_KEY % "*")

    @classmethod
    def add_choices(cls,
                    user_id,
                    choice_list,
                    limit=settings.DEFAULT_LATEST_CHOICE_LIMIT):
        key = cls._make_key(user_id)
        exist_choices = cls.get_choices(user_id, limit)
        for choice in exist_choices:
            if not choice in choice_list:
                cls._client.lpush(key, choice)
        for choice in choice_list:
            cls._client.lpush(key, choice)
        cls._client.ltrim(key, 0, limit - 1)

    @classmethod
    def get_choices(cls, user_id, limit=settings.DEFAULT_LATEST_CHOICE_LIMIT):
        key = cls._make_key(user_id)
        choices = cls._client.lrange(key, 0, limit - 1)
        return choices

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)


class UserCommonChoice(object):
    _RANK_KEY = 'UCC:%s'
    _client = rank_rclient

    @classmethod
    def _make_key(cls, user_id):
        return str(cls._RANK_KEY % (user_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._RANK_KEY % "*")

    @classmethod
    def add_choices(cls,
                    user_id,
                    choices,
                    limit=settings.DEFAULT_COMMON_CHOICE_LIMIT):
        key = cls._make_key(user_id)
        # exist_choices = cls.get_choices(user_id, limit)
        for choice in choices:
            # if choice in exist_choices:
            #     cls._client.zincrby(key, choice, 1)
            # else:
            #     cls._client.zadd(key, choice, 1)
            cls._client.zincrby(key, choice, 1)

    @classmethod
    def get_choices(cls, user_id, limit=settings.DEFAULT_COMMON_CHOICE_LIMIT):
        key = cls._make_key(user_id)
        choices = cls._client.zrange(key, 0, limit, withscores=True)
        choices.reverse()

        return choices

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)
