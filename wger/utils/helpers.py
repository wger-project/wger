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

import decimal
import json


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
