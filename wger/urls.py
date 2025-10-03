# -*- coding: utf-8 -*-
# This file is part of wger Workout Manager.

# Django
from django.conf import settings
from django.conf.urls.i18n import i18n_patterns
from django.conf.urls.static import static
from django.contrib.sitemaps.views import index, sitemap
from django.urls import path, include

# Third Party
from django_email_verification import urls as email_urls
from drf_spectacular.views import SpectacularAPIView, SpectacularRedocView, SpectacularSwaggerView
from rest_framework import routers
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

# wger
from wger.core.api import views as core_api_views
from wger.exercises.api import views as exercises_api_views
from wger.exercises.sitemap import ExercisesSitemap
from wger.gallery.api import views as gallery_api_views
from wger.manager.api import views as manager_api_views
from wger.measurements.api import views as measurements_api_views
from wger.nutrition.api import views as nutrition_api_views
from wger.utils.generic_views import TextTemplateView
from wger.weight.api import views as weight_api_views

#
# REST API (v2)
#
router = routers.DefaultRouter()

# Manager app
router.register(r'routine', manager_api_views.RoutineViewSet, basename='routine')
router.register(r'templates', manager_api_views.UserRoutineTemplateViewSet, basename='templates')
router.register(r'public-templates', manager_api_views.PublicRoutineTemplateViewSet, basename='public-templates')
router.register(r'workoutsession', manager_api_views.WorkoutSessionViewSet, basename='workoutsession')
router.register(r'day', manager_api_views.RoutineDayViewSet, basename='day')
router.register(r'slot', manager_api_views.SlotViewSet, basename='slot')
router.register(r'slot-entry', manager_api_views.SlotEntryViewSet, basename='slot-entry')
router.register(r'weight-config', manager_api_views.WeightConfigViewSet, basename='weight-config')
router.register(r'max-weight-config', manager_api_views.MaxWeightConfigViewSet, basename='max-weight-config')
router.register(r'repetitions-config', manager_api_views.RepetitionsConfigViewSet, basename='repetitions-config')
router.register(r'max-repetitions-config', manager_api_views.MaxRepetitionsConfigViewSet, basename='max-repetitions-config')
router.register(r'sets-config', manager_api_views.SetsConfigViewSet, basename='sets-config')
router.register(r'max-sets-config', manager_api_views.MaxSetsConfigViewSet, basename='max-sets-config')
router.register(r'rest-config', manager_api_views.RestConfigViewSet, basename='rest-config')
router.register(r'max-rest-config', manager_api_views.MaxRestConfigViewSet, basename='max-rest-config')
router.register(r'rir-config', manager_api_views.RiRConfigViewSet, basename='rir-config')
router.register(r'max-rir-config', manager_api_views.MaxRiRConfigViewSet, basename='max-rir-config')
router.register(r'workoutlog', manager_api_views.WorkoutLogViewSet, basename='workoutlog')

# Core app
router.register(r'language', core_api_views.LanguageViewSet, basename='language')
router.register(r'license', core_api_views.LicenseViewSet, basename='license')
router.register(r'userprofile', core_api_views.UserProfileViewSet, basename='userprofile')
router.register(r'setting-repetitionunit', core_api_views.RepetitionUnitViewSet, basename='setting-repetition-unit')
router.register(r'setting-weightunit', core_api_views.RoutineWeightUnitViewSet, basename='setting-weight-unit')

# Exercises app
router.register(r'exerciseinfo', exercises_api_views.ExerciseInfoViewset, basename='exerciseinfo')
router.register(r'exercise-translation', exercises_api_views.ExerciseTranslationViewSet, basename='exercise-translation')
router.register(r'exercise', exercises_api_views.ExerciseViewSet, basename='exercise')
router.register(r'equipment', exercises_api_views.EquipmentViewSet, basename='equipment')
router.register(r'deletion-log', exercises_api_views.DeletionLogViewSet, basename='deletion-log')
router.register(r'exercisecategory', exercises_api_views.ExerciseCategoryViewSet, basename='exercisecategory')
router.register(r'video', exercises_api_views.ExerciseVideoViewSet, basename='video')
router.register(r'exerciseimage', exercises_api_views.ExerciseImageViewSet, basename='exerciseimage')
router.register(r'exercisecomment', exercises_api_views.ExerciseCommentViewSet, basename='exercisecomment')
router.register(r'exercisealias', exercises_api_views.ExerciseAliasViewSet, basename='exercisealias')
router.register(r'muscle', exercises_api_views.MuscleViewSet, basename='muscle')
router.register(r'variation', exercises_api_views.ExerciseVariationViewSet, basename='variation')

