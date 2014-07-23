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

from django.http import HttpResponseNotFound, HttpResponse
from django.utils.translation import ugettext as _
from django.shortcuts import render

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate
from reportlab.platypus import KeepTogether
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer

from rest_framework.reverse import reverse
from wger.manager.forms import RoutineSettingsForm
from wger.manager.routines.helpers import render_routine_week

from wger.manager.routines import routines
from wger.utils.pdf import styleSheet
from wger.utils.pdf import render_footer


logger = logging.getLogger('wger.custom')


def overview(request):
    '''
    An overview of all the available routines
    '''
    form = RoutineSettingsForm

    context = {'routines': routines,
               'form': form}
    return render(request, 'routines/overview.html', context)


def detail(request, name):
    '''
    Detail view for a routine
    '''

    context = {}
    try:
        context['routine'] = routines[name]
    except KeyError:
        return HttpResponseNotFound()

    return render(request, 'routines/detail.html', context)


def export_pdf(request, name):
    '''
    Exports a routine as a PDF
    '''
    try:
        routine = routines[name]
    except KeyError:
        return HttpResponseNotFound()

    response = HttpResponse(content_type='application/pdf')
    doc = SimpleDocTemplate(response,
                            pagesize=A4,
                            leftMargin=cm,
                            rightMargin=cm,
                            topMargin=1 * cm,
                            title=routine.name,
                            author='wger Workout Manager',
                            subject=routine.description)
    elements = []
    p = Paragraph('<para align="center">{0}</para>'.format(routine.name),
                  styleSheet["HeaderBold"])
    elements.append(p)
    elements.append(Spacer(10*cm, 0.5*cm))
    p = Paragraph('<para align="center">{0}</para>'.format(routine.description),
                  styleSheet["SubHeader"])
    elements.append(p)
    elements.append(Spacer(10*cm, 0.5*cm))

    # Process the routine
    tmp = {}
    for config in routine:
        if not tmp.get(config['week']):
            tmp[config['week']] = []

        tmp[config['week']].append(config)

    for week in tmp:
        p = Paragraph('<para>{0} {1}</para>'.format(_("Week"), week), styleSheet["Bold"])
        t = render_routine_week(tmp[week])
        s = Spacer(10*cm, 0.5*cm)
        elements.append(KeepTogether([p, t, s]))

    # Footer
    elements.append(Spacer(10*cm, 0.5*cm))
    url = reverse('routines-detail', kwargs={'name': routine.short_name})
    elements.append(render_footer(request.build_absolute_uri(url)))

    # Create the HttpResponse object with the appropriate PDF headers.
    doc.build(elements)
    filename = 'Routine-{0}.pdf'.format(routine.short_name)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    response['Content-Length'] = len(response.content)
    return response
