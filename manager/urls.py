from django.conf.urls import patterns, include, url

urlpatterns = patterns('manager.views',
    url(r'^$', 'index'),
    url(r'^login$', 'login'),
    url(r'^logout$', 'logout'),
    url(r'^user/registration$', 'registration'),
    url(r'^user/preferences$', 'preferences'),
    
    url(r'^workout/add$', 'add'),
    url(r'^workout/(?P<id>\d+)/pdf/$', 'pdf_workout'),
    url(r'^workout/(?P<id>\d+)/view/$', 'view_workout'),
    url(r'^workout/(?P<id>\d+)/delete/$', 'delete_workout'),
    url(r'^workout/(?P<id>\d+)/edit/day/(?P<day_id>\w*)$', 'edit_day'),
    url(r'^workout/(?P<id>\d+)/delete/day/(?P<day_id>\d+)$', 'delete_day'),
    url(r'^workout/day/view/(?P<id>\d+)$', 'view_day'),
    url(r'^workout/(?P<id>\d+)/day/(?P<day_id>\d+)/edit/set/(?P<set_id>\w*)$', 'edit_set'),
    url(r'^workout/(?P<id>\d+)/day/(?P<day_id>\d+)/delete/set/(?P<set_id>\d+)$', 'delete_set'),
    url(r'^workout/(?P<id>\d+)/set/(?P<set_id>\d+)/exercise/(?P<exercise_id>\d+)/edit/setting/(?P<setting_id>\d*)$', 'edit_setting'),
    url(r'^workout/(?P<id>\d+)/set/(?P<set_id>\d+)/exercise/(?P<exercise_id>\d+)/delete/setting$', 'delete_setting'),
    
    url(r'^workout/api/edit-set$', 'api_edit_set'),
    url(r'^workout/api/edit-settting$', 'api_edit_setting'),
    url(r'^workout/api/user-preferences$', 'api_user_preferences'),
)
