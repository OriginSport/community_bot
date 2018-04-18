#coding=utf-8

import logging
import datetime

import utils.errors as err

from utils.view_tools import ok_json, fail_json, get_args
from utils.timeutils import stamp_to_datetime
from utils.cache.page import PageCache

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sessions.models import Session
from django.views.decorators.csrf import csrf_exempt


class AbstractAPI(object):
    logger = logging.getLogger(__name__)
    args = None

    def __init__(self, cache_args=[]):
        self.config_args()
        self.cache_args = cache_args

    def config_args(self):
        self.args = {}

    def access_db(self, kwarg):
        return fail_json(err.ERROR_CODE_UNDEFINED)

    def format_data(self, data):
        if data is not None:
            if isinstance(data, models.query.QuerySet):
                return ok_json([d.get_json() for d in data])
            return ok_json(data.get_json())
        return fail_json(err.ERROR_CODE_DATABASE_ACCESS_ERROR)

    def cache_page(self, cache_key, data, timeout=settings.DEFAULT_PAGE_CACHE_TIMEOUT):
        if not settings.DEBUG:
            PageCache.set_page_key(cache_key, data, timeout)

    def make_cache_key(self, kwarg):
        arg_list = list(kwarg.items())
        arg_list.sort(key=lambda x: x[0])
        key = kwarg['request'].path
        for arg in arg_list:
            if arg[0] in self.cache_args:
                key += '?' + '%s=%s' % arg
        return key

    def wrap_func(self, cache_args=[]):
        @csrf_exempt
        def wrapper(request):
            args = get_args(request)
            kwarg = {'request': request}
            for k in self.args:
                if self.args[k] == 'r' and (k not in args or args[k] == ""):
                    return fail_json(err.ERROR_CODE_INVALID_ARGS, k)
                val = args.get(k, None)
                if not val and isinstance(self.args[k], tuple):
                    val = self.args[k][1]
                kwarg[k] = val

            if self.cache_args != [] and not settings.DEBUG:
                cache_key = self.make_cache_key(kwarg)
                cache_data = PageCache.get_page_key(cache_key)
                if cache_data:
                    return ok_json(cache_data)

            obj = self.access_db(kwarg)
            return self.format_data(obj)

        return wrapper
