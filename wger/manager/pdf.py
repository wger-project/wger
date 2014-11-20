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
import datetime

from django.http import HttpResponse
from django.http import HttpResponseForbidden
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from django.utils.translation import ugettext as _

from wger.manager.models import Workout
from wger.utils.helpers import check_token
from wger.utils.pdf import styleSheet

from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import Paragraph
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import Table
from reportlab.platypus import Spacer
from reportlab.lib import colors

from wger import get_version

logger = logging.getLogger('wger.custom')


def workout_log(request, id, uidb64=None, token=None):
    '''
    Generates a PDF with the contents of the given workout

    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    '''

    # Load the workout
    if uidb64 is not None and token is not None:
        if check_token(uidb64, token):
            workout = get_object_or_404(Workout, pk=id)
        else:
            return HttpResponseForbidden()
    else:
        if request.user.is_anonymous():
            return HttpResponseForbidden()
        workout = get_object_or_404(Workout, pk=id, user=request.user)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response,
                            pagesize=A4,
                            # pagesize = landscape(A4),
                            leftMargin=cm,
                            rightMargin=cm,
                            topMargin=0.5 * cm,
                            bottomMargin=0.5 * cm,
                            title=_('Workout'),
                            author='wger Workout Manager',
                            subject=_('Workout for %s') % request.user.username)

    # container for the 'Flowable' objects
    elements = []

    # table data, here we will put the workout info
    data = []

    # Init several counters and markers, this will be used after the iteration to
    # set different borders and colours
    day_markers = []
    exercise_markers = {}
    group_exercise_marker = {}
    group_day_marker = {}

    # Set the number of weeks for this workout
    # (sets number of columns for the weight/date log)
    nr_of_weeks = 7

    # Set the first column of the weight log, depends on design
    first_weight_column = 3

    # Background colour for days
    # Reportlab doesn't use the HTML hexadecimal format, but has a range of
    # 0 till 1, so we have to convert here.
    header_colour = colors.Color(int('73', 16) / 255.0,
                                 int('8a', 16) / 255.0,
                                 int('5f', 16) / 255.0)

    #
    # Iterate through the Workout
    #

    # Days
    for day in workout.canonical_representation['day_list']:
        set_count = 1
        day_markers.append(len(data))
        group_day_marker[day['obj'].id] = {'start': len(data), 'end': len(data)}

        if not exercise_markers.get(day['obj'].id):
            exercise_markers[day['obj'].id] = []

        P = Paragraph('<para align="center">%(days)s: %(description)s</para>' %
                      {'days': day['days_of_week']['text'],
                       'description': day['obj'].description},
                      styleSheet["Bold"])

        data.append([P])

        # Note: the _('Date') will be on the 3rd cell, but since we make a span
        #       over 3 cells, the value has to be on the 1st one
        data.append([_('Date') + ' ', '', ''] + [''] * nr_of_weeks)
        data.append([_('Nr.'), _('Exercise'), _('Reps')] + [_('Weight')] * nr_of_weeks)

        # Sets
        for set in day['set_list']:
            group_exercise_marker[set['obj'].id] = {'start': len(data), 'end': len(data)}

            # Exercises
            for exercise in set['exercise_list']:
                group_exercise_marker[set['obj'].id]['end'] = len(data)

                # Note: '+1' here because there's an emtpy cell between days
                exercise_markers[day['obj'].id].append(len(data) + 1)

                data.append([set_count,
                             Paragraph(exercise['obj'].name, styleSheet["Small"]),
                             exercise['setting_text']]
                            + [''] * nr_of_weeks)
            set_count += 1

        data.append([''])
        group_day_marker[day['obj'].id]['end'] = len(data)

        # Set the widths and heights of rows and columns
        # Note: 'None' is treated as 'automatic'. Either there is only one value for the whole list
        #       or exactly one for every row/column
        colwidths = None
        rowheights = [None] * len(data)

    # Set general table styles
    table_style = [('FONT', (0, 0), (-1, -1), 'OpenSans'),
                   ('FONTSIZE', (0, 0), (-1, -1), 8),
                   ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

                   # Note: a padding of 3 seems to be the default
                   ('LEFTPADDING', (0, 0), (-1, -1), 2),
                   ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                   ('TOPPADDING', (0, 0), (-1, -1), 3),
                   ('BOTTOMPADDING', (0, 0), (-1, -1), 2), ]

    # Set specific styles, e.g. background for title cells
    for marker in day_markers:
        # Set background colour for headings
        table_style.append(('BACKGROUND', (0, marker), (-1, marker), header_colour))
        table_style.append(('BOX', (0, marker), (-1, marker), 1.25, colors.black))
        table_style.append(('BOX', (0, marker), (-1, marker + 2), 1.25, colors.black))

        # Make the headings span the whole width
        table_style.append(('SPAN', (0, marker), (-1, marker)))

        # Make the space between days span the whole width
        table_style.append(('SPAN', (0, marker - 1), (-1, marker - 1)))

        # Manually set
        rowheights[marker - 1] = 5

        # Make the date span 3 cells and align it to the right
        table_style.append(('ALIGN', (0, marker + 1), (2, marker + 1), 'RIGHT'))
        table_style.append(('SPAN', (0, marker + 1), (2, marker + 1)))

    # Combine the cells for exercises on the same set
    for marker in group_exercise_marker:
        start_marker = group_exercise_marker[marker]['start']
        end_marker = group_exercise_marker[marker]['end']

        table_style.append(('VALIGN', (0, start_marker), (0, end_marker), 'MIDDLE'))
        table_style.append(('SPAN', (0, start_marker), (0, end_marker)))

    # Set an alternating background colour for rows
    for i in exercise_markers:
        counter = 1
        for j in exercise_markers[i]:
            if not j % 2:
                table_style.append(('BACKGROUND', (1, j - 1), (-1, j - 1), colors.lavender))
            counter += 1

    # Make the 'impression' span 3 cells and align it to the right
    for marker in group_day_marker:
        start_marker = group_day_marker[marker]['start']
        end_marker = group_day_marker[marker]['end']

        # There is an empty cell between the day blocks, set a border around them
        table_style.append(('INNERGRID',
                            (0, start_marker),
                            (- 1, end_marker - 2),
                            0.25,
                            colors.black))
        table_style.append(('BOX',
                            (0, start_marker),
                            (-1, end_marker - 2),
                            1.25,
                            colors.black))

    # Set the table data
    if data:
        t = Table(data, colwidths, rowheights, style=table_style)

        # Manually set the width of the columns
        for i in range(first_weight_column, nr_of_weeks + first_weight_column):
            t._argW[i] = 1.8 * cm  # Columns for entering the log

        t._argW[0] = 0.6 * cm  # Exercise numbering
        t._argW[1] = 3.5 * cm  # Name of exercise
        t._argW[2] = 2 * cm  # Repetitions

    # There is nothing to output
    else:
        t = Paragraph(_('<i>This is an empty workout, what did you expect on the PDF?</i>'),
                      styleSheet["Normal"])

    #
    # Add all elements to the document
    #

    # Set the title (if available)
    if workout.comment:
        P = Paragraph('<para align="center"><strong>%(description)s</strong></para>' %
                      {'description': workout.comment},
                      styleSheet["Bold"])
        elements.append(P)

        # Filler
        elements.append(Spacer(10*cm, 0.5*cm))

    # Append the table
    elements.append(t)

    # Footer, date and info
    elements.append(Spacer(10*cm, 0.5*cm))
    created = datetime.date.today().strftime("%d.%m.%Y")
    url = reverse('manager:workout:view', kwargs={'id': workout.id})
    P = Paragraph('''<para align="left">
                        %(date)s -
                        <a href="%(url)s">%(url)s</a> -
                        %(created)s
                        %(version)s
                    </para>''' %
                  {'date': _("Created on the <b>%s</b>") % created,
                   'created': "wger Workout Manager",
                   'version': get_version(),
                   'url': request.build_absolute_uri(url), },
                  styleSheet["Normal"])
    elements.append(P)

    # write the document and send the response to the browser
    doc.build(elements)

    # Create the HttpResponse object with the appropriate PDF headers.
    response['Content-Disposition'] = 'attachment; filename=Workout-{0}-log.pdf'.format(id)
    response['Content-Length'] = len(response.content)
    return response


