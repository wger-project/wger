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
from django.urls import path

# wger
from wger.core.views.react import ReactView
from wger.manager.views import (
    ical,
    pdf,
    routine,
    timer,
)


# sub patterns for templates
patterns_templates = [
    path(
        'overview/private',
        ReactView.as_view(login_required=True),
        name='overview',
    ),
    path(
        'overview/public',
        ReactView.as_view(login_required=True),
        name='public',
    ),
    path(
        '<int:pk>/view',
        ReactView.as_view(login_required=True),
        name='view',
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

# sub patterns for routines
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
        '<int:pk>/edit',
        ReactView.as_view(login_required=True),
        name='edit',
    ),
    path(
        '<int:pk>/edit/progression/<int:progression_pk>',
        ReactView.as_view(login_required=True),
        name='edit-progression',
    ),
    path(
        '<int:pk>/statistics',
        ReactView.as_view(login_required=True),
        name='statistics',
    ),
    path(
        '<int:pk>/logs',
        ReactView.as_view(login_required=True),
        name='logs',
    ),
    path(
        '<int:pk>/view',
        ReactView.as_view(login_required=True),
        name='view',
    ),
    path(
        '<int:pk>/table',
        ReactView.as_view(login_required=True),
        name='table',
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
    path(
        '<int:pk>/ical',
        ical.export,
        name='ical',
    ),
    path(
        'calendar',
        ReactView.as_view(login_required=True),
        name='calendar',
    ),
]

urlpatterns = [
    path('', include((patterns_routine, 'routine'), namespace='routine')),
    path('templates/', include((patterns_templates, 'template'), namespace='template')),
    path('<int:routine_pk>/day/', include((patterns_days, 'day'), namespace='day')),
    path('timer-demo/', timer.timer_demo, name='timer-demo'),
    path('add-timed-exercise/', timer.add_timed_exercise, name='add-timed-exercise'),
    path('api/days/<int:routine_id>/', timer.get_days_for_routine, name='api-days'),
]
