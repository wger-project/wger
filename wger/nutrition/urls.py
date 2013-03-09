from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required

from wger.nutrition.views import IngredientCreateView
from wger.nutrition.views import IngredientEditView
from wger.nutrition.views import IngredientDeleteView
from wger.nutrition.views import PlanDeleteView
from wger.nutrition.views import PlanEditView
from wger.nutrition.views import MealCreateView
from wger.nutrition.views import MealEditView

from wger.nutrition.views import WeightUnitListView
from wger.nutrition.views import WeightUnitCreateView
from wger.nutrition.views import WeightUnitDeleteView
from wger.nutrition.views import WeightUnitUpdateView

urlpatterns = patterns('wger.nutrition.views',
    url(r'^overview/$', 'overview'),

    # Plans
    url(r'^add/$', 'add'),
    url(r'^(?P<id>\d+)/view/$', 'view'),

    url(r'^(?P<pk>\d+)/copy/$',
        'copy',
        name='nutrition-copy'),

    url(r'^(?P<pk>\d+)/delete/$',
        login_required(PlanDeleteView.as_view()),
        name='nutrition-delete'),
    url(r'^(?P<pk>\d+)/edit/$',
        login_required(PlanEditView.as_view()),
        name='nutrition-edit'),
    url(r'^(?P<id>\d+)/pdf/$', 'export_pdf'),

    # Meals
    url(r'^(?P<plan_pk>\d+)/meal/add/$',
        login_required(MealCreateView.as_view()),
        name='meal-add'),
    url(r'^meal/(?P<pk>\d+)/edit/$',
        login_required(MealEditView.as_view()),
        name='meal-edit'),

    url(r'^(?P<id>\d+)/delete/meal/$', 'delete_meal'),

    # Meal items
    url(r'^(?P<id>\d+)/edit/meal/(?P<meal_id>\d+)/item/(?P<item_id>\w*)$', 'edit_meal_item'),
    url(r'^delete/meal/item/(?P<item_id>\d+)$', 'delete_meal_item'),

    # Ingredients
    url(r'^ingredient/(?P<pk>\d+)/delete/$',
        permission_required('exercises.change_exercise')(IngredientDeleteView.as_view()),
        name='ingredient-delete'),

    url(r'^ingredient/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercise')(IngredientEditView.as_view()),
        name='ingredient-edit'),

    url(r'^ingredient/add/$',
        permission_required('exercises.change_exercise')(IngredientCreateView.as_view()),
        name='ingredient-add'),

    url(r'^ingredient/overview/$', 'ingredient_overview'),
    url(r'^ingredient/(?P<id>\d+)/view/$', 'ingredient_view'),
    url(r'^ingredient/(?P<id>\d+)/view/(?P<slug>[-\w]+)/$', 'ingredient_view'),
    url(r'^ingredient/search/$', 'ingredient_search'),

    # Ingredient units
    url(r'^ingredient/unit/list/$',
        permission_required('exercises.change_exercise')(WeightUnitListView.as_view()),
        name='weight-unit-list'),
    url(r'^ingredient/unit/add/$',
        permission_required('exercises.change_exercise')(WeightUnitCreateView.as_view()),
        name='weight-unit-add'),
    url(r'^ingredient/unit/(?P<pk>\d+)/delete/$',
        permission_required('exercises.change_exercise')(WeightUnitDeleteView.as_view()),
        name='weight-unit-delete'),
    url(r'^ingredient/unit/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercise')(WeightUnitUpdateView.as_view()),
        name='weight-unit-edit'),
        

    # Ingredient to weight units cross table
    #url(r'^ingredient/unit/add-to-ingredient/$',
    #    permission_required('exercises.change_exercise')(WeightUnitCreateView.as_view()),
    #    name='weight-unit-add'),
)
