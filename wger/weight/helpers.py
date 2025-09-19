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

# wger
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

    return weight_list, error_list
