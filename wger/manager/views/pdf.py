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
import logging

# Django
from django.http import (
    HttpResponse,
    HttpResponseForbidden,
)
from django.shortcuts import get_object_or_404
from django.utils.translation import gettext as _

# Third Party
from reportlab.lib.pagesizes import (
    A4,
    landscape,
)
from reportlab.lib.units import cm
from reportlab.platypus import (
    Paragraph,
    SimpleDocTemplate,
    Spacer,
)

# wger
from wger.manager.helpers import render_workout_day
from wger.manager.models import Routine
from wger.utils.pdf import (
    get_logo,
    render_footer,
    styleSheet,
)


logger = logging.getLogger(__name__)


def workout_log(request, pk: int):
    """
    Generates a PDF with the contents of the given routine
    """

    # Load the workout
    if request.user.is_anonymous:
        return HttpResponseForbidden()
    routine = get_object_or_404(Routine, pk=pk, user=request.user)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(
        response,
        pagesize=landscape(A4),
        # pagesize = landscape(A4),
        leftMargin=cm,
        rightMargin=cm,
        topMargin=0.5 * cm,
        bottomMargin=0.5 * cm,
        title=_('Workout'),
        author='wger Workout Manager',
        subject=_('Workout for %s') % request.user.username,
    )

    # container for the 'Flowable' objects
    elements = []

    # Add site logo
    elements.append(get_logo())
    elements.append(Spacer(10 * cm, 0.5 * cm))

    # Set the title
    p = Paragraph(
        f'<para align="center"><strong>{routine.name}</strong></para>', styleSheet['HeaderBold']
    )
    elements.append(p)
    elements.append(Spacer(10 * cm, 0.5 * cm))
    if routine.description:
        p = Paragraph(f'<para align="center">{routine.description}</para>')
        elements.append(p)
        elements.append(Spacer(10 * cm, 1.5 * cm))

    # Iterate through the Workout and render the training days
    for day_data in routine.data_for_iteration():
        if day_data.day is None:
            continue
        elements.append(render_workout_day(day_data))
        elements.append(Spacer(10 * cm, 0.5 * cm))

    # Footer, date and info
    elements.append(Spacer(10 * cm, 0.5 * cm))
    elements.append(render_footer(request.build_absolute_uri(routine.get_absolute_url())))

    # write the document and send the response to the browser
    doc.build(elements)

    # Create the HttpResponse object with the appropriate PDF headers.
    response['Content-Length'] = len(response.content)
    return response


def workout_view(request, pk):
    """
    Generates a PDF with the contents of the workout, without table for logs
    """
    """
    Generates a PDF with the contents of the given workout
    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    """

    if request.user.is_anonymous:
        return HttpResponseForbidden()

    routine = get_object_or_404(Routine, pk=pk, user=request.user)

    # Create the HttpResponse object with the appropriate PDF headers.
    response = HttpResponse(content_type='application/pdf')

    # Create the PDF object, using the response object as its "file."
    doc = SimpleDocTemplate(
        response,
        pagesize=A4,
        leftMargin=cm,
        rightMargin=cm,
        topMargin=0.5 * cm,
        bottomMargin=0.5 * cm,
        title=_('Workout'),
        author='wger Workout Manager',
        subject=_('Workout for %s') % request.user.username,
    )

    # container for the 'Flowable' objects
    elements = []

    # Add site logo
    elements.append(get_logo())
    elements.append(Spacer(10 * cm, 0.5 * cm))

    # Set the title
    p = Paragraph(
        '<para align="center"><strong>%(description)s</strong></para>' % {'description': routine},
        styleSheet['HeaderBold'],
    )
    elements.append(p)
    elements.append(Spacer(10 * cm, 1.5 * cm))

    # Iterate through the Workout and render the training days
    for day_data in routine.data_for_iteration():
        if day_data.day is None:
            continue
        elements.append(render_workout_day(day_data, only_table=True))
        elements.append(Spacer(10 * cm, 0.5 * cm))

    # Footer, date and info
    elements.append(Spacer(10 * cm, 0.5 * cm))
    elements.append(render_footer(request.build_absolute_uri(routine.get_absolute_url())))

    # write the document and send the response to the browser
    doc.build(elements)

    # Create the HttpResponse object with the appropriate PDF headers.
    response['Content-Length'] = len(response.content)
    return response
