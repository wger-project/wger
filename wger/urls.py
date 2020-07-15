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

# Django
from django.conf import settings
from django.conf.urls import (
    include,
    url
)
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap

# Third Party
from rest_framework import routers
from tastypie.api import Api

# wger
from wger.core.api import (
    resources as core_api,
    views as core_api_views
)
from wger.exercises.api import (
    resources as exercises_api,
    views as exercises_api_views
)
from wger.exercises.sitemap import ExercisesSitemap
from wger.manager.api import (
    resources as manager_api,
    views as manager_api_views
)
from wger.nutrition.api import (
    resources as nutrition_api,
    views as nutrition_api_views
)
from wger.nutrition.sitemap import NutritionSitemap
from wger.utils.generic_views import (
    TextTemplateView,
    WebappManifestView
)
from wger.weight.api import (
    resources as weight_api,
    views as weight_api_views
)


admin.autodiscover()


#
# REST API
#

# /api/v1 - tastypie - deprecated
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


# /api/v2 - django rest framework
router = routers.DefaultRouter()

# Manager app
router.register(r'workout', manager_api_views.WorkoutViewSet, basename='workout')
router.register(r'workoutsession', manager_api_views.WorkoutSessionViewSet, basename='workoutsession')
router.register(r'schedulestep', manager_api_views.ScheduleStepViewSet, basename='schedulestep')
router.register(r'schedule', manager_api_views.ScheduleViewSet, basename='schedule')
router.register(r'day', manager_api_views.DayViewSet, basename='day')
router.register(r'set', manager_api_views.SetViewSet, basename='Set')
router.register(r'setting', manager_api_views.SettingViewSet, basename='Setting')
router.register(r'workoutlog', manager_api_views.WorkoutLogViewSet, basename='workoutlog')

# Core app
router.register(r'userprofile', core_api_views.UserProfileViewSet, basename='userprofile')
router.register(r'language', core_api_views.LanguageViewSet, basename='language')
router.register(r'daysofweek', core_api_views.DaysOfWeekViewSet, basename='daysofweek')
router.register(r'license', core_api_views.LicenseViewSet, basename='license')
router.register(r'setting-repetitionunit', core_api_views.RepetitionUnitViewSet, basename='setting-repetition-unit')
router.register(r'setting-weightunit', core_api_views.WeightUnitViewSet, basename='setting-weight-unit')

# Exercises app
# Add router for viewing exercise info
router.register(r'exerciseinfo', exercises_api_views.ExerciseInfoViewset, basename='exerciseinfo')
router.register(r'exercise', exercises_api_views.ExerciseViewSet, basename='exercise')
router.register(r'equipment', exercises_api_views.EquipmentViewSet, basename='api')
router.register(r'exercisecategory', exercises_api_views.ExerciseCategoryViewSet, basename='exercisecategory')
router.register(r'exerciseimage', exercises_api_views.ExerciseImageViewSet, basename='exerciseimage')
router.register(r'exercisecomment', exercises_api_views.ExerciseCommentViewSet, basename='exercisecomment')
router.register(r'muscle', exercises_api_views.MuscleViewSet, basename='muscle')

# Nutrition app
router.register(r'ingredient', nutrition_api_views.IngredientViewSet, basename='api-ingredient')
router.register(r'weightunit', nutrition_api_views.WeightUnitViewSet, basename='weightunit')
router.register(r'ingredientweightunit', nutrition_api_views.IngredientWeightUnitViewSet, basename='ingredientweightunit')
router.register(r'nutritionplan', nutrition_api_views.NutritionPlanViewSet, basename='nutritionplan')
router.register(r'meal', nutrition_api_views.MealViewSet, basename='meal')
router.register(r'mealitem', nutrition_api_views.MealItemViewSet, basename='mealitem')

# Weight app
router.register(r'weightentry', weight_api_views.WeightEntryViewSet, basename='weightentry')

#
# Sitemaps
#
sitemaps = {'exercises': ExercisesSitemap,
            'nutrition': NutritionSitemap}

#
# The actual URLs
#
urlpatterns = i18n_patterns(
    url(r'^admin/', admin.site.urls),
    url(r'^', include(('wger.core.urls', 'core'), namespace='core')),
    url(r'workout/', include(('wger.manager.urls', 'manager'), namespace='manager')),
    url(r'exercise/', include(('wger.exercises.urls', 'exercise'), namespace='exercise')),
    url(r'weight/', include(('wger.weight.urls', 'weight'), namespace='weight')),
    url(r'nutrition/', include(('wger.nutrition.urls', 'nutrition'), namespace='nutrition')),
    url(r'software/', include(('wger.software.urls', 'software'), namespace='software')),
    url(r'config/', include(('wger.config.urls', 'config'), namespace='config')),
    url(r'gym/', include(('wger.gym.urls', 'gym'), namespace='gym')),
    url(r'email/', include(('wger.email.urls', 'email'), namespace='email')),
    url(r'^sitemap\.xml$',
        sitemap,
        {'sitemaps': sitemaps},
        name='sitemap')
)

#
# URLs without language prefix
#
urlpatterns += [
    url(r'^robots\.txt$',
        TextTemplateView.as_view(template_name="robots.txt"),
        name='robots'),
    url(r'^manifest\.webapp$', WebappManifestView.as_view(template_name="manifest.webapp")),
    url(r'^amazon-manifest\.webapp$', WebappManifestView.as_view(template_name="amazon-manifest.webapp")),

    # API
    url(r'^api/', include(v1_api.urls)),
    url(r'^api/v2/exercise/search/$',
        exercises_api_views.search,
        name='exercise-search'),
    url(r'^api/v2/exerciseinfo/search/$',
        exercises_api_views.search,
        name='exercise-info'),
    url(r'^api/v2/ingredient/search/$',
        nutrition_api_views.search,
        name='ingredient-search'),
    url(r'^api/v2/', include(router.urls)),
]

#
# URL for user uploaded files, served like this during development only
#
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
