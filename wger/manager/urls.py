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

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from wger.manager.views import schedule
from wger.manager.views import schedule_step
from wger.manager.views import ical
from wger.manager.views import workout
from wger.manager.views import log
from wger.manager.views import set
from wger.manager.views import day
from wger.manager.views import workout_session
from wger.manager import pdf


urlpatterns = patterns('',

    # Workout
    url(r'^workout/overview$',
        workout.overview,
        name='workout-overview'),
    url(r'^workout/add$',
        workout.add,
        name='workout-add'),
    url(r'^workout/(?P<pk>\d+)/copy/$',
        workout.copy_workout,
        name='workout-copy'),
    url(r'^workout/(?P<pk>\d+)/edit/$',
        workout.WorkoutEditView.as_view(),
        name='workout-edit'),
    url(r'^workout/(?P<pk>\d+)/delete/$',
        workout.WorkoutDeleteView.as_view(),
        name='workout-delete'),
    url(r'^workout/(?P<id>\d+)/view/$',
        workout.view,
        name='workout-view'),
    url(r'^workout/(?P<pk>\d+)/log/$',
        log.WorkoutLogDetailView.as_view(),
        name='workout-log'),
    url(r'^workout/log/edit-entry/(?P<pk>\d+)$',
        log.WorkoutLogUpdateView.as_view(),
        name='workout-log-edit'),
    url(r'^workout/log/delete-entry/(?P<pk>\d+)$',
        log.WorkoutLogDeleteView.as_view(),
        name='workout-log-delete'),
    url(r'^workout/(?P<workout_pk>\d+)/log/add$',
        log.WorkoutLogAddView.as_view(),
        name='workout-log-add'),
    url(r'^workout/calendar$',
        log.calendar,
        name='workout-calendar'),
    url(r'^workout/calendar/(?P<year>\d{4})-(?P<month>\d{1,2})$',
        log.calendar,
        name='workout-calendar'),
    url(r'^workout/(?P<pk>\d+)/ical$',
        ical.export,
        name='workout-ical'),
    # PDF
    url(r'^workout/(?P<id>\d+)/pdf/log$',
         pdf.workout_log,
         name='workout-pdf-log'),
     url(r'^workout/(?P<id>\d+)/pdf/table$',
         pdf.workout_view,
         name='workout-pdf-table'),

    # Workout session
    url(r'^workout/session/(?P<workout_pk>\d+)/add/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$',
        workout_session.WorkoutSessionAddView.as_view(),
        name='workout-session-add'),
    url(r'^workout/session/(?P<pk>\d+)/edit$',
        workout_session.WorkoutSessionUpdateView.as_view(),
        name='workout-session-edit'),

    # Timer
    url(r'^workout/(?P<day_pk>\d+)/timer$',
        workout.timer,
        name='workout-timer'),

    # Schedules
    url(r'^workout/schedule/overview$',
        schedule.overview,
        name='schedule-overview'),
    url(r'^workout/schedule/add$',
        schedule.ScheduleCreateView.as_view(),
        name='schedule-add'),
    url(r'^workout/schedule/(?P<pk>\d+)/view/$',
        schedule.view,
        name='schedule-view'),
    url(r'^workout/schedule/(?P<pk>\d+)/edit/$',
        schedule.ScheduleEditView.as_view(),
        name='schedule-edit'),
    url(r'^workout/schedule/(?P<pk>\d+)/delete/$',
        schedule.ScheduleDeleteView.as_view(),
        name='schedule-delete'),
    url(r'^workout/schedule/(?P<pk>\d+)/ical$',
        ical.export_schedule,
        name='schedule-ical'),
    url(r'^workout/schedule/api/(?P<pk>\d+)/edit$',
        schedule.edit_step_api,
        name='schedule-edit-api'),

    # Schedule steps
    url(r'^workout/schedule/(?P<schedule_pk>\d+)/step/add$',
        schedule_step.StepCreateView.as_view(),
        name='step-add'),
    url(r'^workout/schedule/step/(?P<pk>\d+)/edit$',
        schedule_step.StepEditView.as_view(),
        name='step-edit'),
    url(r'^workout/schedule/step/(?P<pk>\d+)/delete$',
        schedule_step.StepDeleteView.as_view(),
        name='step-delete'),

    # Days
    url(r'^workout/day/(?P<pk>\d+)/edit/$',
        login_required(day.DayEditView.as_view()),
        name='day-edit'),
    url(r'^workout/(?P<workout_pk>\d+)/day/add/$',
        login_required(day.DayCreateView.as_view()),
        name='day-add'),
    url(r'^workout/day/(?P<pk>\d+)/delete/$',
        day.delete,
        name='day-delete'),
    url(r'^workout/day/(?P<id>\d+)/view/$',
        day.view),
    url(r'^workout/day/(?P<pk>\d+)/log/add/$',
        log.add,
        name='day-log'),

    # Sets and Settings
    url(r'^workout/day/(?P<day_pk>\d+)/set/add/$',
        set.create,
        name='set-add'),
    url(r'^workout/get-formset/(?P<exercise_pk>\d+)/(?P<reps>\d+)/',
        set.get_formset,
        name='set-get-formset'),  # Used by JS
    url(r'^workout/set/(?P<pk>\d+)/delete$',
        set.delete),
    url(r'^workout/set/(?P<pk>\d+)/edit/$',
        set.edit,
        name='set-edit'),

    # AJAX
    url(r'^workout/api/edit-set$', set.api_edit_set),
)