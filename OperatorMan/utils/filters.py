# -*- coding: utf-8 -*-

"""
created: 14-11-10 10:36

@author: brian<zhangfan@yunfan.com>
"""
import time
import datetime

from OperatorMan.configs import settings



def iso_to_datetime(s):
    """ Converts iso time format to `datetime.datetime`

    @param s: iso time
    """
    return datetime.datetime.fromtimestamp(time.mktime(time.strptime(s, '%Y-%m-%dT%H:%M:%SZ')))


def datetime_to_stamp(dt):
    """ Converts `datetime` to timestamp.

    @param dt: instance of `datetime.datetime`
    """
    return int(time.mktime(dt.timetuple()))


def stamp_to_datetime(ts):
    """ Converts timestamp to `datetime.datetime`

    @param ts: int timestamp
    """
    return datetime.datetime.fromtimestamp(ts)


def str_to_datetime(date_string, format_='%Y-%m-%d %H:%M:%S'):
    """ Converts date string to specific `datetime.datetime` value

    @param date_string: str e.g. "2014-02-27 12:32:14"
    @param format_: str
    """
    return datetime.datetime.strptime(date_string, format_)

JINJA2_FILTERS = {
    'iso_to_datetime':          iso_to_datetime,
    'datetime_to_stamp':        datetime_to_stamp,
    'stamp_to_datetime':        stamp_to_datetime,
    'str_to_datetime':          str_to_datetime
}


JINJA2_GLOBALS = {
    'SERVER_NAME':             settings.SERVER_NAME
}
