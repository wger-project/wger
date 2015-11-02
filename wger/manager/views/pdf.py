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
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _

from wger.manager.models import Workout
from wger.manager.helpers import render_workout_day
from wger.utils.helpers import check_token
from wger.utils.pdf import styleSheet
from wger.utils.pdf import render_footer

from reportlab.lib.pagesizes import A4, cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Table,
    Spacer
)

from reportlab.lib import colors

from wger import get_version

logger = logging.getLogger(__name__)


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

    # Set the title
    p = Paragraph('<para align="center"><strong>%(description)s</strong></para>' %
                  {'description': workout},
                  styleSheet["HeaderBold"])
    elements.append(p)
    elements.append(Spacer(10 * cm, 0.5 * cm))

    # Iterate through the Workout and render the training days
    for day in workout.canonical_representation['day_list']:
        elements.append(render_workout_day(day, nr_of_weeks=7))
        elements.append(Spacer(10 * cm, 0.5 * cm))

    # Footer, date and info
    elements.append(Spacer(10 * cm, 0.5 * cm))
    elements.append(render_footer(request.build_absolute_uri(workout.get_absolute_url())))

    # write the document and send the response to the browser
    doc.build(elements)

    # Create the HttpResponse object with the appropriate PDF headers.
    response['Content-Disposition'] = 'attachment; filename=Workout-{0}-log.pdf'.format(id)
    response['Content-Length'] = len(response.content)
    return response


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
            return HttpResponseForbidden()
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

                # Process the settings
                if exercise['has_weight']:
                    setting_out = []
                    for i in exercise['setting_text'].split(u'–'):
                        setting_out.append(Paragraph(i, styleSheet["Small"], bulletText=''))
                else:
                    setting_out = Paragraph(exercise['setting_text'], styleSheet["Small"])

                data.append([set_count,
                             Paragraph(exercise['obj'].name, styleSheet["Small"]),
                             setting_out])
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
                   ('RIGHTPADDING', (0, 0), (-1, -1), 2),
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
            t._argW[1] = 10 * cm  # Exercise
            t._argW[2] = 2.5 * cm  # Repetitions

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
        elements.append(Spacer(10 * cm, 0.5 * cm))

    # Append the table
    elements.append(t)

    # Footer, date and info
    elements.append(Spacer(10 * cm, 0.5 * cm))
    created = datetime.date.today().strftime("%d.%m.%Y")
    p = Paragraph('''<para align="left">
                        %(date)s -
                        <a href="%(url)s">%(url)s</a> -
                        %(created)s
                        %(version)s
                    </para>''' %
                  {'date': _("Created on the <b>%s</b>") % created,
                   'created': "wger Workout Manager",
                   'version': get_version(),
                   'url': request.build_absolute_uri(workout.get_absolute_url()), },
                  styleSheet["Normal"])
    elements.append(p)

    # write the document and send the response to the browser
    doc.build(elements)

    # Create the HttpResponse object with the appropriate PDF headers.
    response['Content-Disposition'] = 'attachment; filename=Workout-{0}-table.pdf'.format(id)
    response['Content-Length'] = len(response.content)
    return response
