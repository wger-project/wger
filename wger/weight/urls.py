from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from wger.weight.views import WeightAddView
from wger.weight.views import WeightUpdateView
from wger.weight.views import WeightCsvImportFormPreview
from wger.weight.views import WeightCsvImportForm

urlpatterns = patterns('wger.weight.views',

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
