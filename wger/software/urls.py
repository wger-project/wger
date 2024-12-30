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
from django.urls import path
from django.views.generic import (
    RedirectView,
    TemplateView,
)

# wger
from wger import get_version
from wger.software import views


urlpatterns = [
    path(
        'terms-of-service',
        TemplateView.as_view(template_name='tos.html'),
        name='tos',
    ),
    path(
        'features',
        views.features,
        name='features',
    ),
    path(
        'code',
        RedirectView.as_view(permanent=True, url='https://github.com/wger-project/wger'),
        name='code',
    ),
    path(
        'about-us',
        TemplateView.as_view(
            template_name='about_us.html', extra_context={'version': get_version()}
        ),
        name='about-us',
    ),
    path(
        'api',
        TemplateView.as_view(template_name='api.html'),
        name='api',
    ),
]
