from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from weight.views import WeightAddView
from weight.views import WeightUpdateView

urlpatterns = patterns('weight.views',

    url(r'^weight/add/$',
        login_required(WeightAddView.as_view()),
        name='weight-add'),

    url(r'^weight/(?P<pk>\d+)/edit/$',
        login_required(WeightUpdateView.as_view()),
        name='weight-edit'),

    url(r'^weight/export_csv/$', 'export_csv'),
    url(r'^weight/overview/$', 'overview'),
    url(r'^weight/api/get_weight_data/$', 'get_weight_data'),


)
