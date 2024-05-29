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

# Django
from django.conf.urls import include
from django.urls import path

# wger
from wger.mailer.forms import EmailListForm
from wger.mailer.views import gym


# sub patterns for email lists
patterns_email = [
    path(
        'overview/gym/<int:gym_pk>',
        gym.EmailLogListView.as_view(),
        name='overview',
    ),
    path(
        'add/gym/<int:gym_pk>',
        gym.EmailListFormPreview(EmailListForm),
        name='add-gym',
    ),
]

urlpatterns = [
    path('', include((patterns_email, 'email'), namespace='email')),
]
