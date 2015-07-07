# -*- coding: utf-8 -*-

# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

from tastypie.api import Api
from rest_framework import routers

from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.i18n import patterns

from wger.nutrition.sitemap import NutritionSitemap
from wger.exercises.sitemap import ExercisesSitemap

from wger.utils.generic_views import TextTemplateView
from wger.utils.generic_views import WebappManifestView

from wger.exercises.api import resources as exercises_api
from wger.nutrition.api import resources as nutrition_api
from wger.manager.api import resources as manager_api
from wger.core.api import resources as core_api
from wger.weight.api import resources as weight_api

from wger.manager.api import views as manager_api_views
from wger.core.api import views as core_api_views
from wger.exercises.api import views as exercises_api_views
from wger.nutrition.api import views as nutrition_api_views
from wger.weight.api import views as weight_api_views

#
# REST API
#

### /api/v1 - tastypie - deprecated
v1_api = Api(api_name='v1')

v1_api.register(exercises_api.ExerciseCategoryResource())
v1_api.register(exercises_api.ExerciseCommentResource())
v1_api.register(exercises_api.ExerciseImageResource())
v1_api.register(exercises_api.ExerciseResource())
v1_api.register(exercises_api.MuscleResource())
v1_api.register(exercises_api.EquipmentResource())

v1_api.register(nutrition_api.IngredientResource())
v1_api.register(nutrition_api.WeightUnitResource())
v1_api.register(nutrition_api.NutritionPlanResource())
v1_api.register(nutrition_api.MealResource())
v1_api.register(nutrition_api.MealItemResource())
v1_api.register(nutrition_api.IngredientToWeightUnit())

v1_api.register(manager_api.WorkoutResource())
v1_api.register(manager_api.ScheduleResource())
v1_api.register(manager_api.ScheduleStepResource())
v1_api.register(manager_api.DayResource())
v1_api.register(manager_api.SetResource())
v1_api.register(manager_api.SettingResource())
v1_api.register(manager_api.WorkoutLogResource())
v1_api.register(manager_api.WorkoutSessionResource())

v1_api.register(weight_api.WeightEntryResource())

v1_api.register(core_api.LanguageResource())
v1_api.register(core_api.DaysOfWeekResource())
v1_api.register(core_api.UserProfileResource())
v1_api.register(core_api.LicenseResource())


### /api/v2 - django rest framework
router = routers.DefaultRouter()

# Manager app
router.register(r'workout', manager_api_views.WorkoutViewSet, base_name='workout')
router.register(r'workoutsession', manager_api_views.WorkoutSessionViewSet, base_name='workoutsession')
router.register(r'schedulestep', manager_api_views.ScheduleStepViewSet, base_name='schedulestep')
router.register(r'schedule', manager_api_views.ScheduleViewSet, base_name='schedule')
router.register(r'day', manager_api_views.DayViewSet, base_name='day')
router.register(r'set', manager_api_views.SetViewSet, base_name='Set')
router.register(r'setting', manager_api_views.SettingViewSet, base_name='Setting')
router.register(r'workoutlog', manager_api_views.WorkoutLogViewSet, base_name='workoutlog')

# Core app
router.register(r'userprofile', core_api_views.UserProfileViewSet, base_name='userprofile')
router.register(r'language', core_api_views.LanguageViewSet, base_name='language')
router.register(r'daysofweek', core_api_views.DaysOfWeekViewSet, base_name='daysofweek')
router.register(r'license', core_api_views.LicenseViewSet, base_name='license')

# Exercises app
router.register(r'exercise', exercises_api_views.ExerciseViewSet, base_name='exercise')
router.register(r'equipment', exercises_api_views.EquipmentViewSet, base_name='api')
router.register(r'exercisecategory', exercises_api_views.ExerciseCategoryViewSet, base_name='exercisecategory')
router.register(r'exerciseimage', exercises_api_views.ExerciseImageViewSet, base_name='exerciseimage')
router.register(r'exercisecomment', exercises_api_views.ExerciseCommentViewSet, base_name='exercisecomment')
router.register(r'muscle', exercises_api_views.MuscleViewSet, base_name='muscle')

# Nutrition app
router.register(r'ingredient', nutrition_api_views.IngredientViewSet, base_name='api-ingredient')
router.register(r'weightunit', nutrition_api_views.WeightUnitViewSet, base_name='weightunit')
router.register(r'ingredientweightunit', nutrition_api_views.IngredientWeightUnitViewSet, base_name='ingredientweightunit')
router.register(r'nutritionplan', nutrition_api_views.NutritionPlanViewSet, base_name='nutritionplan')
router.register(r'meal', nutrition_api_views.MealViewSet, base_name='meal')
router.register(r'mealitem', nutrition_api_views.MealItemViewSet, base_name='mealitem')

# Weight app
router.register(r'weightentry', weight_api_views.WeightEntryViewSet, base_name='weightentry')


from django.contrib import admin
admin.autodiscover()

#
# Sitemaps
#
sitemaps = {'exercises': ExercisesSitemap,
            'nutrition': NutritionSitemap}

#
# The actual URLs
#
urlpatterns = i18n_patterns('',
    url(r'^admin/', include(admin.site.urls)),
    url(r'^', include('wger.core.urls', namespace='core', app_name='core')),
    url(r'workout/', include('wger.manager.urls', namespace='manager')),
    url(r'exercise/', include('wger.exercises.urls', namespace='exercise')),
    url(r'weight/', include('wger.weight.urls', namespace='weight')),
    url(r'nutrition/', include('wger.nutrition.urls', namespace='nutrition')),
    url(r'software/', include('wger.software.urls', namespace='software', app_name='software')),
    url(r'config/', include('wger.config.urls', namespace='config', app_name='config')),
    url(r'gym/', include('wger.gym.urls', namespace='gym', app_name='gym')),
    url(r'^browserid/', include('django_browserid.urls')),
    url(r'^sitemap\.xml$',
        'django.contrib.sitemaps.views.sitemap',
        {'sitemaps': sitemaps},
        name='sitemap')
)

#
# URLs without language prefix
#
urlpatterns = urlpatterns + patterns('',
    url(r'^robots\.txt$',
        TextTemplateView.as_view(template_name="robots.txt"),
        name='robots'),
    url(r'^manifest\.webapp$', WebappManifestView.as_view(template_name="manifest.webapp")),
    url(r'^amazon-manifest\.webapp$', WebappManifestView.as_view(template_name="amazon-manifest.webapp")),

    # persona (browserID) login
    url(r'^browserid/', include('django_browserid.urls')),

    # API
    url(r'^api/', include(v1_api.urls)),
    url(r'^api/v2/exercise/search/$',
        exercises_api_views.search,
        name='exercise-search'),
    url(r'^api/v2/ingredient/search/$',
        nutrition_api_views.search,
        name='ingredient-search'),
    url(r'^api/v2/', include(router.urls)),
)
