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

from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from wger.manager.views import (
    pdf,
    schedule,
    schedule_step,
    ical,
    workout,
    log,
    set,
    day,
    workout_session
)

# sub patterns for workout logs
patterns_log = [
    url(r'^(?P<pk>\d+)/view$',
        log.WorkoutLogDetailView.as_view(),
        name='log'),
    url(r'^(?P<pk>\d+)/edit$',  # JS
        log.WorkoutLogUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete$',
        log.WorkoutLogDeleteView.as_view(),
        name='delete')
]


# sub patterns for workouts
patterns_workout = [
    url(r'^overview$',
        workout.overview,
        name='overview'),
    url(r'^add$',
        workout.add,
        name='add'),
    url(r'^(?P<pk>\d+)/copy/$',
        workout.copy_workout,
        name='copy'),
    url(r'^(?P<pk>\d+)/edit/$',
        workout.WorkoutEditView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete/$',
        workout.WorkoutDeleteView.as_view(),
        name='delete'),
    url(r'^(?P<pk>\d+)/view/$',
        workout.view,
        name='view'),
    url(r'^calendar/(?P<username>[\w.@+-]+)$',
        log.calendar,
        name='calendar'),
    url(r'^calendar$',
        log.calendar,
        name='calendar'),
    url(r'^calendar/(?P<username>[\w.@+-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})$',
        log.calendar,
        name='calendar'),
    url(r'^calendar/(?P<year>\d{4})/(?P<month>\d{1,2})$',
        log.calendar,
        name='calendar'),
    url(r'^calendar/(?P<username>[\w.@+-]+)/(?P<year>\d{4})/(?P<month>\d{1,2})/(?P<day>\d{1,2})$',
        log.day,
        name='calendar-day'),
    url(r'^(?P<pk>\d+)/ical/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        ical.export,
        name='ical'),
    url(r'^(?P<pk>\d+)/ical$',
        ical.export,
        name='ical'),
    url(r'^(?P<id>\d+)/pdf/log/(?P<images>[01]+)/(?P<comments>[01]+)/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        pdf.workout_log,
        name='pdf-log'), #JS!
    url(r'^(?P<id>\d+)/pdf/log/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        pdf.workout_log,
        name='pdf-log'),
    url(r'^(?P<id>\d+)/pdf/log/(?P<images>[01]+)/(?P<comments>[01]+)$',
        pdf.workout_log,
        name='pdf-log'),
    url(r'^(?P<id>\d+)/pdf/log$',
        pdf.workout_log,
        name='pdf-log'),
    url(r'^(?P<id>\d+)/pdf/table/(?P<images>[01]+)/(?P<comments>[01]+)/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        pdf.workout_view,
        name='pdf-table'), #JS!
    url(r'^(?P<id>\d+)/pdf/table/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        pdf.workout_view,
        name='pdf-table'),
    url(r'^(?P<id>\d+)/pdf/table/(?P<images>[01]+)/(?P<comments>[01]+)$',
        pdf.workout_view,
        name='pdf-table'),
    url(r'^(?P<id>\d+)/pdf/table$',
        pdf.workout_view,
        name='pdf-table'),
    url(r'^(?P<day_pk>\d+)/timer$',
        workout.timer,
        name='timer'),
]


# sub patterns for workout sessions
patterns_session = [
    url(r'^(?P<workout_pk>\d+)/add/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$',
        workout_session.WorkoutSessionAddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit$',
        workout_session.WorkoutSessionUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete/(?P<logs>(session|logs))?$',
        workout_session.WorkoutSessionDeleteView.as_view(),
        name='delete'),
]


# sub patterns for workout days
patterns_day = [
    url(r'^(?P<pk>\d+)/edit/$',
        login_required(day.DayEditView.as_view()),
        name='edit'),
    url(r'(?P<workout_pk>\d+)/day/add/$',
        login_required(day.DayCreateView.as_view()),
        name='add'),
    url(r'(?P<pk>\d+)/delete/$',
        day.delete,
        name='delete'),
    url(r'^(?P<id>\d+)/view/$',
        day.view,
        name='view'),
    url(r'^(?P<pk>\d+)/log/add/$',
        log.add,
        name='log'),
]

# sub patterns for workout sets
patterns_set = [
    url(r'^day/(?P<day_pk>\d+)/set/add/$',
        set.create,
        name='add'),
    url(r'^get-formset/(?P<exercise_pk>\d+)/(?P<reps>\d+)/',
        set.get_formset,
        name='get-formset'),  # Used by JS
    url(r'^(?P<pk>\d+)/delete$',
        set.delete,
        name='delete'),
    url(r'^(?P<pk>\d+)/edit/$',
        set.edit,
        name='edit'),
]


# sub patterns for schedules
patterns_schedule = [
    url(r'^overview$',
        schedule.overview,
        name='overview'),
    url(r'^add$',
        schedule.ScheduleCreateView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/view/$',
        schedule.view,
        name='view'),
    url(r'^(?P<pk>\d+)/start$',
        schedule.start,
        name='start'),
    url(r'^(?P<pk>\d+)/edit/$',
        schedule.ScheduleEditView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete/$',
        schedule.ScheduleDeleteView.as_view(),
        name='delete'),
    url(r'^(?P<pk>\d+)/ical/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        ical.export_schedule,
        name='ical'),
    url(r'^(?P<pk>\d+)/ical$',
        ical.export_schedule,
        name='ical'),

    url(
        r'^(?P<pk>\d+)/pdf/log/(?P<images>[01]+)/(?P<comments>[01]+)/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        schedule.export_pdf_log,
        name='pdf-log'),  # JS!
    url(r'^(?P<pk>\d+)/pdf/log/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        schedule.export_pdf_log,
        name='pdf-log'),
    url(r'^(?P<pk>\d+)/pdf/log/(?P<images>[01]+)/(?P<comments>[01]+)$',
        schedule.export_pdf_log,
        name='pdf-log'),
    url(r'^(?P<pk>\d+)/pdf/log$',
        schedule.export_pdf_log,
        name='pdf-log'),
    url(
        r'^(?P<pk>\d+)/pdf/table/(?P<images>[01]+)/(?P<comments>[01]+)/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        schedule.export_pdf_table,
        name='pdf-table'),  # JS!
    url(r'^(?P<pk>\d+)/pdf/table/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        schedule.export_pdf_table,
        name='pdf-table'),
    url(r'^(?P<pk>\d+)/pdf/table/(?P<images>[01]+)/(?P<comments>[01]+)$',
        schedule.export_pdf_table,
        name='pdf-table'),
    url(r'^(?P<pk>\d+)/pdf/table$',
        schedule.export_pdf_table,
        name='pdf-table'),
]


# sub patterns for schedule steps
patterns_step = [
    url(r'^(?P<schedule_pk>\d+)/step/add$',
        schedule_step.StepCreateView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit$',
        schedule_step.StepEditView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete$',
        schedule_step.StepDeleteView.as_view(),
        name='delete'),
]



urlpatterns = [
   url(r'^', include(patterns_workout, namespace="workout")),
   url(r'^log/', include(patterns_log, namespace="log")),
   url(r'^day/', include(patterns_day, namespace="day")),
   url(r'^set/', include(patterns_set, namespace="set")),
   url(r'^session/', include(patterns_session, namespace="session")),
   url(r'^schedule/', include(patterns_schedule, namespace="schedule")),
   url(r'^schedule/step/', include(patterns_step, namespace="step")),
]
