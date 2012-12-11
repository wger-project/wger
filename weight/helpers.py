# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
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

from weight.models import WeightEntry

logger = logging.getLogger('workout_manager.custom')


def parse_weight_csv(request, cleaned_data):

    try:
        dialect = csv.Sniffer().sniff(cleaned_data['csv_input'])
    except csv.Error:
        logger.debug('Error while sniffing CSV format')
        dialect='excel'

    # csv.reader expects a file-like object, so use StringIO
    parsed_csv = csv.reader(StringIO.StringIO(cleaned_data['csv_input']),
                            dialect)

    weight_list = []
    error_list = []
    for row in parsed_csv:
        try:
            parsed_date = datetime.datetime.strptime(row[0], cleaned_data['date_format'])
            parsed_weight =  decimal.Decimal(row[1].replace(',', '.'))
            weight_list.append(WeightEntry(creation_date=parsed_date,
                                           weight=parsed_weight,
                                           user=request.user))
        except (ValueError, decimal.InvalidOperation), e:
            error_list.append(row)
            logger.debug(e)

    return (weight_list, error_list)
