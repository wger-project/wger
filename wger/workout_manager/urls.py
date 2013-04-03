from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.i18n import patterns
from django.views.generic import TemplateView

from wger.exercises.sitemap import ExercisesSitemap
from wger.nutrition.sitemap import NutritionSitemap

from django.contrib import admin
admin.autodiscover()

sitemaps = {'exercises': ExercisesSitemap,
            'nutrition': NutritionSitemap}

urlpatterns = i18n_patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('wger.manager.urls')),
    url(r'exercise/', include('wger.exercises.urls')),
    url(r'weight/', include('wger.weight.urls')),
    url(r'nutrition/', include('wger.nutrition.urls')),
    url(r'software/', include('wger.software.urls', namespace='software', app_name='software')),
    url(r'^browserid/', include('django_browserid.urls')),
    url(r'^sitemap\.xml$',
        'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps},
        name='sitemap')
)

# Send robots.txt without any language prefix
urlpatterns = urlpatterns + patterns('',
    url(r'^robots\.txt$',
        TemplateView.as_view(template_name="robots.txt"),
       ),
)
