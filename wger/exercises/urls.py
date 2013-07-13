from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required

from wger.exercises.views import exercises
from wger.exercises.views import comments
from wger.exercises.views import categories
from wger.exercises.views import muscles

urlpatterns = patterns('wger.exercises.views',

    # Exercises
    url(r'^overview/$',
        'exercises.overview',
        name='exercise-overview'),

    url(r'^search/$', 'exercises.search'),
    url(r'^(?P<id>\d+)/view/$',
    url(r'^(?P<id>\d+)/view/(?P<slug>[-\w]+)/$',
        'exercises.view',
        name='exercise-view'),
    url(r'^add/$',
        login_required(exercises.ExerciseAddView.as_view()),
        name='exercise-add'),
    url(r'^(?P<pk>\d+)/edit/$',
        permission_required('exercises.add_exercise')(exercises.ExerciseUpdateView.as_view()),
        name='exercise-edit'),
    url(r'^(?P<pk>\d+)/delete/$',
        permission_required('exercises.delete_exercise')(exercises.ExerciseDeleteView.as_view()),
        name='exercise-delete'),
    url(r'^pending/$',
        permission_required('exercises.change_exercise')(exercises.PendingExerciseListView.as_view()),
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
        permission_required('exercises.add_muscle')(muscles.MuscleAddView.as_view()),
        name='muscle-add'),
    url(r'^muscle/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_muscle')(muscles.MuscleUpdateView.as_view()),
        name='muscle-edit'),
    url(r'^muscle/(?P<pk>\d+)/delete/$',
        permission_required('exercises.delete_muscle')(muscles.MuscleDeleteView.as_view()),
        name='muscle-delete'),

    # Comments
    url(r'^(?P<exercise_pk>\d+)/comment/add/$',
        permission_required('exercises.add_exercisecomment')(comments.ExerciseCommentAddView.as_view()),
        name='exercisecomment-add'),
    url(r'^comment/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercisecomment')(comments.ExerciseCommentEditView.as_view()),
        name='exercisecomment-edit'),
    url(r'^comment/(?P<id>\d+)/delete/$',
        'comments.delete',
        name='exercisecomment-delete'),

    # Categories
    url(r'^category/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercisecategory')(categories.ExerciseCategoryUpdateView.as_view()),
        name='exercisecategory-edit'),
    url(r'^category/add/$',
        permission_required('exercises.add_exercisecategory')(categories.ExerciseCategoryAddView.as_view()),
        name='exercisecategory-add'),
    url(r'^category/(?P<pk>\d+)/delete/$',
        permission_required('exercises.delete_exercisecategory')(categories.ExerciseCategoryDeleteView.as_view()),
        name='exercisecategory-delete'),
)
