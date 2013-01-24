from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required

from wger.exercises.views import ExerciseUpdateView
from wger.exercises.views import ExerciseAddView
from wger.exercises.views import ExerciseDeleteView

from wger.exercises.views import ExerciseCategoryAddView
from wger.exercises.views import ExerciseCategoryUpdateView
from wger.exercises.views import ExerciseCategoryDeleteView

from wger.exercises.views import ExerciseCommentAddView
from wger.exercises.views import ExerciseCommentEditView

from wger.exercises.views import MuscleListView

urlpatterns = patterns('wger.exercises.views',

    # Exercises
    url(r'^overview/$', 'exercise_overview'),

    url(r'^muscle/overview/$',
        MuscleListView.as_view(),
        name='muscle-overview'),
    url(r'^search/$', 'exercise_search'),
    url(r'^(?P<id>\d+)/view/(?P<slug>[-\w]+)/$', 'exercise_view'),
    url(r'^(?P<id>\d+)/view/$', 'exercise_view'),
    url(r'^add/$',
        permission_required('exercises.change_exercise')(ExerciseAddView.as_view()),
        name='exercise-add'),
    url(r'^(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercise')(ExerciseUpdateView.as_view()),
        name='exercise-edit'),
    url(r'^(?P<pk>\d+)/delete/$',
        permission_required('exercises.change_exercise')(ExerciseDeleteView.as_view()),
        name='exercise-delete'),

    # Comments
    url(r'^(?P<exercise_pk>\d+)/comment/add/$',
        permission_required('exercises.change_exercise')(ExerciseCommentAddView.as_view()),
        name='exercisecomment-add'),
    url(r'^comment/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercise')(ExerciseCommentEditView.as_view()),
        name='exercisecomment-edit'),
    url(r'^comment/(?P<id>\d+)/delete/$',
        'exercisecomment_delete',
        name='exercisecomment-delete'),

    # Categories
    url(r'^category/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercise')(ExerciseCategoryUpdateView.as_view()),
        name='exercisecategory-edit'),
    url(r'^category/add/$',
        permission_required('exercises.change_exercise')(ExerciseCategoryAddView.as_view()),
        name='exercisecategory-add'),
    url(r'^category/(?P<pk>\d+)/delete/$',
        permission_required('exercises.change_exercise')(ExerciseCategoryDeleteView.as_view()),
        name='exercisecategory-delete'),
)
