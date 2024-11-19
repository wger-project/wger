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

# Django
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
    Table,
)

# wger
from wger.utils.pdf import (
    header_colour,
    row_color,
    styleSheet,
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

    p = Paragraph(
        '<para align="center">%(days)s: %(description)s</para>'
        % {'days': day.days_txt, 'description': day.description},
        styleSheet['SubHeader'],
    )

    data.append([p])

    # Note: the _('Date') will be on the 3rd cell, but since we make a span
    #       over 3 cells, the value has to be on the 1st one
    data.append([_('Date') + ' ', '', ''] + [''] * nr_of_weeks)
    data.append([_('Nr.'), _('Exercise'), _('Reps')] + [_('Weight')] * nr_of_weeks)

    # Sets
    exercise_start = len(data)
    for set_obj in day.set_set.all():
        group_exercise_marker[set_obj.id] = {'start': len(data), 'end': len(data)}

        # Exercises
        for base in set_obj.exercise_bases:
            exercise = base.get_translation()
            group_exercise_marker[set_obj.id]['end'] = len(data)

            # Process the settings
            setting_out = []
            for i in set_obj.reps_smart_text(base).split('–'):
                setting_out.append(Paragraph(i, styleSheet['Small'], bulletText=''))

            # Collect a list of the exercise comments
            item_list = [Paragraph('', styleSheet['Small'])]
            if comments:
                item_list = [
                    ListItem(Paragraph(i.comment, style=styleSheet['ExerciseComments']))
                    for i in exercise.exercisecomment_set.all()
                ]

            # Add the exercise's main image
            image = Paragraph('', styleSheet['Small'])
            if images:
                if base.main_image:
                    # Make the images somewhat larger when printing only the workout and not
                    # also the columns for weight logs
                    if only_table:
                        image_size = 2
                    else:
                        image_size = 1.5

                    image = Image(base.main_image.image)
                    image.drawHeight = image_size * cm * image.drawHeight / image.drawWidth
                    image.drawWidth = image_size * cm

            # Put the name and images and comments together
            exercise_content = [
                Paragraph(exercise.name, styleSheet['Small']),
                image,
                ListFlowable(
                    item_list,
                    bulletType='bullet',
                    leftIndent=5,
                    spaceBefore=7,
                    bulletOffsetY=-3,
                    bulletFontSize=3,
                    start='square',
                ),
            ]

            data.append([f'#{set_count}', exercise_content, setting_out] + [''] * nr_of_weeks)
        set_count += 1

    table_style = [
        ('FONT', (0, 0), (-1, -1), 'OpenSans'),
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
        ('ALIGN', (0, 1), (2, 1), 'RIGHT'),
    ]

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