# Nutrition app
router.register(r'ingredient', nutrition_api_views.IngredientViewSet, basename='api-ingredient')
router.register(r'ingredientinfo', nutrition_api_views.IngredientInfoViewSet, basename='api-ingredientinfo')
router.register(r'weightunit', nutrition_api_views.WeightUnitViewSet, basename='weightunit')
router.register(r'ingredientweightunit', nutrition_api_views.IngredientWeightUnitViewSet, basename='ingredientweightunit')
router.register(r'nutritionplan', nutrition_api_views.NutritionPlanViewSet, basename='nutritionplan')
router.register(r'nutritionplaninfo', nutrition_api_views.NutritionPlanInfoViewSet, basename='nutritionplaninfo')
router.register(r'nutritiondiary', nutrition_api_views.LogItemViewSet, basename='nutritiondiary')
router.register(r'meal', nutrition_api_views.MealViewSet, basename='meal')
router.register(r'mealitem', nutrition_api_views.MealItemViewSet, basename='mealitem')
router.register(r'ingredient-image', nutrition_api_views.ImageViewSet, basename='ingredientimage')

# Weight app
router.register(r'weightentry', weight_api_views.WeightEntryViewSet, basename='weightentry')

# Gallery app
router.register(r'gallery', gallery_api_views.GalleryImageViewSet, basename='gallery')

# Measurements app
router.register(r'measurement', measurements_api_views.MeasurementViewSet, basename='measurement')
router.register(r'measurement-category', measurements_api_views.CategoryViewSet, basename='measurement-category')

#
# Sitemaps
#
sitemaps = {
    'exercises': ExercisesSitemap,
}

#
# Localized URLs (language-prefixed)
#
urlpatterns = i18n_patterns(
    path('', include(('wger.core.urls', 'core'), namespace='core')),
    path('routine/', include(('wger.manager.urls', 'manager'), namespace='manager')),
    path('exercise/', include(('wger.exercises.urls', 'exercise'), namespace='exercise')),
    path('weight/', include(('wger.weight.urls', 'weight'), namespace='weight')),
    path('nutrition/', include(('wger.nutrition.urls', 'nutrition'), namespace='nutrition')),
    path('software/', include(('wger.software.urls', 'software'), namespace='software')),
    path('config/', include(('wger.config.urls', 'config'), namespace='config')),
    path('gym/', include(('wger.gym.urls', 'gym'), namespace='gym')),
    path('gallery/', include(('wger.gallery.urls', 'gallery'), namespace='gallery')),
    path('measurement/', include(('wger.measurements.urls', 'measurements'), namespace='measurements')),
    path('email/', include(('wger.mailer.urls', 'email'), namespace='email')),
    path('sitemap.xml', index, {'sitemaps': sitemaps}, name='sitemap'),
    path('sitemap-<section>.xml', sitemap, {'sitemaps': sitemaps}, name='django.contrib.sitemaps.views.sitemap'),
)

#
# URLs without language prefix (API and misc)
#
urlpatterns += [
    path('robots.txt', TextTemplateView.as_view(template_name='robots.txt'), name='robots'),

    # API v2
    path('api/v2/exercise/search/', exercises_api_views.search, name='exercise-search'),
    path('api/v2/exercise-submission/', exercises_api_views.ExerciseSubmissionViewSet.as_view(), name='exercise-submission'),
    path('api/v2/ingredient/search/', nutrition_api_views.search, name='ingredient-search'),
    path('api/v2/check-language/', core_api_views.check_language, name='check-language'),
    path('api/v2/', include(router.urls)),

    # Custom endpoint for native "My exercises" search
    path('api/v2/my-custom-exercise/search/', manager_api_views.MyCustomExerciseSearchView.as_view(), name='my-custom-exercise-search'),

    # API auth
    path('api/v2/login/', core_api_views.UserAPILoginView.as_view({'post': 'post'}), name='api_user'),
    path('api/v2/register/', core_api_views.UserAPIRegistrationViewSet.as_view({'post': 'post'}), name='api_register'),
    path('api/v2/token', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v2/token/refresh', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v2/token/verify', TokenVerifyView.as_view(), name='token_verify'),

    # API metadata
    path('api/v2/version/', core_api_views.ApplicationVersionView.as_view({'get': 'get'}), name='app_version'),
    path('api/v2/check-permission/', core_api_views.PermissionView.as_view({'get': 'get'}), name='permission'),
    path('api/v2/min-app-version/', core_api_views.RequiredApplicationVersionView.as_view({'get': 'get'}), name='min_app_version'),
    path('api/v2/min-server-version/', core_api_views.RequiredServerVersionView.as_view({'get': 'get'}), name='min_server_version'),

    # API documentation
    path('api/v2/schema', SpectacularAPIView.as_view(), name='schema'),
    path('api/v2/schema/ui', SpectacularSwaggerView.as_view(url_name='schema'), name='api-swagger-ui'),
    path('api/v2/schema/redoc', SpectacularRedocView.as_view(url_name='schema'), name='api-redoc'),

    # Email verification
    path('email/', include(email_urls)),
]

# Development-only media
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Prometheus metrics
if settings.EXPOSE_PROMETHEUS_METRICS:
    urlpatterns += [path('prometheus/', include('django_prometheus.urls'))]
