from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView


from wger.config.views import languages

from wger.utils.constants import USER_TAB


urlpatterns = patterns('',

   # Languages
   url(r'^languages/list$',
        languages.LanguageListView.as_view(),
        name='language-overview'),
   url(r'^languages/(?P<pk>\d+)/view$',
        languages.LanguageDetailView.as_view(),
        name='language-view'),
   url(r'^languages/(?P<pk>\d+)/delete$',
        languages.LanguageDeleteView.as_view(),
        name='language-delete'),
   url(r'^languages/(?P<pk>\d+)/edit',
        languages.LanguageEditView.as_view(),
        name='language-edit'),
   url(r'^languages/add$',
        languages.LanguageCreateView.as_view(),
        name='language-add'),

)