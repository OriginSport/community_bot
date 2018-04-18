#coding=utf-8

import datetime
import time
from gettext import gettext, ngettext


def iso_to_datetime(s):
    return datetime.datetime.fromtimestamp(
        time.mktime(time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')))


def datetime_to_iso(d):
    if d:
        return d.strftime('%Y-%m-%dT%H:%M:%SZ')


def datetime_to_stamp(d):
    return int(time.mktime(d.timetuple()))


def stamp_to_datetime(s):
    return datetime.datetime.fromtimestamp(s)


def duration_to_cn(duration):
    if not duration:
        return ''

    chunks = (
        (60 * 60, lambda n: _ungettext(u'小时', u'小时', n)),
        (60, lambda n: _ungettext(u'分钟', u'分钟', n)),
        #(1, lambda n: _ungettext(u'秒', u'秒', n))
    )

    if duration <= 0:
        # d is in the future compared to now, stop processing.
        return u'0'

    for i, (seconds, name) in enumerate(chunks):
        count = duration // seconds
        if count != 0:
            break

    s = _ugettext('%(number)d %(type)s') % {
        'number': count,
        'type': name(count)
    }
    for seconds2, name2 in chunks[i + 1:]:
        # Now get the second item
        count2 = (duration - (seconds * count)) // seconds2
        if count2 != 0:
            s += _ugettext(',%(number)d%(type)s') % {
                'number': count2,
                'type': name2(count2)
            }

    if duration % 60 > 0:
        s += _ugettext(u',%s秒' % str(duration % 60))
    return s


def _ungettext(singular, plural, number):
    """ stupid wrapper yet waiting internationalisation """
    return ngettext(singular, plural, number)


def _ugettext(message):
    """ stupid wrapper yet waiting internationalisation """
    return gettext(message)


if __name__ == '__main__':
    #now = datetime.datetime.now()
    #print 'datetime:',  now
    #s = datetime_to_stamp(now)
    #print 'stamp:', s

    print(duration_to_cn(36111))
