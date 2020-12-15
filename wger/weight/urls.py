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
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from django.urls import path

# wger
from wger.weight import views
from wger.weight.forms import WeightCsvImportForm


urlpatterns = [
    path('add/',
         login_required(views.WeightAddView.as_view()),
         name='add'),

    path('<int:pk>/edit/',
         login_required(views.WeightUpdateView.as_view()),
         name='edit'),

    path('<int:pk>/delete/',
         views.WeightDeleteView.as_view(),
         name='delete'),

    path('export-csv/',
         views.export_csv,
         name='export-csv'),
    path('import-csv/',
         login_required(views.WeightCsvImportFormPreview(WeightCsvImportForm)),
         name='import-csv'),

    url(r'^overview/(?P<username>[\w.@+-]+)$',
        views.overview,
        name='overview'),
    # url(r'^overview/$',
    #     views.overview,
    #     name='overview'),
    url(r'^api/get_weight_data/(?P<username>[\w.@+-]+)$',  # JS
        views.get_weight_data,
        name='weight-data'),
    path('api/get_weight_data/',  # JS
         views.get_weight_data,
         name='weight-data'),
]
