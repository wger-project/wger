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

from wger.groups.views import group
from wger.groups.views import membership


# sub patterns for groups
patterns_group = patterns('',
    url(r'^list$',
        group.ListView.as_view(),
        name='list'),
    url(r'^add$',
        group.AddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/view$',
        group.DetailView.as_view(),
        name='view'),
    url(r'^(?P<pk>\d+)/edit$',
        group.UpdateView.as_view(),
        name='edit'),
)

# sub patterns for group memberships
patterns_membership = patterns('',
    url(r'^(?P<group_pk>\d+)/join$',
        membership.join_public_group,
        name='join-public'),
    url(r'^(?P<group_pk>\d+)/leave$',
        membership.leave_group,
        name='leave'),
    url(r'^(?P<group_pk>\d+)/(?P<user_pk>\d+)/promote$',
        membership.make_admin,
        name='promote'),
)

urlpatterns = patterns('',
   url(r'^', include(patterns_group, namespace="group")),
   url(r'^', include(patterns_membership, namespace="member")),
)
