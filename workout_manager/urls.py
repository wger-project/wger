from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    url(r'^admin/',   include(admin.site.urls)),
    url(r'^', include('manager.urls')),
    url(r'^', include('exercises.urls')),
    #url(r'^', include('weight.urls')),
)