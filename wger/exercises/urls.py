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

from django.conf.urls import patterns, url, include
from django.contrib.auth.decorators import login_required

from wger.exercises.views import (
    exercises,
    comments,
    categories,
    muscles,
    images,
    equipment
)



# sub patterns for muscles
patterns_muscle = [
    url(r'^overview/$',
        muscles.MuscleListView.as_view(),
        name='overview'),
    url(r'^admin-overview/$',
        muscles.MuscleAdminListView.as_view(),
        name='admin-list'),
    url(r'^add/$',
        muscles.MuscleAddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit/$',
        muscles.MuscleUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete/$',
        muscles.MuscleDeleteView.as_view(),
        name='delete'),
]

# sub patterns for exercise images
patterns_images = [
    url(r'^(?P<exercise_pk>\d+)/image/add$',
        images.ExerciseImageAddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit$',
        images.ExerciseImageEditView.as_view(),
        name='edit'),
    url(r'^(?P<exercise_pk>\d+)/image/(?P<pk>\d+)/delete$',
        images.ExerciseImageDeleteView.as_view(),
        name='delete'),
    url(r'^(?P<pk>\d+)/accept/$',
        images.accept,
        name='accept'),
    url(r'^(?P<pk>\d+)/decline/$',
        images.decline,
        name='decline'),
]

# sub patterns for exercise comments
patterns_comment = [
    url(r'^(?P<exercise_pk>\d+)/comment/add/$',
        comments.ExerciseCommentAddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit/$',
        comments.ExerciseCommentEditView.as_view(),
        name='edit'),
    url(r'^(?P<id>\d+)/delete/$',
        comments.delete,
        name='delete'),
]

# sub patterns for categories
patterns_category = [
    url(r'^list$',
        categories.ExerciseCategoryListView.as_view(),
        name='list'),
    url(r'^(?P<pk>\d+)/edit/$',
        categories.ExerciseCategoryUpdateView.as_view(),
        name='edit'),
    url(r'^add/$',
        categories.ExerciseCategoryAddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/delete/$',
        categories.ExerciseCategoryDeleteView.as_view(),
        name='delete'),
]

# sub patterns for equipment
patterns_equipment = [
    url(r'^list$',
        equipment.EquipmentListView.as_view(),
        name='list'),
    url(r'^add$',
        equipment.EquipmentAddView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit$',
        equipment.EquipmentEditView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete$',
        equipment.EquipmentDeleteView.as_view(),
        name='delete'),
    url(r'^overview$',
        equipment.EquipmentOverviewView.as_view(),
        name='overview'),
]


# sub patterns for exercises
patterns_exercise = [
    url(r'^overview/$',
        exercises.ExerciseListView.as_view(),
        name='overview'),
    url(r'^(?P<id>\d+)/view/$',
        exercises.view,
        name='view'),
    url(r'^(?P<id>\d+)/view/(?P<slug>[-\w]*)/?$',
        exercises.view,
        name='view'),
    url(r'^add/$',
        login_required(exercises.ExerciseAddView.as_view()),
        name='add'),
    url(r'^(?P<pk>\d+)/edit/$',
        exercises.ExerciseUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/correct$',
        exercises.ExerciseCorrectView.as_view(),
        name='correct'),
    url(r'^(?P<pk>\d+)/delete/$',
        exercises.ExerciseDeleteView.as_view(),
        name='delete'),
    url(r'^pending/$',
        exercises.PendingExerciseListView.as_view(),
        name='pending'),
    url(r'^(?P<pk>\d+)/accept/$',
        exercises.accept,
        name='accept'),
    url(r'^(?P<pk>\d+)/decline/$',
        exercises.decline,
        name='decline'),
]


urlpatterns = [
   url(r'^muscle/', include(patterns_muscle, namespace="muscle")),
   url(r'^image/', include(patterns_images, namespace="image")),
   url(r'^comment/', include(patterns_comment, namespace="comment")),
   url(r'^category/', include(patterns_category, namespace="category")),
   url(r'^equipment/', include(patterns_equipment, namespace="equipment")),
   url(r'^', include(patterns_exercise, namespace="exercise")),
]
