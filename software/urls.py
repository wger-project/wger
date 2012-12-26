# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

from django.conf.urls import patterns, url

from django.views.generic import TemplateView


from software.views import IssuesTemplateView

urlpatterns = patterns('',

    url(r'^issues$',
        IssuesTemplateView.as_view(),
        name='issues'),

    url(r'^features$',
        TemplateView.as_view(template_name="functions.html"),
        name='functions'),

    url(r'^changelog$',
        TemplateView.as_view(template_name="changelog.html"),
        name='changelog'),

    url(r'^license$',
        TemplateView.as_view(template_name="license.html"),
        name='license'),

    url(r'^code$',
        TemplateView.as_view(template_name="code.html"),
        name='code'),
)
