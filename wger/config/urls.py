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

from django.conf.urls import patterns, url

from wger.config.views import languages
from wger.config.views import language_config
from wger.config.views import gym_config


urlpatterns = patterns('',

   # Languages
   url(r'^language/list$',
        languages.LanguageListView.as_view(),
        name='language-overview'),
   url(r'^language/(?P<pk>\d+)/view$',
        languages.LanguageDetailView.as_view(),
        name='language-view'),
   url(r'^language/(?P<pk>\d+)/delete$',
        languages.LanguageDeleteView.as_view(),
        name='language-delete'),
   url(r'^language/(?P<pk>\d+)/edit',
        languages.LanguageEditView.as_view(),
        name='language-edit'),
   url(r'^language/add$',
        languages.LanguageCreateView.as_view(),
        name='language-add'),

   # Language configs
   url(r'^language-config/(?P<pk>\d+)/edit',
       language_config.LanguageConfigUpdateView.as_view(),
       name='languageconfig-edit'),

   # Gym config
   url(r'^default-gym',
       gym_config.GymConfigUpdateView.as_view(),
       name='gymconfig-edit'),
)
