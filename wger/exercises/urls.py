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
from django.conf.urls import include
from django.urls import (
    path,
    re_path,
)

# wger
from wger.core.views.react import ReactView
from wger.exercises.views import (
    categories,
    equipment,
    exercises,
    history,
    muscles,
)


# sub patterns for history
patterns_history = [
    path('admin-control', history.control, name='overview'),
    path(
        'admin-control/revert/<int:history_pk>/<int:content_type_id>',
        history.history_revert,
        name='revert',
    ),
]

# sub patterns for muscles
patterns_muscle = [
    path(
        'admin-overview/',
        muscles.MuscleAdminListView.as_view(),
        name='admin-list',
    ),
    path(
        'add/',
        muscles.MuscleAddView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>/edit/',
        muscles.MuscleUpdateView.as_view(),
        name='edit',
    ),
    path(
        '<int:pk>/delete/',
        muscles.MuscleDeleteView.as_view(),
        name='delete',
    ),
]

# sub patterns for categories
patterns_category = [
    path(
        'list',
        categories.ExerciseCategoryListView.as_view(),
        name='list',
    ),
    path(
        '<int:pk>/edit/',
        categories.ExerciseCategoryUpdateView.as_view(),
        name='edit',
    ),
    path(
        'add/',
        categories.ExerciseCategoryAddView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>/delete/',
        categories.ExerciseCategoryDeleteView.as_view(),
        name='delete',
    ),
]

# sub patterns for equipment
patterns_equipment = [
    path(
        'list',
        equipment.EquipmentListView.as_view(),
        name='list',
    ),
    path(
        'add',
        equipment.EquipmentAddView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>/edit',
        equipment.EquipmentEditView.as_view(),
        name='edit',
    ),
    path(
        '<int:pk>/delete',
        equipment.EquipmentDeleteView.as_view(),
        name='delete',
    ),
]

# sub patterns for exercises
patterns_exercise = [
    path(
        'overview/',
        ReactView.as_view(div_id='react-exercise-overview'),
        name='overview',
    ),
    path(
        '<int:id>/view/',
        exercises.view,
        name='view',
    ),
    re_path(
        r'^(?P<id>\d+)/view/(?P<slug>[-\w]*)/?$',
        exercises.view,
        name='view',
    ),
    path(
        '<int:pk>/view-base',
        ReactView.as_view(div_id='react-exercise-overview'),
        name='view-base',
    ),
    path(
        '<int:pk>/view-base/<slug:slug>',
        ReactView.as_view(div_id='react-exercise-detail'),
        name='view-base',
    ),
    path(
        'contribute',
        ReactView.as_view(div_id='react-exercise-contribute'),
        name='contribute',
    ),
]

urlpatterns = [
    path('muscle/', include((patterns_muscle, 'muscle'), namespace='muscle')),
    path('category/', include((patterns_category, 'category'), namespace='category')),
    path('equipment/', include((patterns_equipment, 'equipment'), namespace='equipment')),
    path('history/', include((patterns_history, 'history'), namespace='history')),
    path('', include((patterns_exercise, 'exercise'), namespace='exercise')),
]
