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
import six
import datetime
import decimal
import csv
import json
from collections import OrderedDict

from django.core.cache import cache

from wger.utils.helpers import DecimalJsonEncoder
from wger.utils.cache import cache_mapper
from wger.weight.models import WeightEntry
from wger.manager.models import WorkoutSession
from wger.manager.models import WorkoutLog

logger = logging.getLogger(__name__)


def parse_weight_csv(request, cleaned_data):

    try:
        dialect = csv.Sniffer().sniff(cleaned_data['csv_input'])
    except csv.Error:
        dialect = 'excel'

    # csv.reader expects a file-like object, so use StringIO
    parsed_csv = csv.reader(six.StringIO(cleaned_data['csv_input']),
                            dialect)
    distinct_weight_entries = []
    weight_list = []
    error_list = []

    # Process the CSV items first
    for row in parsed_csv:
        try:
            parsed_date = datetime.datetime.strptime(row[0], cleaned_data['date_format'])
            parsed_weight = decimal.Decimal(row[1].replace(',', '.'))
            duplicate_date_in_db = WeightEntry.objects.filter(date=parsed_date,
                                                              user=request.user)
            # within the list there are no duplicates
            unique_among_csv = (parsed_date, parsed_weight) not in distinct_weight_entries
            # there is no existing weight entry in the database for that date
            unique_in_db = not duplicate_date_in_db

            if unique_among_csv and unique_in_db:
                distinct_weight_entries.append((parsed_date, parsed_weight))
            else:
                error_list.append(row)

        except (ValueError, IndexError, decimal.InvalidOperation):
            error_list.append(row)

    # Create the valid weight entries
    for date, weight in distinct_weight_entries:
        weight_list.append(WeightEntry(date=date,
                                       weight=weight,
                                       user=request.user))

    return (weight_list, error_list)


def group_log_entries(user, year, month, day=None):
    '''
    Processes and regroups a list of log entries so they can be more easily
    used in the different calendar pages

    :param user: the user to filter the logs for
    :param year: year
    :param month: month
    :param day: optional, day

    :return: a dictionary with grouped logs by date and exercise
    '''
    if day:
        log_hash = hash((user.pk, year, month, day))
    else:
        log_hash = hash((user.pk, year, month))

    # There can be workout sessions without any associated log entries, so it is
    # not enough so simply iterate through the logs
    if day:
        filter_date = datetime.date(year, month, day)
        logs = WorkoutLog.objects.filter(user=user, date=filter_date)
        sessions = WorkoutSession.objects.filter(user=user, date=filter_date)

    else:
        logs = WorkoutLog.objects.filter(user=user,
                                         date__year=year,
                                         date__month=month)

        sessions = WorkoutSession.objects.filter(user=user,
                                                 date__year=year,
                                                 date__month=month)

    logs = logs.order_by('date', 'id')
    out = cache.get(cache_mapper.get_workout_log_list(log_hash))
    # out = OrderedDict()

    if not out:
        out = OrderedDict()

        # Logs
        for entry in logs:
            if not out.get(entry.date):
                out[entry.date] = {'date': entry.date,
                                   'workout': entry.workout,
                                   'session': entry.get_workout_session(),
                                   'logs': OrderedDict()}

            if not out[entry.date]['logs'].get(entry.exercise):
                out[entry.date]['logs'][entry.exercise] = []

            out[entry.date]['logs'][entry.exercise].append(entry)

        # Sessions
        for entry in sessions:
            if not out.get(entry.date):
                out[entry.date] = {'date': entry.date,
                                   'workout': entry.workout,
                                   'session': entry,
                                   'logs': {}}

        cache.set(cache_mapper.get_workout_log_list(log_hash), out)
    return out


def process_log_entries(logs):
    '''
    Processes and regroups a list of log entries so they can be rendered
    and passed to the D3 library to render a chart
    '''

    reps = []
    entry_log = OrderedDict()
    chart_data = []
    max_weight = {}

    # Group by date
    for entry in logs:
        if entry.reps not in reps:
            reps.append(entry.reps)

        if not entry_log.get(entry.date):
            entry_log[entry.date] = []
        entry_log[entry.date].append(entry)

        # Find the maximum weight per date per repetition.
        # If on a day there are several entries with the same number of
        # repetitions, but different weights, only the entry with the
        # higher weight is shown in the chart
        if not max_weight.get(entry.date):
            max_weight[entry.date] = {entry.reps: entry.weight}

        if not max_weight[entry.date].get(entry.reps):
            max_weight[entry.date][entry.reps] = entry.weight

        if entry.weight > max_weight[entry.date][entry.reps]:
            max_weight[entry.date][entry.reps] = entry.weight

    # Group by repetitions
    reps_list = {}
    for entry in logs:
        temp = {'date': '%s' % entry.date,
                'id': 'manager:workout:log-%s' % entry.id}

        # Only unique date, rep and weight combinations
        if reps_list.get((entry.date, entry.reps, entry.weight)):
            continue
        else:
            reps_list[(entry.date, entry.reps, entry.weight)] = True

        # Only add if weight is the maximum for the day
        if entry.weight != max_weight[entry.date][entry.reps]:
            continue

        for rep in reps:
            if entry.reps == rep:
                temp[rep] = entry.weight
            else:
                # Mark entries without data, this is later filtered out by D3.
                # We use the string 'n.a' instead of 0 to differentiate actual exercises
                # where no weight was used.
                temp[rep] = 'n.a'
        chart_data.append(temp)

    return entry_log, json.dumps(chart_data, cls=DecimalJsonEncoder)
