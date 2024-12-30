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
from django.conf.urls import include
from django.contrib.auth.decorators import login_required
from django.urls import (
    path,
    re_path,
)

# wger
from wger.core.views.react import ReactView
from wger.manager.views import (
    day,
    ical,
    log,
    pdf,
    schedule,
    schedule_step,
    set,
    workout,
    workout_session,
)


# sub patterns for workout logs
patterns_log = [
    path(
        '<int:pk>/view',
        ReactView.as_view(login_required=True),
        name='log',
    ),
    path(
        '<int:pk>/edit',  # JS
        log.WorkoutLogUpdateView.as_view(),
        name='edit',
    ),
    path(
        '<int:pk>/delete',
        log.WorkoutLogDeleteView.as_view(),
        name='delete',
    ),
]

# sub patterns for templates
patterns_templates = [
    path(
        'overview',
        workout.template_overview,
        name='overview',
    ),
    path(
        'public',
        workout.public_template_overview,
        name='public',
    ),
    path(
        '<int:pk>/view',
        workout.template_view,
        name='view',
    ),
    path(
        '<int:pk>/make-workout',
        workout.make_workout,
        name='make-workout',
    ),
]

# sub patterns for workouts
patterns_workout = [
    path(
        'overview',
        ReactView.as_view(login_required=True),
        name='overview',
    ),
    path(
        'add',
        workout.add,
        name='add',
    ),
    path(
        '<int:pk>/copy',
        workout.copy_workout,
        name='copy',
    ),
    path(
        '<int:pk>/edit',
        workout.WorkoutEditView.as_view(),
        name='edit',
    ),
    path(
        '<int:pk>/make-template',
        workout.WorkoutMarkAsTemplateView.as_view(),
        name='make-template',
    ),
    path(
        '<int:pk>/delete',
        workout.WorkoutDeleteView.as_view(),
        name='delete',
    ),
    path(
        '<int:pk>/view',
        # ReactView.as_view(login_required=True),
        workout.view,
        name='view',
    ),
    path(
        'calendar',
        ReactView.as_view(login_required=True),
        name='calendar',
    ),
    re_path(
        r'^(?P<pk>\d+)/ical/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        ical.export,
        name='ical',
    ),
    path(
        '<int:pk>/ical',
        ical.export,
        name='ical',
    ),
    re_path(
        r'^(?P<id>\d+)/pdf/log/(?P<images>[01]+)/(?P<comments>[01]+)/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        pdf.workout_log,
        name='pdf-log',
    ),  # JS!
    re_path(
        r'^(?P<id>\d+)/pdf/log/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        pdf.workout_log,
        name='pdf-log',
    ),
    re_path(
        r'^(?P<id>\d+)/pdf/log/(?P<images>[01]+)/(?P<comments>[01]+)$',
        pdf.workout_log,
        name='pdf-log',
    ),
    path(
        '<int:id>/pdf/log',
        pdf.workout_log,
        name='pdf-log',
    ),
    re_path(
        r'^(?P<id>\d+)/pdf/table/(?P<images>[01]+)/(?P<comments>[01]+)/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        pdf.workout_view,
        name='pdf-table',
    ),  # JS!
    re_path(
        r'^(?P<id>\d+)/pdf/table/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        pdf.workout_view,
        name='pdf-table',
    ),
    re_path(
        r'^(?P<id>\d+)/pdf/table/(?P<images>[01]+)/(?P<comments>[01]+)$',
        pdf.workout_view,
        name='pdf-table',
    ),
    path(
        '<int:id>/pdf/table',
        pdf.workout_view,
        name='pdf-table',
    ),
]

# sub patterns for workout sessions
patterns_session = [
    re_path(
        r'^(?P<workout_pk>\d+)/add/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$',
        workout_session.WorkoutSessionAddView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>/edit',
        workout_session.WorkoutSessionUpdateView.as_view(),
        name='edit',
    ),
    re_path(
        r'^(?P<pk>\d+)/delete/(?P<logs>session|logs)?$',
        workout_session.WorkoutSessionDeleteView.as_view(),
        name='delete',
    ),
]

