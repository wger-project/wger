from django.conf.urls import patterns, include, url

from exercises.views import ExerciseUpdateView
from exercises.views import ExerciseAddView
from exercises.views import ExerciseDeleteView
from exercises.views import ExerciseCategoryAddView
from exercises.views import ExerciseCategoryUpdateView

urlpatterns = patterns('exercises.views',
    url(r'^exercise/overview/$', 'exercise_overview'),
    url(r'^exercise/search/$', 'exercise_search'),
    url(r'^exercise/(?P<id>\d+)/view/$', 'exercise_view'),
    url(r'^exercise/(?P<id>\d+)/view/edit/comment/(?P<comment_id>\d+)$', 'exercise_view'),
    
    url(r'^exercise/(?P<pk>\d+)/edit/$', ExerciseUpdateView.as_view(), name='exercise-edit'),
    url(r'^exercise/add/$', ExerciseAddView.as_view(), name='exercise-add'),
    #url(r'^exercise/(?P<pk>\d+)/delete/$', ExerciseDeleteView.as_view(), name='exercise-delete'),
    url(r'^exercise/(?P<id>\d*)/delete/$', 'exercise_delete', name='exercise-delete'),
    
    
    # Comments
    url(r'^exercise/comment/(?P<id>\d+)/delete/$', 'exercisecomment_delete'),
    
    # Categories
    url(r'^exercise/category/(?P<pk>\d+)/edit/$', ExerciseCategoryUpdateView.as_view(), name='exercisecategory-edit'),
    url(r'^exercise/category/add/$', ExerciseCategoryAddView.as_view(), name='exercisecategory-add'),
    #url(r'^exercise/category/(?P<id>\d*)/edit/$', 'exercise_category_edit'),
    url(r'^exercise/category/(?P<id>\d+)/delete/$', 'exercise_category_delete'),
    
)
