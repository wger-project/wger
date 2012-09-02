from django.conf.urls import patterns, include, url

urlpatterns = patterns('nutrition.views',
    url(r'^nutrition/overview/$', 'overview'),
    url(r'^nutrition/add/$', 'add'),
    url(r'^nutrition/(?P<id>\d+)/view/$', 'view'),
    url(r'^nutrition/(?P<id>\d+)/edit/meal/(?P<meal_id>\w*)$', 'edit_meal'),
    url(r'^nutrition/(?P<id>\d+)/edit/meal/(?P<meal_id>\d+)/item/(?P<item_id>\w*)$', 'edit_meal_item'),
    
    #url(r'^nutrition/export_pdf/$', 'export_pdf'),

)
