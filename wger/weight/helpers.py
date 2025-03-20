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

# Standard Library
import csv
import datetime
import decimal
import io
import logging
from collections import OrderedDict

# Django
from django.core.cache import cache

# wger
from wger.manager.models import (
    WorkoutLog,
    WorkoutSession,
)
from wger.utils.cache import cache_mapper
from wger.weight.models import WeightEntry


logger = logging.getLogger(__name__)


def parse_weight_csv(request, cleaned_data):
    try:
        dialect = csv.Sniffer().sniff(cleaned_data['csv_input'])
    except csv.Error:
        dialect = 'excel'

    # csv.reader expects a file-like object, so use StringIO
    parsed_csv = csv.reader(io.StringIO(cleaned_data['csv_input']), dialect)
    distinct_weight_entries = []
    entry_dates = set()
    weight_list = []
    error_list = []
    MAX_ROW_COUNT = 1000
    row_count = 0

    # Process the CSV items first
    for row in parsed_csv:
        try:
            parsed_date = datetime.datetime.strptime(row[0], cleaned_data['date_format'])
            parsed_weight = decimal.Decimal(row[1].replace(',', '.'))
            duplicate_date_in_db = WeightEntry.objects.filter(
                date=parsed_date, user=request.user
            ).exists()
            # within the list there are no duplicate dates
            unique_among_csv = parsed_date not in entry_dates

            # there is no existing weight entry in the database for that date
            unique_in_db = not duplicate_date_in_db

            if unique_among_csv and unique_in_db and parsed_weight:
                distinct_weight_entries.append((parsed_date, parsed_weight))
                entry_dates.add(parsed_date)
            else:
                error_list.append(row)

        except (ValueError, IndexError, decimal.InvalidOperation):
            error_list.append(row)
        row_count += 1
        if row_count > MAX_ROW_COUNT:
            break

    # Create the valid weight entries
    for date, weight in distinct_weight_entries:
        weight_list.append(WeightEntry(date=date, weight=weight, user=request.user))

    return (weight_list, error_list)


def group_log_entries(user, year, month, day=None):
    """
    Processes and regroups a list of log entries so they can be more easily
    used in the different calendar pages

    :param user: the user to filter the logs for
    :param year: year
    :param month: month
    :param day: optional, day

    :return: a dictionary with grouped logs by date and exercise
    """
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
        logs = WorkoutLog.objects.filter(user=user, date__year=year, date__month=month)

        sessions = WorkoutSession.objects.filter(user=user, date__year=year, date__month=month)

    logs = logs.order_by('date', 'id')
    out = cache.get(cache_mapper.get_workout_log_list(log_hash))
    # out = OrderedDict()

    if not out:
        out = OrderedDict()

        # Logs
        for entry in logs:
            if not out.get(entry.date):
                out[entry.date] = {
                    'date': entry.date,
                    'workout': entry.workout,
                    'session': entry.session,
                    'logs': OrderedDict(),
                }

            if not out[entry.date]['logs'].get(entry.exercise):
                out[entry.date]['logs'][entry.exercise] = []

            out[entry.date]['logs'][entry.exercise].append(entry)

        # Sessions
        for entry in sessions:
            if not out.get(entry.date):
                out[entry.date] = {
                    'date': entry.date,
                    'workout': entry.workout,
                    'session': entry,
                    'logs': {},
                }

        cache.set(cache_mapper.get_workout_log_list(log_hash), out)
    return out


def get_last_entries(user, amount=5):
    """
    Get the last weight entries as well as the difference to the last

    This can be used e.g. to present a list where the last entries and
    their changes are presented.
    """

    last_entries = WeightEntry.objects.filter(user=user).order_by('-date')[:5]
    last_entries_details = []

    for index, entry in enumerate(last_entries):
        curr_entry = entry
        prev_entry_index = index + 1

        if prev_entry_index < len(last_entries):
            prev_entry = last_entries[prev_entry_index]
        else:
            prev_entry = None

        if prev_entry and curr_entry:
            weight_diff = curr_entry.weight - prev_entry.weight
            day_diff = (curr_entry.date - prev_entry.date).days
        else:
            weight_diff = day_diff = None
        last_entries_details.append((curr_entry, weight_diff, day_diff))

    return last_entries_details
