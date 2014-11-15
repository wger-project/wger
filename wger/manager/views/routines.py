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

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import cm
from reportlab.platypus import SimpleDocTemplate, Table
from reportlab.platypus import KeepTogether
from reportlab.platypus import Paragraph
from reportlab.platypus import Spacer

from django.http import HttpResponseNotFound
from django.http import HttpResponse
from django.http import HttpResponseRedirect
from django.utils.translation import ugettext as _
from django.shortcuts import render
from django.contrib.auth.decorators import login_required

from rest_framework.reverse import reverse

from wger.core.models import DaysOfWeek
from wger.manager.models import Workout
from wger.manager.models import WeightConfig
from wger.manager.models import Day
from wger.manager.models import Set
from wger.manager.models import Setting
from wger.manager.models import Schedule
from wger.manager.models import ScheduleStep
from wger.manager.routines.helpers import render_routine_week
from wger.manager import routines

from wger.utils.language import load_language
from wger.utils.pdf import styleSheet
from wger.utils.pdf import render_footer


logger = logging.getLogger('wger.custom')


def overview(request):
    '''
    Render the routine generator overview page
    '''

    context = {'ng_app': 'routineGenerator',
               'user_config': request.session.get('routine_config')}

    return render(request, 'routines/overview.html', context)


@login_required
def make_schedule(request, name):
    '''
    Creates a schedule out of a routine
    '''

    user_config = request.session['routine_config']

    try:
        routine = routines.get_routines()[name]
        routine.set_user_config(user_config)
    except KeyError:
        return HttpResponseNotFound()

    schedule = Schedule()
    schedule.user = request.user
    schedule.name = routine.name
    schedule.start_date = datetime.date.today()
    schedule.is_active = True
    schedule.is_loop = False
    schedule.save()

    current_week = 0
    current_day = 0
    for config in routine:
        if config['week'] != current_week:
            current_day = 0
            current_week = config['week']

            workout = Workout()
            workout.user = request.user
            workout.comment = _('Week {0} of {1}'.format(current_week, routine.name))
            workout.save()

            step = ScheduleStep()
            step.schedule = schedule
            step.workout = workout
            step.duration = 1
            step.order = 1
            step.save()

        if config['day'] != current_day:
            current_day = config['day']

            day = Day()
            day.training = workout
            day.description = _('Day {0}'.format(current_day))
            day.save()

            day_of_week = DaysOfWeek.objects.get(pk=current_day)
            day.day.add(day_of_week)
            day.save()

        set = Set()
        set.exerciseday = day
        set.sets = config['sets']
        set.save()

        # Some monkeying around to get the exercise PK for our language
        mapper = config['exercise'].exercise_mapper
        language = load_language()
        languages = mapper.get_all_languages()
        try:
            exercise = languages[language.short_name]
        except KeyError:
            exercise = languages['en']

        set.exercises.add(exercise)

        setting = Setting()
        setting.set = set
        setting.exercise = exercise
        setting.reps = config['reps']
        setting.order = 1
        setting.save()

        weight_config = WeightConfig()
        weight_config.schedule_step = step
        weight_config.setting = setting

        # Take care of the special weight values
        if config['weight'] == 'auto':
            weight_config.start = 0
        elif config['weight'] == 'max':
            weight_config.start = 0
        else:
            weight_config.start = config['weight']
        weight_config.increment = 0
        weight_config.save()

    return HttpResponseRedirect(reverse('schedule-view',
                                        kwargs={'pk': schedule.id}))


def export_pdf(request, name):
    '''
    Exports a routine as a PDF
    '''

    user_config = request.session['routine_config']
    try:
        routine = routines.get_routines()[name]
        routine.set_user_config(user_config)
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

    # Config data
    data = []
    p = Paragraph('<para>{0}</para>'.format(_("Routine configuration")), styleSheet["Bold"])
    data.append([p])
    data.append([_('Max Bench'), user_config['max_bench']])
    data.append([_('Max Squat'), user_config['max_squat']])
    data.append([_('Max Deadlift'), user_config['max_deadlift']])
    data.append([_('Weights rounded to'), user_config['round_to']])
    table_style = [('FONT', (0, 0), (-1, -1), 'OpenSans')]
    t = Table(data, style=table_style, hAlign='LEFT')
    t._argW[0] = 5 * cm
    elements.append(t)

    # Footer
    elements.append(Spacer(10*cm, 0.5*cm))
    url = reverse('routines-generator')
    elements.append(render_footer(request.build_absolute_uri(url)))

    # Create the HttpResponse object with the appropriate PDF headers.
    doc.build(elements)
    filename = 'Routine-{0}.pdf'.format(routine.slug)
    response['Content-Disposition'] = 'attachment; filename={0}'.format(filename)
    response['Content-Length'] = len(response.content)
    return response
