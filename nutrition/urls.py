from django.conf.urls import patterns, include, url

urlpatterns = patterns('nutrition.views',
    url(r'^nutrition/overview/$', 'overview'),
    url(r'^nutrition/add/$', 'add'),
    url(r'^nutrition/(?P<id>\d+)/view/$', 'view'),
    url(r'^nutrition/(?P<id>\d+)/edit/plan/$', 'edit_plan'),
    url(r'^nutrition/(?P<id>\d+)/edit/meal/(?P<meal_id>\w*)$', 'edit_meal'),
    url(r'^nutrition/(?P<id>\d+)/add/meal/$', 'add_meal'),
    url(r'^nutrition/(?P<id>\d+)/edit/meal/(?P<meal_id>\d+)/item/(?P<item_id>\w*)$', 'edit_meal_item'),
    url(r'^nutrition/delete/meal/item/(?P<item_id>\d+)$', 'delete_meal_item'),
    url(r'^nutrition/delete/meal/(?P<id>\d+)$', 'delete_meal'),
    
    #url(r'^nutrition/export_pdf/$', 'export_pdf'),

)
