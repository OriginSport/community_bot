# -*- coding: utf-8 -*-

import simplejson
import traceback
import logging
from redis import Redis
import collections

class RedisPublishClient(object):
    
    def __init__(self, host, port, channel, password=''):
        self.host = host
        self.port = port
        self.channel = 'ch:'+channel
        self.client = Redis(host=self.host, port=self.port, password=password, db=0) 
    
    def publish_message(self, msg):
        try:
            if isinstance(msg, dict):
                msg = simplejson.dumps(msg)
            result = self.client.publish(self.channel, msg)
            return result
        except Exception as e:
            logging.error('redis publish message error: %s'%e)


def check_callable(cb):
    if not isinstance(cb, collections.Callable):
        raise TypeError("callback isn't a callable")


class RedisConsumer():
    
    def __init__(self, host, port, channel, password='', **kwargs):
        self.client = Redis(host=host, port=int(port), password=password)
        self.channel = 'ch:%s'%channel
        self.pubsub = self.client.pubsub()
    
    def wait(self, cb, **params):
        check_callable(cb)
        self.pubsub.subscribe(self.channel)
        for msg in self.pubsub.listen():
            try:
                if msg.get('type') != 'subscribe':
                    cb(msg['data'])
            except:
                traceback.print_exc()


