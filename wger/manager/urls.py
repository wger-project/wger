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
from django.views.generic import TemplateView

from wger.manager.views import schedule
from wger.manager.views import schedule_step
from wger.manager.views import ical
from wger.manager.views import workout
from wger.manager.views import log
from wger.manager.views import set
from wger.manager.views import routines
from wger.manager.views import day
from wger.manager.views import workout_session
from wger.manager import pdf

# sub patterns for workout logs
patterns_log = patterns('',
    url(r'^(?P<pk>\d+)/log/$',
        log.WorkoutLogDetailView.as_view(),
        name='log'),
    url(r'^edit-entry/(?P<pk>\d+)$',
        log.WorkoutLogUpdateView.as_view(),
        name='edit'),
    url(r'^delete-entry/(?P<pk>\d+)$',
        log.WorkoutLogDeleteView.as_view(),
        name='delete'),
    url(r'^(?P<workout_pk>\d+)/log/add$',
        log.WorkoutLogAddView.as_view(),
        name='add'),
)


# sub patterns for workouts
patterns_workout = patterns('',
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
    url(r'^(?P<id>\d+)/view/$',
        workout.view,
        name='view'),
    url(r'^calendar$',
        log.calendar,
        name='calendar'),
    url(r'^calendar/(?P<year>\d{4})-(?P<month>\d{1,2})$',
        log.calendar,
        name='calendar'),
    url(r'^(?P<pk>\d+)/ical/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        ical.export,
        name='ical'),
    url(r'^(?P<pk>\d+)/ical$',
        ical.export,
        name='ical'),
    url(r'^(?P<id>\d+)/pdf/log/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        pdf.workout_log,
        name='pdf-log'),
    url(r'^(?P<id>\d+)/pdf/log$',
        pdf.workout_log,
        name='pdf-log'),
    url(r'^(?P<id>\d+)/pdf/table/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        pdf.workout_view,
        name='pdf-table'),
    url(r'^(?P<id>\d+)/pdf/table$',
        pdf.workout_view,
        name='pdf-table'),
    url(r'^(?P<day_pk>\d+)/timer$',
        workout.timer,
        name='timer'),
)


# sub patterns for the routine generator
patterns_routines = patterns('',
    url(r'^generator$',
        routines.overview,
        name='generator'),
    url(r'^(?P<name>\w+)/pdf$',
        routines.export_pdf,
        name='pdf'),
    url(r'^(?P<name>\w+)/create-schedule$',
        routines.make_schedule,
        name='create-schedule'),
    url(r'^partials/routine-generator/detail$',
        TemplateView.as_view(template_name="routines/angular_detail.html"),
        name='partial-detail'),
    url(r'^partials/routine-generator/overview$',
        TemplateView.as_view(template_name="routines/angular_overview.html"),
        name='partial-overview'),
)


# sub patterns for workout sessions
patterns_session = patterns('',
    url(r'^(?P<workout_pk>\d+)/add/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$',
        workout_session.WorkoutSessionAddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit$',
        workout_session.WorkoutSessionUpdateView.as_view(),
        name='edit'),
)


# sub patterns for workout days
patterns_day = patterns('',
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
)

# sub patterns for workout sets
patterns_set = patterns('',
                        # Sets and Settings
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
)


# sub patterns for schedules
patterns_schedule = patterns('',
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
    url(r'^(?P<pk>\d+)/pdf/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        schedule.export_pdf,
        name='pdf'),
    url(r'^(?P<pk>\d+)/pdf$',
        schedule.export_pdf,
        name='pdf'),
)



# sub patterns for schedule steps
patterns_step = patterns('',
    url(r'^(?P<schedule_pk>\d+)/step/add$',
        schedule_step.StepCreateView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit$',
        schedule_step.StepEditView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete$',
        schedule_step.StepDeleteView.as_view(),
        name='delete'),
)



urlpatterns = patterns('',
   url(r'^', include(patterns_workout, namespace="workout")),
   url(r'^routine/', include(patterns_routines, namespace="routine")),

   url(r'^log/', include(patterns_log, namespace="log")),
   url(r'^day/', include(patterns_day, namespace="day")),
   url(r'^set/', include(patterns_set, namespace="set")),
   url(r'^session/', include(patterns_session, namespace="session")),
   url(r'^schedule/', include(patterns_schedule, namespace="schedule")),
   url(r'^schedule/step/', include(patterns_step, namespace="step")),
)
