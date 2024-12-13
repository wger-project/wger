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
from django.urls import (
    path,
    re_path,
)

# wger
from wger.core.views.react import ReactView
from wger.manager.views import (
    ical,
    pdf,
    routine,
    workout,
)

# sub patterns for workout logs
patterns_log = [
    path(
        '<int:pk>/view',
        ReactView.as_view(login_required=True),
        name='log',
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

# sub patterns for days
patterns_days = [
    path(
        '<int:day_pk>/add-logs',
        ReactView.as_view(),
        name='overview',
    ),
]

# sub patterns for workouts
patterns_workout = [
    path(
        '<int:pk>/make-template',
        workout.WorkoutMarkAsTemplateView.as_view(),
        name='make-template',
    ),
    path(
        'calendar',
        ReactView.as_view(login_required=True),
        name='calendar',
    ),
    path(
        '<int:pk>/ical',
        ical.export,
        name='ical',
    ),
]

# sub patterns for workouts
patterns_routine = [
    path(
        'overview',
        ReactView.as_view(login_required=True),
        name='overview',
    ),
    path(
        'add',
        ReactView.as_view(login_required=True),
        name='add',
    ),
    path(
        '<int:pk>/view',
        ReactView.as_view(login_required=True),
        name='view',
    ),
    path(
        '<int:pk>/copy',
        routine.copy_routine,
        name='copy',
    ),
    path(
        '<int:pk>/pdf/log',
        pdf.workout_log,
        name='pdf-log',
    ),
    path(
        '<int:pk>/pdf/table',
        pdf.workout_view,
        name='pdf-table',
    ),
]

urlpatterns = [
    path('', include((patterns_workout, 'workout'), namespace='workout')),
    path('', include((patterns_routine, 'routine'), namespace='routine')),
    path('template/', include((patterns_templates, 'template'), namespace='template')),
    path('<int:routine_pk>/day/', include((patterns_days, 'day'), namespace='day')),
    path('log/', include((patterns_log, 'log'), namespace='log')),
]
