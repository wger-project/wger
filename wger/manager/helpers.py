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

# Standard Library
import datetime
from calendar import HTMLCalendar

# Django
from django.urls import reverse
from django.utils.translation import gettext as _

# Third Party
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    KeepTogether,
    ListFlowable,
    ListItem,
    Paragraph,
    Table
)

# wger
from wger.utils.pdf import (
    header_colour,
    row_color,
    styleSheet
)


def render_workout_day(day, nr_of_weeks=7, images=False, comments=False, only_table=False):
    """
    Render a table with reportlab with the contents of the training day

    :param day: a workout day object
    :param nr_of_weeks: the numbrer of weeks to render, default is 7
    :param images: boolean indicating whether to also draw exercise images
           in the PDF (actually only the main image)
    :param comments: boolean indicathing whether the exercise comments will
           be rendered as well
    :param only_table: boolean indicating whether to draw a table with space
           for weight logs or just a list of the exercises
    """

    # If rendering only the table, reset the nr of weeks, since these columns
    # will not be rendered anyway.
    if only_table:
        nr_of_weeks = 0

    data = []

    # Init some counters and markers, this will be used after the iteration to
    # set different borders and colours
    day_markers = []
    group_exercise_marker = {}

    set_count = 1
    day_markers.append(len(data))

    p = Paragraph('<para align="center">%(days)s: %(description)s</para>' %
                  {'days': day['days_of_week']['text'],
                   'description': day['obj'].description},
                  styleSheet["SubHeader"])

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

            # Process the settings
            if exercise['has_weight']:
                setting_out = []
                for i in exercise['setting_text'].split('–'):
                    setting_out.append(Paragraph(i, styleSheet["Small"], bulletText=''))
            else:
                setting_out = Paragraph(exercise['setting_text'], styleSheet["Small"])

            # Collect a list of the exercise comments
            item_list = [Paragraph('', styleSheet["Small"])]
            if comments:
                item_list = [ListItem(Paragraph(i, style=styleSheet["ExerciseComments"]))
                             for i in exercise['comment_list']]

            # Add the exercise's main image
            image = Paragraph('', styleSheet["Small"])
            if images:
                if exercise['obj'].main_image:

                    # Make the images somewhat larger when printing only the workout and not
                    # also the columns for weight logs
                    if only_table:
                        image_size = 2
                    else:
                        image_size = 1.5

                    image = Image(exercise['obj'].main_image.image)
                    image.drawHeight = image_size * cm * image.drawHeight / image.drawWidth
                    image.drawWidth = image_size * cm

            # Put the name and images and comments together
            exercise_content = [Paragraph(exercise['obj'].name, styleSheet["Small"]),
                                image,
                                ListFlowable(item_list,
                                             bulletType='bullet',
                                             leftIndent=5,
                                             spaceBefore=7,
                                             bulletOffsetY=-3,
                                             bulletFontSize=3,
                                             start='square')]

            data.append([f"#{set_count}",
                         exercise_content,
                         setting_out]
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
            table_style.append(('BACKGROUND', (0, i - 1), (-1, i - 1), row_color))

    # Put everything together and manually set some of the widths
    t = Table(data, style=table_style)
    if len(t._argW) > 1:
        if only_table:
            t._argW[0] = 0.6 * cm  # Numbering
            t._argW[1] = 8 * cm  # Exercise
            t._argW[2] = 3.5 * cm  # Repetitions
        else:
            t._argW[0] = 0.6 * cm  # Numbering
            t._argW[1] = 4 * cm  # Exercise
            t._argW[2] = 3 * cm  # Repetitions

    return KeepTogether(t)


class WorkoutCalendar(HTMLCalendar):
    """
    A calendar renderer, see this blog entry for details:
    * http://uggedal.com/journal/creating-a-flexible-monthly-calendar-in-django/
    """
    def __init__(self, workout_logs, *args, **kwargs):
        super(WorkoutCalendar, self).__init__(*args, **kwargs)
        self.workout_logs = workout_logs

    def formatday(self, day, weekday):

        # days belonging to last or next month are rendered empty
        if day == 0:
            return self.day_cell('noday', '&nbsp;')

        date_obj = datetime.date(self.year, self.month, day)
        cssclass = self.cssclasses[weekday]
        if datetime.date.today() == date_obj:
            cssclass += ' today'

        # There are no logs for this day, doesn't need special attention
        if date_obj not in self.workout_logs:
            return self.day_cell(cssclass, day)

        # Day with a log, set background and link
        entry = self.workout_logs.get(date_obj)

        # Note: due to circular imports we use can't import the workout session
        # model to access the impression values directly, so they are hard coded
        # here.
        if entry['session']:
            # Bad
            if entry['session'].impression == '1':
                background_css = 'btn-danger'
            # Good
            elif entry['session'].impression == '3':
                background_css = 'btn-success'
            # Neutral
            else:
                background_css = 'btn-warning'

        else:
            background_css = 'btn-warning'

        url = reverse('manager:log:log', kwargs={'pk': entry['workout'].id})
        formatted_date = date_obj.strftime('%Y-%m-%d')
        body = []
        body.append('<a href="{0}" '
                    'data-log="log-{1}" '
                    'class="btn btn-block {2} calendar-link">'.format(url,
                                                                      formatted_date,
                                                                      background_css))
        body.append(repr(day))
        body.append('</a>')
        return self.day_cell(cssclass, '{0}'.format(''.join(body)))

    def formatmonth(self, year, month):
        """
        Format the table header. This is basically the same code from python's
        calendar module but with additional bootstrap classes
        """
        self.year, self.month = year, month
        out = []
        out.append('<table class="month table table-bordered">\n')
        out.append(self.formatmonthname(year, month))
        out.append('\n')
        out.append(self.formatweekheader())
        out.append('\n')
        for week in self.monthdays2calendar(year, month):
            out.append(self.formatweek(week))
            out.append('\n')
        out.append('</table>\n')
        return ''.join(out)

    def day_cell(self, cssclass, body):
        """
        Renders a day cell
        """
        return '<td class="{0}" style="vertical-align: middle;">{1}</td>'.format(cssclass, body)