# sub patterns for workout days
patterns_day = [
    path(
        '<int:pk>/edit',
        login_required(day.DayEditView.as_view()),
        name='edit',
    ),
    path(
        '<int:workout_pk>/add',
        login_required(day.DayCreateView.as_view()),
        name='add',
    ),
    path(
        '<int:pk>/delete',
        day.delete,
        name='delete',
    ),
    path(
        '<int:pk>/log/add',
        log.add,
        name='log',
    ),
]

# sub patterns for workout sets
patterns_set = [
    path(
        '<int:day_pk>/add',
        set.create,
        name='add',
    ),
    path(
        'get-formset/<int:base_pk>/<int:reps>',
        set.get_formset,
        name='get-formset',
    ),  # Used by JS
    path(
        '<int:pk>/delete',
        set.delete,
        name='delete',
    ),
    path(
        '<int:pk>/edit',
        set.edit,
        name='edit',
    ),
]

# sub patterns for schedules
patterns_schedule = [
    path(
        'overview',
        schedule.overview,
        name='overview',
    ),
    path(
        'add',
        schedule.ScheduleCreateView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>/view',
        schedule.view,
        name='view',
    ),
    path(
        '<int:pk>/start',
        schedule.start,
        name='start',
    ),
    path(
        '<int:pk>/edit',
        schedule.ScheduleEditView.as_view(),
        name='edit',
    ),
    path(
        '<int:pk>/delete',
        schedule.ScheduleDeleteView.as_view(),
        name='delete',
    ),
    re_path(
        r'^(?P<pk>\d+)/ical/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        ical.export_schedule,
        name='ical',
    ),
    path(
        '<int:pk>/ical',
        ical.export_schedule,
        name='ical',
    ),
    re_path(
        r'^(?P<pk>\d+)/pdf/log/(?P<images>[01]+)/(?P<comments>[01]+)/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        schedule.export_pdf_log,
        name='pdf-log',
    ),  # JS!
    re_path(
        r'^(?P<pk>\d+)/pdf/log/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        schedule.export_pdf_log,
        name='pdf-log',
    ),
    re_path(
        r'^(?P<pk>\d+)/pdf/log/(?P<images>[01]+)/(?P<comments>[01]+)$',
        schedule.export_pdf_log,
        name='pdf-log',
    ),
    path(
        '<int:pk>/pdf/log',
        schedule.export_pdf_log,
        name='pdf-log',
    ),
    re_path(
        r'^(?P<pk>\d+)/pdf/table/(?P<images>[01]+)/(?P<comments>[01]+)/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        schedule.export_pdf_table,
        name='pdf-table',
    ),  # JS!
    re_path(
        r'^(?P<pk>\d+)/pdf/table/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})$',
        schedule.export_pdf_table,
        name='pdf-table',
    ),
    re_path(
        r'^(?P<pk>\d+)/pdf/table/(?P<images>[01]+)/(?P<comments>[01]+)$',
        schedule.export_pdf_table,
        name='pdf-table',
    ),
    path(
        '<int:pk>/pdf/table',
        schedule.export_pdf_table,
        name='pdf-table',
    ),
]

# sub patterns for schedule steps
patterns_step = [
    path(
        '<int:schedule_pk>/step/add',
        schedule_step.StepCreateView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>/edit',
        schedule_step.StepEditView.as_view(),
        name='edit',
    ),
    path(
        '<int:pk>/delete',
        schedule_step.StepDeleteView.as_view(),
        name='delete',
    ),
]

urlpatterns = [
    path('', include((patterns_workout, 'workout'), namespace='workout')),
    path('template/', include((patterns_templates, 'template'), namespace='template')),
    path('log/', include((patterns_log, 'log'), namespace='log')),
    path('day/', include((patterns_day, 'day'), namespace='day')),
    path('set/', include((patterns_set, 'set'), namespace='set')),
    path('session/', include((patterns_session, 'session'), namespace='session')),
    path('schedule/', include((patterns_schedule, 'schedule'), namespace='schedule')),
    path('schedule/step/', include((patterns_step, 'step'), namespace='step')),
]
