#!/usr/bin/env python
# -*- coding: utf-8 -*-
from .base import publish_rclient


class RedisPublish(object):
    _client = publish_rclient

    def __init__(self, channel: str):
        self.channel = 'ch:' + channel

    def pub_msg(self, msg: str):
        self._client.publish(self.channel, msg)
