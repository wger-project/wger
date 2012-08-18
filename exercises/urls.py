from django.conf.urls import patterns, include, url

urlpatterns = patterns('exercises.views',
    url(r'^exercise/overview/$', 'exercise_overview'),
    url(r'^exercise/search/$', 'exercise_search'),
    url(r'^exercise/view/(?P<id>\d+)$', 'exercise_view'),
    url(r'^exercise/view/(?P<id>\d+)/edit/comment/(?P<comment_id>\d+)$', 'exercise_view'),
    url(r'^exercise/edit/(?P<id>\d*)$', 'exercise_edit'),
    url(r'^exercise/delete/(?P<id>\d*)$', 'exercise_delete'),
    url(r'^exercise/comment/delete/(?P<id>\d+)$', 'exercisecomment_delete'),
    url(r'^exercise/category/edit/(?P<id>\d*)$', 'exercise_category_edit'),
    url(r'^exercise/category/delete/(?P<id>\d*)$', 'exercise_category_delete'),
    
)
