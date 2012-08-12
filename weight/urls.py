from django.conf.urls import patterns, include, url

urlpatterns = patterns('weight.views',
    url(r'^weight/add/(?P<id>\d*)$', 'add'),
    url(r'^weight/overview/$', 'overview'),

)
