from django.conf.urls import patterns, include, url

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'workout_manager.views.home', name='home'),
    # url(r'^workout_manager/', include('workout_manager.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    #url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
)


urlpatterns += patterns('',
    url(r'^$', 'manager.views.index'),
    url(r'^workout/add$', 'manager.views.add'),
    url(r'^workout/(?P<id>\d+)/view/$', 'manager.views.view_workout'),
    
)