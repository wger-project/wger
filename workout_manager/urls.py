from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns

from django.contrib import admin
admin.autodiscover()

urlpatterns = i18n_patterns('',
    url(r'^admin/',   include(admin.site.urls)),
    url(r'^', include('manager.urls')),
    url(r'exercise/', include('exercises.urls')),
    url(r'weight/', include('weight.urls')),
    url(r'nutrition/', include('nutrition.urls')),
    url(r'^browserid/', include('django_browserid.urls')),
)
