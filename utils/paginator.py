#coding=utf-8
"""
    Paginator utils 
"""

import urllib

from django.conf import settings

from .view_tools import get_args, ok_json
from werkzeug import cached_property


def get_request_page(request):
    if request:
        page = request.get_argument('page', 1)
        try:
            page = int(page)
        except:
            page = 1
        return page
    return 1


def url_quote(s):
    if isinstance(s, str):
        s = s.encode('utf-8')
    return urllib.parse.quote(s)


def recover_page_url(path_info, request_data, page_name='page'):
    return '%s?%s' % (path_info, '&'.join([
        d[0] + '=' + url_quote(d[1]) for d in request_data.items()
        if d[0] != page_name
    ]))


class BasePaginator(object):

    def __init__(self, query, page_size, page=None, request=None):
        self.query = query
        self.page_size = page_size
        self.request = request
        if page:
            self.page = int(page)
        else:
            self.page = get_request_page(self.request)

    @cached_property
    def count(self):
        return self.query.count()

    @cached_property
    def entries(self):
        return self.query.offset((self.page -1) * self.page_size)\
                         .limit(self.page_size).all()

    def _construct_link(self, page):
        if len(self.request.args):
            if len(self.request.args) == 1 and self.request.args.get('page',
                                                                     None):
                return '?'.join([self.request.path, 'page=%s' % page])
            else:
                return '&'.join([
                    recover_page_url(self.request.path, self.request.args),
                    'page=%s' % page
                ])
        else:
            return '?'.join([self.request_path, 'page=%s' % page])

    has_previous = property(lambda x: x.page > 1)
    has_next = property(lambda x: x.page < x.pages)
    pages = property(lambda x: max(0, x.count - 1) // x.page_size + 1)
    previous = property(lambda x: x._construct_link(x.page - 1))
    next = property(lambda x: x._construct_link(x.page + 1))


class CommonPaginator(BasePaginator):

    def __init__(self, result, wrapper, page, page_size, request, limit=None, \
            pager_width=settings.APP_PAGINATOR_DEFAULT_WIDTH, \
            pager_lmargin=settings.APP_PAGINATOR_DEFAULT_LMARGIN, **params):

        self.result = result
        self.wrapper = wrapper

        self.page_size = page_size
        self.page = page

        if not hasattr(request, 'args'):
            args = get_args(request)
            request.args = args

        self.request = request

        self.limit = limit

        self.request_args = {}
        for k, v in request.args.items():
            if v:
                self.request_args[k] = v[0]
        self.request_path = request.path

        self.window_pager = WindowPager(self.pages, pager_width, pager_lmargin)
        #if self.page > self.pages:
        #    self.page = 1

    @property
    def count(self):
        if hasattr(self, '_count'):
            return self._count

        count = len(self.result)
        if count:
            if self.limit and self.limit < count:
                count = self.limit
        else:
            count = 0
        self._count = count
        return self._count

    def add_entry(self, entry):
        if hasattr(self, '_entries'):
            self._entries.append(entry)
        else:
            self._entries = self.entries
            self._entries.append(entry)

    @property
    def entry_count(self):
        return len(self.entries)

    @property
    def entry_ids(self):
        if hasattr(self, '_entry_ids'):
            return self._entry_ids
        else:
            self._entry_ids = [x.id for x in self.entries]
            return self._entry_ids

    @property
    def entries(self):
        if hasattr(self, '_entries'):
            return self._entries

        offset = (self.page - 1) * self.page_size
        if offset + self.page_size > self.count:
            page_size = self.count - offset
        else:
            page_size = self.page_size

        result = self.result[offset:offset + page_size]

        if self.wrapper:
            self._entries = self.wrapper(result)
        else:
            self._entries = result

        return self._entries

    has_previous = property(lambda x: x.page > 1)
    has_next = property(lambda x: x.page < x.pages)
    pages = property(lambda x: max(0, x.count - 1) // x.page_size + 1)
    next = property(lambda x: x._construct_link(x.page + 1))
    first = property(lambda x: x._construct_link(1))
    last = property(lambda x: x._construct_link(x.pages))
    indexes = property(lambda x: [ (idx, x._construct_link(idx)) for idx in x.window_pager.get_indexes(x.page) ])


class WindowPager:
    """
        implement a pager with window cursor like google
    """

    def __init__(self, count, width, left_margin):
        self.width = width
        self.left_margin = left_margin
        self.count = count

    def get_indexes(self, current):
        self.current = current

        if self.count >= self.width:
            if self.current <= self.left_margin:
                self.head = 0
            else:
                if self.count - self.current > self.width - self.left_margin:
                    self.head = self.current - self.left_margin
                else:
                    self.head = self.count - self.width

            return range(self.head + 1, self.head + self.width + 1)
        else:
            return range(1, self.count + 1)


class StaticPaginator(CommonPaginator):

    def _construct_link(self, page):
        path_list = self.request_path.split('/')
        path_buf = path_list[:-1]
        path_buf.append(str(page))
        return '/'.join(path_buf) + '.html'


class EmptyPaginator(object):

    def __init__(self):
        self.count = 0
        self.entries = []
        self.has_previous = False
        self.has_next = False
        self.pages = 0


def dict_pagination_response(object_list,
                             request,
                             page,
                             page_size,
                             wrapper=None):
    if not object_list or len(object_list) == 0:
        return {'object_list': [], 'meta': None}
    paginator = CommonPaginator(object_list, wrapper, page, page_size, request)
    return {
        'object_list': paginator.entries,
        'meta': {
            'page_size': page_size,
            'prev': paginator.previous if paginator.has_previous else None,
            'next': paginator.next if paginator.has_next else None,
            'page': paginator.page,
            'page_list': paginator.indexes,
            'total_page': paginator.pages,
            'total_count': paginator.count
        }
    }


def json_pagination_response(object_list,
                             request,
                             page,
                             page_size,
                             wrapper=None):
    return ok_json(
        dict_pagination_response(object_list, request, page, page_size,
                                 wrapper))
