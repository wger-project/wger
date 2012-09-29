from django.conf.urls import patterns, include, url

urlpatterns = patterns('weight.views',
    url(r'^weight/add/(?P<id>\w*)$', 'add'),
    url(r'^weight/export_csv/$', 'export_csv'),
    url(r'^weight/overview/$', 'overview'),
    url(r'^weight/api/get_weight_data/$', 'get_weight_data'),
    

)
