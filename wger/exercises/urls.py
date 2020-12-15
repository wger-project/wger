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
from django.conf.urls import (
    include,
    url
)
from django.contrib.auth.decorators import login_required
from django.urls import path

# wger
from wger.exercises.views import (
    categories,
    comments,
    equipment,
    exercises,
    images,
    muscles
)


# sub patterns for muscles
patterns_muscle = [
    path('overview/',
         muscles.MuscleListView.as_view(),
         name='overview'),
    path('admin-overview/',
         muscles.MuscleAdminListView.as_view(),
         name='admin-list'),
    path('add/',
         muscles.MuscleAddView.as_view(),
         name='add'),
    path('<int:pk>/edit/',
         muscles.MuscleUpdateView.as_view(),
         name='edit'),
    path('<int:pk>/delete/',
         muscles.MuscleDeleteView.as_view(),
         name='delete'),
]

# sub patterns for exercise images
patterns_images = [
    path('<int:exercise_pk>/image/add',
         images.ExerciseImageAddView.as_view(),
         name='add'),
    path('<int:pk>/edit',
         images.ExerciseImageEditView.as_view(),
         name='edit'),
    path('<int:exercise_pk>/image/<int:pk>/delete',
         images.ExerciseImageDeleteView.as_view(),
         name='delete'),
    path('<int:pk>/accept/',
         images.accept,
         name='accept'),
    path('<int:pk>/decline/',
         images.decline,
         name='decline'),
]

# sub patterns for exercise comments
patterns_comment = [
    path('<int:exercise_pk>/comment/add/',
         comments.ExerciseCommentAddView.as_view(),
         name='add'),
    path('<int:pk>/edit/',
         comments.ExerciseCommentEditView.as_view(),
         name='edit'),
    path('<int:id>/delete/',
         comments.delete,
         name='delete'),
]

# sub patterns for categories
patterns_category = [
    path('list',
         categories.ExerciseCategoryListView.as_view(),
         name='list'),
    path('<int:pk>/edit/',
         categories.ExerciseCategoryUpdateView.as_view(),
         name='edit'),
    path('add/',
         categories.ExerciseCategoryAddView.as_view(),
         name='add'),
    path('<int:pk>/delete/',
         categories.ExerciseCategoryDeleteView.as_view(),
         name='delete'),
]

# sub patterns for equipment
patterns_equipment = [
    path('list',
         equipment.EquipmentListView.as_view(),
         name='list'),
    path('add',
         equipment.EquipmentAddView.as_view(),
         name='add'),
    path('<int:pk>/edit',
         equipment.EquipmentEditView.as_view(),
         name='edit'),
    path('<int:pk>/delete',
         equipment.EquipmentDeleteView.as_view(),
         name='delete'),
    path('overview',
         equipment.EquipmentOverviewView.as_view(),
         name='overview'),
]


# sub patterns for exercises
patterns_exercise = [
    path('overview/',
         exercises.ExerciseListView.as_view(),
         name='overview'),
    path('<int:id>/view/',
         exercises.view,
         name='view'),
    url(r'^(?P<id>\d+)/view/(?P<slug>[-\w]*)/?$',
        exercises.view,
        name='view'),
    path('add/',
         login_required(exercises.ExerciseAddView.as_view()),
         name='add'),
    path('<int:pk>/edit/',
         exercises.ExerciseUpdateView.as_view(),
         name='edit'),
    path('<int:pk>/correct',
         exercises.ExerciseCorrectView.as_view(),
         name='correct'),
    path('<int:pk>/delete/',
         exercises.ExerciseDeleteView.as_view(),
         name='delete'),
    path('pending/',
         exercises.PendingExerciseListView.as_view(),
         name='pending'),
    path('<int:pk>/accept/',
         exercises.accept,
         name='accept'),
    path('<int:pk>/decline/',
         exercises.decline,
         name='decline'),
]


urlpatterns = [
    path('muscle/', include((patterns_muscle, 'muscle'), namespace="muscle")),
    path('image/', include((patterns_images, 'image'), namespace="image")),
    path('comment/', include((patterns_comment, 'comment'), namespace="comment")),
    path('category/', include((patterns_category, 'category'), namespace="category")),
    path('equipment/', include((patterns_equipment, 'equipment'), namespace="equipment")),
    path('', include((patterns_exercise, 'exercise'), namespace="exercise")),
]
