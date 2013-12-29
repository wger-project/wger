from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from wger.exercises.views import exercises
from wger.exercises.views import comments
from wger.exercises.views import categories
from wger.exercises.views import muscles
from wger.exercises.views import images
from wger.exercises.views import equipment

urlpatterns = patterns('wger.exercises.views',

    # Exercises
    url(r'^overview/$',
        exercises.overview,
        name='exercise-overview'),

    url(r'^search/$',
        exercises.search),
    url(r'^(?P<id>\d+)/view/$',
        exercises.view,
        name='exercise-view'),
    url(r'^(?P<id>\d+)/view/(?P<slug>[-\w]+)/$',
        exercises.view,
        name='exercise-view'),
    url(r'^add/$',
        login_required(exercises.ExerciseAddView.as_view()),
        name='exercise-add'),
    url(r'^(?P<pk>\d+)/edit/$',
        exercises.ExerciseUpdateView.as_view(),
        name='exercise-edit'),
    url(r'^(?P<pk>\d+)/delete/$',
        exercises.ExerciseDeleteView.as_view(),
        name='exercise-delete'),
    url(r'^pending/$',
        exercises.PendingExerciseListView.as_view(),
        name='exercise-pending'),
    url(r'^(?P<pk>\d+)/accept/$',
        'exercises.accept',
        name='exercise-accept'),
    url(r'^(?P<pk>\d+)/decline/$',
        'exercises.decline',
        name='exercise-decline'),

    # Muscles
    url(r'^muscle/overview/$',
        muscles.MuscleListView.as_view(),
        name='muscle-overview'),
    url(r'^muscle/add/$',
        muscles.MuscleAddView.as_view(),
        name='muscle-add'),
    url(r'^muscle/(?P<pk>\d+)/edit/$',
        muscles.MuscleUpdateView.as_view(),
        name='muscle-edit'),
    url(r'^muscle/(?P<pk>\d+)/delete/$',
        muscles.MuscleDeleteView.as_view(),
        name='muscle-delete'),

    # Comments
    url(r'^(?P<exercise_pk>\d+)/comment/add/$',
        comments.ExerciseCommentAddView.as_view(),
        name='exercisecomment-add'),
    url(r'^comment/(?P<pk>\d+)/edit/$',
        comments.ExerciseCommentEditView.as_view(),
        name='exercisecomment-edit'),
    url(r'^comment/(?P<id>\d+)/delete/$',
        'comments.delete',
        name='exercisecomment-delete'),

    # Categories
    url(r'^category/(?P<pk>\d+)/edit/$',
        categories.ExerciseCategoryUpdateView.as_view(),
        name='exercisecategory-edit'),
    url(r'^category/add/$',
        categories.ExerciseCategoryAddView.as_view(),
        name='exercisecategory-add'),
    url(r'^category/(?P<pk>\d+)/delete/$',
        categories.ExerciseCategoryDeleteView.as_view(),
        name='exercisecategory-delete'),

    # Images
    url(r'^(?P<exercise_pk>\d+)/image/add$',
        images.ExerciseImageAddView.as_view(),
        name='exerciseimage-add'),
    url(r'^image/(?P<pk>\d+)/edit$',
        images.ExerciseImageEditView.as_view(),
        name='exerciseimage-edit'),
    url(r'^(?P<exercise_pk>\d+)/image/(?P<pk>\d+)/delete$',
        images.ExerciseImageDeleteView.as_view(),
        name='exerciseimage-delete'),

    # Equipment
    url(r'^equipment/list$',
        equipment.EquipmentListView.as_view(),
        name='equipment-list'),
    url(r'^equipment/add$',
        equipment.EquipmentAddView.as_view(),
        name='equipment-add'),
    url(r'^equipment/(?P<pk>\d+)/edit$',
        equipment.EquipmentEditView.as_view(),
        name='equipment-edit'),
    url(r'^equipment/(?P<pk>\d+)/delete$',
        equipment.EquipmentDeleteView.as_view(),
        name='equipment-delete'),

)
