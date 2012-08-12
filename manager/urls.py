from django.conf.urls import patterns, include, url

urlpatterns = patterns('manager.views',
    url(r'^$', 'index'),
    url(r'^login$', 'login'),
    url(r'^logout$', 'logout'),
    
    url(r'^workout/add$', 'add'),
    url(r'^workout/(?P<id>\d+)/pdf/$', 'pdf_workout'),
    url(r'^workout/(?P<id>\d+)/view/$', 'view_workout'),
    url(r'^workout/(?P<id>\d+)/delete/$', 'delete_workout'),
    url(r'^workout/(?P<id>\d+)/edit/day/(?P<day_id>\d*)$', 'edit_day'),
    url(r'^workout/(?P<id>\d+)/delete/day/(?P<day_id>\d+)$', 'delete_day'),
    url(r'^workout/(?P<id>\d+)/day/(?P<day_id>\d+)/edit/set/(?P<set_id>\d*)$', 'edit_set'),
    url(r'^workout/(?P<id>\d+)/day/(?P<day_id>\d+)/delete/set/(?P<set_id>\d+)$', 'delete_set'),
    url(r'^workout/(?P<id>\d+)/set/(?P<set_id>\d+)/exercise/(?P<exercise_id>\d+)/edit/setting/(?P<setting_id>\d*)$', 'edit_setting'),
    url(r'^workout/(?P<id>\d+)/set/(?P<set_id>\d+)/exercise/(?P<exercise_id>\d+)/delete/setting$', 'delete_setting'),
    
    
    url(r'^exercise/overview/$', 'exercise_overview'),
    url(r'^exercise/view/(?P<id>\d+)$', 'exercise_view'),
    url(r'^exercise/view/(?P<id>\d+)/edit/comment/(?P<comment_id>\d+)$', 'exercise_view'),
    url(r'^exercise/edit/(?P<id>\d*)$', 'exercise_edit'),
    url(r'^exercise/delete/(?P<id>\d*)$', 'exercise_delete'),
    url(r'^exercise/comment/delete/(?P<id>\d+)$', 'exercisecomment_delete'),
    url(r'^exercise/category/edit/(?P<id>\d*)$', 'exercise_category_edit'),
    url(r'^exercise/category/delete/(?P<id>\d*)$', 'exercise_category_delete'),
    
)
