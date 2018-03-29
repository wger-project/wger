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

# Third Party
from django.http import (
    HttpResponse,
    HttpResponseForbidden
)
from django.shortcuts import get_object_or_404
from django.utils.translation import ugettext as _


# wger
from wger.manager.helpers import render_workout_day
from wger.manager.models import Workout
from wger.utils.helpers import check_token
from wger.utils.json import (
    render_header,
    render_JSON
)


logger = logging.getLogger(__name__)


def workout_log(request, id, comments=False, uidb64=None, token=None):
    print("in json.workout_log...")
    '''
    Generates a JSON with the contents of the given workout
    '''

    comments = bool(int(comments))

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

    # Create the HttpResponse object with the appropriate JSON headers.
    response = HttpResponse(content_type='application/json')

    # Create the JSON object, using the response object as its "file."
    # FIXME: make JSON
    json_obj = render_JSON(comments=comments,
                           uidb64=uidb64,
                           token=token)
    print("json_obj =", json_obj)
    # doc = SimpleDocTemplate(response,
    #                         pagesize=A4,
    #                         # pagesize = landscape(A4),
    #                         leftMargin=cm,
    #                         rightMargin=cm,
    #                         topMargin=0.5 * cm,
    #                         bottomMargin=0.5 * cm,
    #                         title=_('Workout'),
    #                         author='wger Workout Manager',
    #                         subject=_('Workout for %s') % request.user.username)

    # container for the 'Flowable' objects
    # elements = []

    # # Set the title
    # # p = Paragraph('<para align="center"><strong>%(description)s</strong></para>' %
    # #               {'description': workout},
    # #               styleSheet["HeaderBold"])
    # # elements.append(p)
    # elements.append(Spacer(10 * cm, 0.5 * cm))

    # # Iterate through the Workout and render the training days
    # for day in workout.canonical_representation['day_list']:
    #     elements.append(render_workout_day(day, images=images, comments=comments))
    #     elements.append(Spacer(10 * cm, 0.5 * cm))

    # # Footer, date and info
    # elements.append(Spacer(10 * cm, 0.5 * cm))
    # elements.append(render_footer(request.build_absolute_uri(workout.get_absolute_url())))

    # # write the document and send the response to the browser
    # doc.build(elements) 

    # Create the HttpResponse object with the appropriate JSON headers.
    response = HttpResponse(json_obj, content_type='application/json')
    response['Content-Disposition'] = 'attachment; filename=Workout-{0}.json'.format(id)
    response['Content-Length'] = len(response.content)
    return response
