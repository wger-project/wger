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
import decimal

from django.utils.translation import ugettext as _

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Table

from wger.utils.constants import TWOPLACES


def render_routine_week(week_data):
    '''
    Helper function that renders a week of a routine.

    :param week_data:
    :return: a reportlab Table object
    '''
    data = [[_('Day'), _('Exercise'), _('Repetitions'), _('Weight')]]
    previous_day = print_day = 0
    for day in week_data:

        # 'filler' rows
        if day['day'] != previous_day:
            if previous_day != 0:
                data.append([''])
            previous_day = day['day']
            print_day = day['day']
        else:
            print_day = ''

        # Routine data
        weight = day['weight']
        if day['weight'] == 'max':
            weight = _('your max!')
        elif day['weight'] == 'auto':
            weight = _('some weight')
        data.append([print_day,
                     day['exercise'],
                     u"{0} × {1}".format(day['sets'], day['reps']),
                     weight])

    table_style = [('FONT', (0, 0), (-1, -1), 'OpenSans'),
                   ('FONTSIZE', (0, 0), (-1, -1), 10),
                   ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                   ('ALIGN', (-1, 0), (-1, -1), 'RIGHT'),
                   ('BOX', (0, 1), (-1, 0), 0.25, colors.black)]

    t = Table(data, style=table_style, hAlign='LEFT')
    t._argW[0] = 2 * cm  # Day
    t._argW[1] = 7 * cm  # Exercise
    t._argW[2] = 4 * cm  # Repetitions
    t._argW[3] = 4 * cm  # Weight
    return t
