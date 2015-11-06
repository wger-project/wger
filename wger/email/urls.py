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

from django.conf.urls import url, include

from wger.email.forms import EmailListForm
from wger.email.views import gym


# sub patterns for email lists
patterns_email = [
    url(r'^overview/gym/(?P<gym_pk>\d+)$',
        gym.EmailLogListView.as_view(),
        name='overview'),
    url(r'^add/gym/(?P<gym_pk>\d+)$',
        gym.EmailListFormPreview(EmailListForm),
        name='add-gym'),
]


urlpatterns = [
    url(r'^email/', include(patterns_email, namespace="email")),
]
