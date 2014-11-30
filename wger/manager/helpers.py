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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import Paragraph
from reportlab.platypus import Table
from reportlab.platypus import KeepTogether

from django.utils.translation import ugettext as _

from wger.utils.pdf import styleSheet


def render_workout_day(day, nr_of_weeks):
    '''
    Render a table with reportlab with the contents of the training day
    '''

    data = []

    # Init some counters and markers, this will be used after the iteration to
    # set different borders and colours
    day_markers = []
    group_exercise_marker = {}

    # Background colour for days
    # Reportlab doesn't use the HTML hexadecimal format, but has a range of
    # 0 till 1, so we have to convert here.
    header_colour = colors.Color(int('73', 16) / 255.0,
                                 int('8a', 16) / 255.0,
                                 int('5f', 16) / 255.0)

    set_count = 1
    day_markers.append(len(data))

    p = Paragraph('<para align="center">%(days)s: %(description)s</para>' %
                  {'days': day['days_of_week']['text'],
                   'description': day['obj'].description},
                  styleSheet["Bold"])

    data.append([p])

    # Note: the _('Date') will be on the 3rd cell, but since we make a span
    #       over 3 cells, the value has to be on the 1st one
    data.append([_('Date') + ' ', '', ''] + [''] * nr_of_weeks)
    data.append([_('Nr.'), _('Exercise'), _('Reps')] + [_('Weight')] * nr_of_weeks)

    # Sets
    exercise_start = len(data)
    for set in day['set_list']:
        group_exercise_marker[set['obj'].id] = {'start': len(data), 'end': len(data)}

        # Exercises
        for exercise in set['exercise_list']:
            group_exercise_marker[set['obj'].id]['end'] = len(data)

            data.append([set_count,
                         Paragraph(exercise['obj'].name, styleSheet["Small"]),
                         exercise['setting_text']]
                        + [''] * nr_of_weeks)
        set_count += 1

    table_style = [('FONT', (0, 0), (-1, -1), 'OpenSans'),
                   ('FONTSIZE', (0, 0), (-1, -1), 8),
                   ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                   ('LEFTPADDING', (0, 0), (-1, -1), 2),
                   ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                   ('TOPPADDING', (0, 0), (-1, -1), 3),
                   ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                   ('INNERGRID', (0, 0), (-1, -1), 0.25, colors.black),

                   # Header
                   ('BACKGROUND', (0, 0), (-1, 0), header_colour),
                   ('BOX', (0, 0), (-1, -1), 1.25, colors.black),
                   ('BOX', (0, 1), (-1, -1), 1.25, colors.black),
                   ('SPAN', (0, 0), (-1, 0)),

                   # Cell with 'date'
                   ('SPAN', (0, 1), (2, 1)),
                   ('ALIGN', (0, 1), (2, 1), 'RIGHT')]

    # Combine the cells for exercises on the same superset
    for marker in group_exercise_marker:
        start_marker = group_exercise_marker[marker]['start']
        end_marker = group_exercise_marker[marker]['end']

        table_style.append(('VALIGN', (0, start_marker), (0, end_marker), 'MIDDLE'))
        table_style.append(('SPAN', (0, start_marker), (0, end_marker)))

    # Set an alternating background colour for rows with exercises.
    # The rows with exercises range from exercise_start till the end of the data
    # list
    for i in range(exercise_start, len(data) + 1):
        if not i % 2:
            table_style.append(('BACKGROUND', (1, i - 1), (-1, i - 1), colors.lavender))

    # Put everything together and manually set some of the widths
    t = Table(data, style=table_style)
    if len(t._argW) > 1:
        t._argW[0] = 0.6 * cm  # Numbering
        t._argW[1] = 4 * cm  # Exercise
        t._argW[2] = 2 * cm  # Repetitions

    return KeepTogether(t)


def reps_smart_text(settings, set_obj):
    '''
    "Smart" textual representation
    This is a human representation of the settings, in a way that humans
    would also write: e.g. "8 8 10 10" but "4 x 10" and not "10 10 10 10"

    :param settings:
    :param set_obj:
    :return setting_text, setting_list:
    '''
    if len(settings) == 0:
        setting_text = ''
        setting_list = []
    elif len(settings) == 1:
        reps = settings[0].reps if settings[0].reps != 99 else u'∞'
        setting_text = u'{0} × {1}'.format(set_obj.sets, reps)
        setting_list = [settings[0].reps] * set_obj.sets
    elif len(settings) > 1:
        tmp_reps_text = []
        tmp_reps = []
        for i in settings:
            reps = str(i.reps) if i.reps != 99 else u'∞'
            tmp_reps_text.append(reps)
            tmp_reps.append(i.reps)

        setting_text = u' – '.join(tmp_reps_text)
        setting_list = tmp_reps

    return setting_text, setting_list
