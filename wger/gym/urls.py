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


from django.conf.urls import patterns, url, include

from wger.gym.views import gym
from wger.gym.views import config
from wger.gym.views import admin_config
from wger.gym.views import user_config


# 'sub patterns' for gyms
patterns_gym = patterns('',
    url(r'^list$',
        gym.GymListView.as_view(),
        name='list'),
    url(r'^new-user-data/view$',
        gym.gym_new_user_info,
        name='new-user-data'),
    url(r'^new-user-data/export$',
        gym.gym_new_user_info_export,
        name='new-user-data-export'),
    url(r'^(?P<pk>\d+)/members$',
        gym.GymUserListView.as_view(),
        name='user-list'),
    url(r'^(?P<gym_pk>\d+)/add-member$',
        gym.GymAddUserView.as_view(),
        name='add-user'),
    url(r'^add$',
        gym.GymAddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit$',
        gym.GymUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete$',
        gym.GymDeleteView.as_view(),
        name='delete'),
)

# 'sub patterns' for gym config
patterns_gymconfig = patterns('',
    url(r'^(?P<pk>\d+)/edit$',
        config.GymConfigUpdateView.as_view(),
        name='edit'),
)


# 'sub patterns' for gym admin config
patterns_adminconfig = patterns('',
    url(r'^(?P<pk>\d+)/edit$',
        admin_config.ConfigUpdateView.as_view(),
        name='edit'),
)

# 'sub patterns' for gym user config
patterns_userconfig = patterns('',
    url(r'^(?P<pk>\d+)/edit$',
        user_config.ConfigUpdateView.as_view(),
        name='edit'),
)

#
# All patterns for this app
#
urlpatterns = patterns('',

    url(r'^', include(patterns_gym, namespace="gym")),
    url(r'^config/', include(patterns_gymconfig, namespace="config")),
    url(r'^admin-config/', include(patterns_adminconfig, namespace="admin_config")),
    url(r'^user-config/', include(patterns_userconfig, namespace="user_config")),
)
