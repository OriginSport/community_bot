#coding=utf-8

from ..base import task_rclient


class CreateRoomTimesVerify(object):
    _CREATE_ROOM_TIMES_VERIFY_KEY = 'CRTV:%s'
    _client = task_rclient

    @classmethod
    def _make_key(cls, user_id):
        return str(cls._CREATE_ROOM_TIMES_VERIFY_KEY % (user_id))

    @classmethod
    def get_all_keys(cls):
        return cls._client.keys(cls._CREATE_ROOM_TIMES_VERIFY_KEY % "*")

    @classmethod
    def set_user_create_room_times(cls, user_id, count):
        key = cls._make_key(user_id)
        cls._client.set(key, count)

    @classmethod
    def get_user_create_room_times(cls, user_id):
        key = cls._make_key(user_id)
        count = cls._client.get(key)
        if count:
            return int(count)
        else:
            return 0

    @classmethod
    def delete(cls):
        all_keys = cls.get_all_keys()
        for key in all_keys:
            cls._client.delete(key)
