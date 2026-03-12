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
from decimal import Decimal

# Django
from django.core.cache import cache
from django.utils.translation import gettext as _

# Third Party
from reportlab.lib import colors
from reportlab.lib.units import cm
from reportlab.platypus import (
    KeepTogether,
    Paragraph,
    Table,
)

# wger
from wger.exercises.models import Exercise
from wger.manager.dataclasses import WorkoutDayData
from wger.manager.models import Routine
from wger.utils.cache import CacheKeyMapper
from wger.utils.pdf import (
    header_colour,
    row_color,
    styleSheet,
)


def render_workout_day(
    day_data: WorkoutDayData,
    nr_of_weeks=7,
    only_table=False,
):
    """
    Render a table with reportlab with the contents of the training day

    :param day_data: a workout day object
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

    data.append(
        [
            Paragraph(
                f'<para align="center">{_("Rest day") if day_data.day.is_rest else day_data.day.name}</para>',
                styleSheet['SubHeader'],
            )
        ]
    )

    # Note: the _('Date') will be on the 3rd cell, but since we make a span
    #       over 3 cells, the value has to be on the 1st one
    data.append(['' if only_table else _('Date') + ' ', '', ''] + [''] * nr_of_weeks)
    data.append([_('Nr.'), _('Exercise'), _('Reps')] + [_('Weight')] * nr_of_weeks)

    # Sets
    exercise_start = len(data)
    slot_count = 0
    for slot in day_data.slots_display_mode:
        slot_count += 1

        group_exercise_marker[slot_count] = {'start': len(data), 'end': len(data)}

        for slot_set in slot.sets:
            # TODO
            exercise = Exercise.objects.get(pk=slot_set.exercise)
            group_exercise_marker[slot_count]['end'] = len(data)

            # Process the settings
            slot_entries_out = [Paragraph(slot_set.text_repr, styleSheet['Small'], bulletText='')]

            # Add the exercise's main image
            # image = Paragraph('', styleSheet['Small'])
            # if images:
            #     if exercise.main_image:
            #         # Make the images somewhat larger when printing only the workout and not
            #         # also the columns for weight logs
            #         if only_table:
            #             image_size = 2
            #         else:
            #             image_size = 1.5
            #
            #         image = Image(exercise.main_image.image)
            #         image.drawHeight = image_size * cm * image.drawHeight / image.drawWidth
            #         image.drawWidth = image_size * cm

            # Put the name and images and comments together
            exercise_content = [
                Paragraph(exercise.get_translation().name, styleSheet['Small']),
                # image,
            ]

            data.append([f'#{set_count}', exercise_content, slot_entries_out] + [''] * nr_of_weeks)
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
    if only_table:
        col_widths = [
            0.6 * cm,  # Numbering
            7 * cm,  # Exercise
            7 * cm,  # Repetitions
        ]
    else:
        col_widths = [
            0.6 * cm,  # Numbering
            6 * cm,  # Exercise
            6 * cm,  # Repetitions
            1.5 * cm,  # Logs
        ]

    t = Table(data, style=table_style, colWidths=col_widths)

    return KeepTogether(t)


def reset_routine_cache(instance: Routine, structure: bool = True):
    """Resets all caches related to a routine"""

    cache.delete(CacheKeyMapper.routine_date_sequence_key(instance.id))
    cache.delete(
        CacheKeyMapper.routine_api_date_sequence_display_key(instance.id, instance.user_id)
    )
    cache.delete(CacheKeyMapper.routine_api_date_sequence_gym_key(instance.id, instance.user_id))
    cache.delete(CacheKeyMapper.routine_api_logs(instance.id, instance.user_id))
    cache.delete(CacheKeyMapper.routine_api_stats(instance.id, instance.user_id))

    if structure:
        cache.delete(CacheKeyMapper.routine_api_structure_key(instance.id, instance.user_id))

    if instance.pk:
        for day in instance.days.all():
            for slot in day.slots.all():
                for entry in slot.entries.all():
                    cache.delete(CacheKeyMapper.slot_entry_configs_key(entry.id))


def brzycki_one_rm(weight: float | None, reps: float | None) -> Decimal:
    return Decimal(weight) / (Decimal(1.0278) - Decimal(0.0278) * Decimal(reps))


def brzycki_intensity(weight, reps) -> Decimal:
    one_rm = brzycki_one_rm(weight, reps)
    return Decimal(weight / one_rm if one_rm != 0 else 0)
