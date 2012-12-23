from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from weight.views import WeightAddView
from weight.views import WeightUpdateView
from weight.views import WeightCsvImportFormPreview
from weight.views import WeightCsvImportForm

urlpatterns = patterns('weight.views',

    url(r'^add/$',
        login_required(WeightAddView.as_view()),
        name='weight-add'),

    url(r'^(?P<pk>\d+)/edit/$',
        login_required(WeightUpdateView.as_view()),
        name='weight-edit'),

    url(r'^export-csv/$', 'export_csv'),
    url(r'^import-csv/$',
        login_required(WeightCsvImportFormPreview(WeightCsvImportForm)),
        name='weight-import-csv'),
    
    url(r'^overview/$',
        'overview',
        name='weight-overview'),
    url(r'^api/get_weight_data/$', 'get_weight_data'),


)
