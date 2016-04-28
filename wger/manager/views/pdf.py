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


def workout_log(request, id, images=False, comments=False, uidb64=None, token=None):
    '''
    Generates a PDF with the contents of the given workout

    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    '''
    comments = bool(int(comments))
    images = bool(int(images))

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
        elements.append(render_workout_day(day, images=images, comments=comments))
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


def workout_view(request, id, images=False, comments=False, uidb64=None, token=None):
    '''
    Generates a PDF with the contents of the workout, without table for logs
    '''

    '''
    Generates a PDF with the contents of the given workout
    See also
    * http://www.blog.pythonlibrary.org/2010/09/21/reportlab
    * http://www.reportlab.com/apis/reportlab/dev/platypus.html
    '''
    comments = bool(int(comments))
    images = bool(int(images))

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
        elements.append(render_workout_day(day, images=images, comments=comments, only_table=True))
        elements.append(Spacer(10 * cm, 0.5 * cm))

    # Footer, date and info
    elements.append(Spacer(10 * cm, 0.5 * cm))
    elements.append(render_footer(request.build_absolute_uri(workout.get_absolute_url())))

    # write the document and send the response to the browser
    doc.build(elements)

    # Create the HttpResponse object with the appropriate PDF headers.
    response['Content-Disposition'] = 'attachment; filename=Workout-{0}-table.pdf'.format(id)
    response['Content-Length'] = len(response.content)
    return response
