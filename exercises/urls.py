from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required

from exercises.views import ExerciseUpdateView
from exercises.views import ExerciseAddView
from exercises.views import ExerciseDeleteView

from exercises.views import ExerciseCategoryAddView
from exercises.views import ExerciseCategoryUpdateView
from exercises.views import ExerciseCategoryDeleteView

from exercises.views import ExerciseCommentAddView
from exercises.views import ExerciseCommentEditView

from exercises.views import MuscleListView

urlpatterns = patterns('exercises.views',

    # Exercises
    url(r'^exercise/overview/$', 'exercise_overview'),
    url(r'^exercise/muscle/overview/$',
        MuscleListView.as_view(),
        name='muscle-overview'),
    url(r'^exercise/search/$', 'exercise_search'),
    url(r'^exercise/(?P<id>\d+)/view/$', 'exercise_view'),
    url(r'^exercise/add/$',
        permission_required('exercises.change_exercise')(ExerciseAddView.as_view()),
        name='exercise-add'),
    url(r'^exercise/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercise')(ExerciseUpdateView.as_view()),
        name='exercise-edit'),
    url(r'^exercise/(?P<pk>\d+)/delete/$',
        permission_required('exercises.change_exercise')(ExerciseDeleteView.as_view()),
        name='exercise-delete'),

    # Comments
    url(r'^exercise/(?P<exercise_pk>\d+)/comment/add/$',
        permission_required('exercises.change_exercise')(ExerciseCommentAddView.as_view()),
        name='exercisecomment-add'),
    url(r'^exercise/comment/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercise')(ExerciseCommentEditView.as_view()),
        name='exercisecomment-edit'),
    url(r'^exercise/comment/(?P<id>\d+)/delete/$', 'exercisecomment_delete'),

    # Categories
    url(r'^exercise/category/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercise')(ExerciseCategoryUpdateView.as_view()),
        name='exercisecategory-edit'),
    url(r'^exercise/category/add/$',
        permission_required('exercises.change_exercise')(ExerciseCategoryAddView.as_view()),
        name='exercisecategory-add'),
    url(r'^exercise/category/(?P<pk>\d+)/delete/$',
        permission_required('exercises.change_exercise')(ExerciseCategoryDeleteView.as_view()),
        name='exercisecategory-delete'),
)
