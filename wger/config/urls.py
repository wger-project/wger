from django.conf.urls import patterns, url

from wger.config.views import languages
from wger.config.views import language_config


urlpatterns = patterns('',

   # Languages
   url(r'^language/list$',
        languages.LanguageListView.as_view(),
        name='language-overview'),
   url(r'^language/(?P<pk>\d+)/view$',
        languages.LanguageDetailView.as_view(),
        name='language-view'),
   url(r'^language/(?P<pk>\d+)/delete$',
        languages.LanguageDeleteView.as_view(),
        name='language-delete'),
   url(r'^language/(?P<pk>\d+)/edit',
        languages.LanguageEditView.as_view(),
        name='language-edit'),
   url(r'^language/add$',
        languages.LanguageCreateView.as_view(),
        name='language-add'),

    # Language configs
    url(r'^language/config/(?P<pk>\d+)/edit',
        language_config.LanguageConfigUpdateView.as_view(),
        name='languageconfig-edit'),
)
