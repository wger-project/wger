from django.conf.urls import patterns, include, url

urlpatterns = patterns('exercises.views',
    url(r'^exercise/overview/$', 'exercise_overview'),
    url(r'^exercise/search/$', 'exercise_search'),
    url(r'^exercise/(?P<id>\d+)/view/$', 'exercise_view'),
    url(r'^exercise/(?P<id>\d+)/view/edit/comment/(?P<comment_id>\d+)$', 'exercise_view'),
    url(r'^exercise/(?P<id>\w*)/edit/$', 'exercise_edit'),
    url(r'^exercise/(?P<id>\d*)/delete/$', 'exercise_delete'),
    
    # Comments
    url(r'^exercise/comment/(?P<id>\d+)/delete/$', 'exercisecomment_delete'),
    
    # Categories
    url(r'^exercise/category/(?P<id>\d*)/edit/$', 'exercise_category_edit'),
    url(r'^exercise/category/(?P<id>\d*)/delete/$', 'exercise_category_delete'),
    
)
