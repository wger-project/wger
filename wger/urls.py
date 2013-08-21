from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.i18n import patterns

from wger.exercises.sitemap import ExercisesSitemap
from wger.nutrition.sitemap import NutritionSitemap
from wger.utils.generic_views import TextTemplateView
from wger.utils.generic_views import WebappManifestView

from tastypie.api import Api

from wger.exercises.api.resources import ExerciseResource
from wger.exercises.api.resources import ExerciseCategoryResource
from wger.exercises.api.resources import ExerciseCommentResource
from wger.exercises.api.resources import MuscleResource
from wger.exercises.api.resources import LanguageResource

from wger.nutrition.api.resources import IngredientResource
from wger.nutrition.api.resources import WeightUnitResource

# REST API
v1_api = Api(api_name='v1')

# Exercises app
v1_api.register(ExerciseCategoryResource())
v1_api.register(ExerciseCommentResource())
v1_api.register(ExerciseResource())
v1_api.register(MuscleResource())
v1_api.register(LanguageResource())

# Nutrition app
v1_api.register(IngredientResource())
v1_api.register(WeightUnitResource())


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
    url(r'config/', include('wger.config.urls', namespace='config', app_name='config')),
    url(r'^browserid/', include('django_browserid.urls')),
    url(r'^sitemap\.xml$',
        'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps},
        name='sitemap')
)

# Send these static files without any language prefix
urlpatterns = urlpatterns + patterns('',
    url(r'^robots\.txt$',
        TextTemplateView.as_view(template_name="robots.txt"),
        name='robots'),
    url(r'^manifest\.webapp$',
        WebappManifestView.as_view(template_name="manifest.webapp"),
       ),
   (r'^api/', include(v1_api.urls)),
)
