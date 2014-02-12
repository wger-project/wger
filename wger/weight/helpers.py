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
import StringIO
import datetime
import decimal
import csv
import json
from collections import OrderedDict

from wger.utils.helpers import DecimalJsonEncoder
from wger.weight.models import WeightEntry

logger = logging.getLogger('wger.custom')


def parse_weight_csv(request, cleaned_data):

    try:
        dialect = csv.Sniffer().sniff(cleaned_data['csv_input'])
    except csv.Error:
        #logger.debug('Error while sniffing CSV format')
        dialect = 'excel'

    # csv.reader expects a file-like object, so use StringIO
    parsed_csv = csv.reader(StringIO.StringIO(cleaned_data['csv_input']),
                            dialect)

    weight_list = []
    error_list = []
    for row in parsed_csv:
        try:
            parsed_date = datetime.datetime.strptime(row[0], cleaned_data['date_format'])
            parsed_weight = decimal.Decimal(row[1].replace(',', '.'))

            weight_list.append(WeightEntry(creation_date=parsed_date,
                                           weight=parsed_weight,
                                           user=request.user))

        except (ValueError, IndexError, decimal.InvalidOperation):
            error_list.append(row)
            #logger.debug(row)
            #logger.debug(e)

    return (weight_list, error_list)


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
                'id': 'workout-log-%s' % entry.id}

        # Only unique date, rep and weight combinations
        if reps_list.get('{0}-{1}-{2}'.format(entry.date, entry.reps, entry.weight)):
            continue
        else:
            reps_list['{0}-{1}-{2}'.format(entry.date, entry.reps, entry.weight)] = True

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
