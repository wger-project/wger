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


# sub patterns for workout logs
patterns_group = patterns('',
    # url(r'^(?P<pk>\d+)/view$',
    #     log.WorkoutLogDetailView.as_view(),
    #     name='log'),
    # url(r'^(?P<pk>\d+)/edit$',  # JS
    #     log.WorkoutLogUpdateView.as_view(),
    #     name='edit'),
    # url(r'^(?P<pk>\d+)/delete$',
    #     log.WorkoutLogDeleteView.as_view(),
    #     name='delete'),
    # url(r'^(?P<workout_pk>\d+)/add$',  # not used?
    #     log.WorkoutLogAddView.as_view(),
    #     name='add'),
)

urlpatterns = patterns('',
   url(r'^', include(patterns_group, namespace="group")),
)
