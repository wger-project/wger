from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required

from wger.nutrition.views.ingredient import IngredientCreateView
from wger.nutrition.views.ingredient import IngredientEditView
from wger.nutrition.views.ingredient import IngredientDeleteView

from wger.nutrition.views.plan import PlanDeleteView
from wger.nutrition.views.plan import PlanEditView

from wger.nutrition.views.meal import MealCreateView
from wger.nutrition.views.meal import MealEditView

from wger.nutrition.views.unit import WeightUnitListView
from wger.nutrition.views.unit import WeightUnitCreateView
from wger.nutrition.views.unit import WeightUnitDeleteView
from wger.nutrition.views.unit import WeightUnitUpdateView

from wger.nutrition.views.unit_ingredient import WeightUnitIngredientCreateView
from wger.nutrition.views.unit_ingredient import WeightUnitIngredientUpdateView
from wger.nutrition.views.unit_ingredient import WeightUnitIngredientDeleteView

urlpatterns = patterns('wger.nutrition.views',
    url(r'^overview/$', 'plan.overview'),

    # Plans
    url(r'^add/$', 'plan.add'),
    url(r'^(?P<id>\d+)/view/$', 'plan.view'),

    url(r'^(?P<pk>\d+)/copy/$',
        'plan.copy',
        name='nutrition-copy'),

    url(r'^(?P<pk>\d+)/delete/$',
        login_required(PlanDeleteView.as_view()),
        name='nutrition-delete'),
    url(r'^(?P<pk>\d+)/edit/$',
        login_required(PlanEditView.as_view()),
        name='nutrition-edit'),
    url(r'^(?P<id>\d+)/pdf/$', 'plan.export_pdf'),

    # Meals
    url(r'^(?P<plan_pk>\d+)/meal/add/$',
        login_required(MealCreateView.as_view()),
        name='meal-add'),
    url(r'^meal/(?P<pk>\d+)/edit/$',
        login_required(MealEditView.as_view()),
        name='meal-edit'),

    url(r'^(?P<id>\d+)/delete/meal/$', 'meal.delete_meal'),

    # Meal items
    url(r'^(?P<id>\d+)/edit/meal/(?P<meal_id>\d+)/item/(?P<item_id>\w*)$', 'ingredient.edit_meal_item'),
    url(r'^delete/meal/item/(?P<item_id>\d+)$', 'ingredient.delete_meal_item'),

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

    url(r'^ingredient/overview/$', 'ingredient.ingredient_overview'),
    url(r'^ingredient/(?P<id>\d+)/view/$', 'ingredient.ingredient_view'),
    url(r'^ingredient/(?P<id>\d+)/view/(?P<slug>[-\w]+)/$', 'ingredient.ingredient_view'),
    url(r'^ingredient/search/$',
        'ingredient.ingredient_search',
        name='ingredient-search'),
    url(r'^ingredient/(?P<pk>\d+)/get-units$',
        'ingredient.ajax_get_ingredient_units',
        name='ingredient-get-units'),

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
    url(r'^ingredient/unit-to-ingredient/add/(?P<ingredient_pk>\d+)/$',
        permission_required('exercises.change_exercise')(WeightUnitIngredientCreateView.as_view()),
        name='weight-unit-ingredient-add'),
    url(r'^ingredient/unit-to-ingredient/(?P<pk>\d+)/edit/$',
        permission_required('exercises.change_exercise')(WeightUnitIngredientUpdateView.as_view()),
        name='weight-unit-ingredient-edit'),
    url(r'^ingredient/unit-to-ingredient/(?P<pk>\d+)/delete/$',
        permission_required('exercises.change_exercise')(WeightUnitIngredientDeleteView.as_view()),
        name='weight-unit-ingredient-delete'),
)
