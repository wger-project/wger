from django.conf.urls import patterns, include, url

urlpatterns = patterns('manager.views',
    url(r'^$', 'index'),
    url(r'^workout/add$', 'add'),
    url(r'^workout/(?P<id>\d+)/view/$', 'view_workout'),
    
)