@login_required
def workout_view(request, id, uidb64=None, token=None):
    '''
    Generates a PDF with the contents of the workout, without table for logs
    '''

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')

    # Load the workout
    if uidb64 is not None and token is not None:
        if check_token(uidb64, token):
            workout = get_object_or_404(Workout, pk=id)
    else:
        if request.user.is_anonymous():
            return HttpResponseForbidden()
        workout = get_object_or_404(Workout, pk=id, user=request.user)

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(response,
                            pagesize=A4,
                            # pagesize = landscape(A4),
                            leftMargin=cm,
                            rightMargin=cm,
                            topMargin=0.5 * cm,
                            bottomMargin=0.5 * cm,
                            title=_('Workout'),
                            author='wger Workout Manager',
                            subject=_('Workout for %s') % request.user.username)

    # container for the 'Flowable' objects
    elements = []

    # table data, here we will put the workout info
    data = []

    # Init several counters and markers, this will be used after the iteration to
    # set different borders and colours
    day_markers = []
    exercise_markers = {}
    group_exercise_marker = {}
    group_day_marker = {}

    # Background colour for days
    # Reportlab doesn't use the HTML hexadecimal format, but has a range of
    # 0 till 1, so we have to convert here.
    header_colour = colors.Color(int('73', 16) / 255.0,
                                 int('8a', 16) / 255.0,
                                 int('5f', 16) / 255.0)

    #
    # Iterate through the Workout
    #

    # Days
    for day in workout.canonical_representation['day_list']:
        set_count = 1
        day_markers.append(len(data))
        group_day_marker[day['obj'].id] = {'start': len(data), 'end': len(data)}

        if not exercise_markers.get(day['obj'].id):
            exercise_markers[day['obj'].id] = []

        p = Paragraph('<para align="center">%(days)s: %(description)s</para>' %
                      {'days': day['days_of_week']['text'],
                       'description': day['obj'].description},
                      styleSheet["Bold"])

        data.append([p])

        # Sets
        for set in day['set_list']:
            group_exercise_marker[set['obj'].id] = {'start': len(data), 'end': len(data)}

            # Exercises
            for exercise in set['exercise_list']:
                group_exercise_marker[set['obj'].id]['end'] = len(data)

                # Note: '+1' here because there's an emtpy cell between days
                exercise_markers[day['obj'].id].append(len(data) + 1)
                data.append([set_count,
                             Paragraph(exercise['obj'].name, styleSheet["Small"]),
                             exercise['setting_text']])
            set_count += 1

        data.append([''])
        group_day_marker[day['obj'].id]['end'] = len(data)

        # Set the widths and heights of rows and columns
        # Note: 'None' is treated as 'automatic'. Either there is only one value for the whole list
        #       or exactly one for every row/column
        colwidths = None
        rowheights = [None] * len(data)

    table_style = [('FONT', (0, 0), (-1, -1), 'OpenSans'),
                   ('FONTSIZE', (0, 0), (-1, -1), 8),
                   ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),

                   # Note: a padding of 3 seems to be the default
                   ('LEFTPADDING', (0, 0), (-1, -1), 2),
                   ('RIGHTPADDING', (0, 0), (-1, -1), 0),
                   ('TOPPADDING', (0, 0), (-1, -1), 3),
                   ('BOTTOMPADDING', (0, 0), (-1, -1), 2), ]

    # Set specific styles, e.g. background for title cells
    for marker in day_markers:
        # Set background colour for headings
        table_style.append(('BACKGROUND', (0, marker), (-1, marker), header_colour))
        table_style.append(('BOX', (0, marker), (-1, marker), 1.25, colors.black))

        # Make the headings span the whole width
        table_style.append(('SPAN', (0, marker), (-1, marker)))

        # Manually set
        rowheights[marker - 1] = 5

    # Combine the cells for exercises on the same set
    counter = 1
    for marker in group_exercise_marker:
        counter += 1
        start_marker = group_exercise_marker[marker]['start']
        end_marker = group_exercise_marker[marker]['end']

        table_style.append(('SPAN', (0, start_marker), (0, end_marker)))
        table_style.append(('BOX',
                            (0, start_marker),
                            (-1, end_marker),
                            0.25,
                            colors.black))

        if counter % 2:
            table_style.append(('BACKGROUND',
                                (0, start_marker),
                                (-1, end_marker),
                                colors.lavender))

    for marker in group_day_marker:
        start_marker = group_day_marker[marker]['start']
        end_marker = group_day_marker[marker]['end']

        table_style.append(('BOX',
                            (0, start_marker),
                            (-1, end_marker - 2),
                            1.25,
                            colors.black))

    # Set the table data
    if data:
        t = Table(data, colwidths, rowheights, style=table_style)

        # Manually set the width of the columns
        if len(t._argW) > 1:
            t._argW[0] = 0.6 * cm  # Numbering
            t._argW[1] = 9 * cm  # Exercise
            t._argW[2] = 4 * cm  # Repetitions

    # There is nothing to output
    else:
        t = Paragraph(_('<i>This is an empty workout, what did you expect on the PDF?</i>'),
                      styleSheet["Normal"])

    #
    # Add all elements to the document
    #

    # Set the title (if available)
    if workout.comment:
        p = Paragraph('<para align="center"><strong>%(description)s</strong></para>' %
                      {'description': workout.comment},
                      styleSheet["Bold"])
        elements.append(p)

        # Filler
        elements.append(Spacer(10*cm, 0.5*cm))

    # Append the table
    elements.append(t)

    # Footer, date and info
    elements.append(Spacer(10*cm, 0.5*cm))
    created = datetime.date.today().strftime("%d.%m.%Y")
    url = reverse('manager:workout:view', kwargs={'id': workout.id})
    p = Paragraph('''<para align="left">
                        %(date)s -
                        <a href="%(url)s">%(url)s</a> -
                        %(created)s
                        %(version)s
                    </para>''' %
                  {'date': _("Created on the <b>%s</b>") % created,
                   'created': "wger Workout Manager",
                   'version': get_version(),
                   'url': request.build_absolute_uri(url), },
                  styleSheet["Normal"])
    elements.append(p)

    # write the document and send the response to the browser
    doc.build(elements)

    # Create the HttpResponse object with the appropriate PDF headers.
    response['Content-Disposition'] = 'attachment; filename=Workout-{0}-table.pdf'.format(id)
    response['Content-Length'] = len(response.content)
    return response
