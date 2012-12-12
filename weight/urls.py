from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from weight.views import WeightAddView
from weight.views import WeightUpdateView
from weight.views import WeightCsvImportFormPreview
from weight.views import WeightCsvImportForm

urlpatterns = patterns('weight.views',

    url(r'^weight/add/$',
        login_required(WeightAddView.as_view()),
        name='weight-add'),

    url(r'^weight/(?P<pk>\d+)/edit/$',
        login_required(WeightUpdateView.as_view()),
        name='weight-edit'),

    url(r'^weight/export-csv/$', 'export_csv'),
    url(r'^weight/import-csv/$',
        login_required(WeightCsvImportFormPreview(WeightCsvImportForm)),
        name='weight-import-csv'),
    
    url(r'^weight/overview/$',
        'overview',
        name='weight-overview'),
    url(r'^weight/api/get_weight_data/$', 'get_weight_data'),


)
