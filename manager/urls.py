from django.conf.urls import patterns, include, url

urlpatterns = patterns('manager.views',
    url(r'^$', 'index'),
    url(r'^workout/add$', 'add'),
    url(r'^workout/add/step/2$', 'add_step_2'),
    url(r'^workout/add/step/3$', 'add_step_3'),
    url(r'^workout/add/step/4$', 'add_step_4'),
    url(r'^workout/(?P<id>\d+)/view/$', 'view_workout'),
    url(r'^exercise/overview/$', 'exercise_overview'),
    url(r'^exercise/view/(?P<id>\d+)$', 'exercise_view'),
    url(r'^exercise/view/(?P<id>\d+)/edit/comment/(?P<comment_id>\d+)$', 'exercise_view'),
    url(r'^exercise/edit/(?P<id>\d*)$', 'exercise_edit'),
    url(r'^exercise/delete/(?P<id>\d*)$', 'exercise_delete'),
    url(r'^exercise/comment/delete/(?P<id>\d+)$', 'exercisecomment_delete'),
    
)