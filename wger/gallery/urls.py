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
from wger.gallery.views import images


# 'sub patterns' for gyms
patterns_images = [
    path(
        'overview',
        images.overview,
        name='overview',
    ),
    path(
        '<int:pk>/edit',
        images.ImageUpdateView.as_view(),
        name='edit',
    ),
    path(
        'add',
        images.ImageAddView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>/delete',
        images.ImageDeleteView.as_view(),
        name='delete',
    ),
]

#
# All patterns for this app
#
urlpatterns = [
    path('', include((patterns_images, 'images'), namespace='images')),
]
