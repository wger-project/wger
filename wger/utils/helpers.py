# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

import logging
import decimal
import json
import datetime

from functools import wraps


logger = logging.getLogger('wger.custom')


class DecimalJsonEncoder(json.JSONEncoder):
    '''
    Custom JSON encoder.

    This class is needed because we store some data as a decimal (e.g. the
    individual weight entries in the workout log) and they need to be
    processed, json.dumps() doesn't work on them
    '''
    def default(self, obj):
        if isinstance(obj, decimal.Decimal):
            return str(obj)
            #return "%.2f" % obj
        return json.JSONEncoder.default(self, obj)


def disable_for_loaddata(signal_handler):
    '''
    Decorator to prevent clashes when loading data with loaddata and
    post_connect signals. See also:
    http://stackoverflow.com/questions/3499791/how-do-i-prevent-fixtures-from-conflicting
    '''
    @wraps(signal_handler)
    def wrapper(*args, **kwargs):
        if kwargs['raw']:
            #print "Skipping signal for {0} {1}".format(args, kwargs)
            return
        signal_handler(*args, **kwargs)
    return wrapper


def next_weekday(date, weekday):
    '''
    Helper function to find the next weekday after a given date,
    e.g. the first Monday after the 2013-12-05

    See link for more details:
    * http://stackoverflow.com/questions/6558535/python-find-the-date-for-the-first-monday-after-a

    :param date: the start date
    :param weekday: weekday (0, Monday, 1 Tuesday, 2 Wednesday)
    :type date: datetime.date
    :type weekday int
    :return: datetime.date
    '''
    days_ahead = weekday - date.weekday()
    if days_ahead <= 0:
        days_ahead += 7
    return date + datetime.timedelta(days_ahead)
