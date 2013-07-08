from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required

from wger.nutrition.views import ingredient
from wger.nutrition.views import plan
from wger.nutrition.views import meal
from wger.nutrition.views import meal_item
from wger.nutrition.views import unit
from wger.nutrition.views import unit_ingredient

urlpatterns = patterns('wger.nutrition.views',
    # Plans
    url(r'^overview/$',
        'plan.overview',
        name='nutrition-overview'),
    url(r'^add/$', 'plan.add'),
    url(r'^(?P<id>\d+)/view/$', 'plan.view'),
    url(r'^(?P<pk>\d+)/copy/$',
        'plan.copy',
        name='nutrition-copy'),
    url(r'^(?P<pk>\d+)/delete/$',
        login_required(plan.PlanDeleteView.as_view()),
        name='nutrition-delete'),
    url(r'^(?P<pk>\d+)/edit/$',
        login_required(plan.PlanEditView.as_view()),
        name='nutrition-edit'),
    url(r'^(?P<id>\d+)/pdf/$', 'plan.export_pdf'),

    # Meals
    url(r'^(?P<plan_pk>\d+)/meal/add/$',
        login_required(meal.MealCreateView.as_view()),
        name='meal-add'),
    url(r'^meal/(?P<pk>\d+)/edit/$',
        login_required(meal.MealEditView.as_view()),
        name='meal-edit'),
    url(r'^meal/(?P<id>\d+)/delete/$', 'meal.delete_meal'),

    # Meal items
    url(r'^meal/(?P<meal_id>\d+)/item/add/$',
        login_required(meal_item.MealItemCreateView.as_view()),
        name='mealitem-add'),
    url(r'^meal/item/(?P<pk>\d+)/edit/$',
        login_required(meal_item.MealItemEditView.as_view()),
        name='mealitem-edit'),
    url(r'^meal/item/(?P<item_id>\d+)/delete/$', 'meal_item.delete_meal_item'),

    # Ingredients
    url(r'^ingredient/(?P<pk>\d+)/delete/$',
        permission_required('nutrition.delete_ingredient')(ingredient.IngredientDeleteView.as_view()),
        name='ingredient-delete'),
    url(r'^ingredient/(?P<pk>\d+)/edit/$',
        permission_required('nutrition.change_ingredient')(ingredient.IngredientEditView.as_view()),
        name='ingredient-edit'),
    url(r'^ingredient/add/$',
        login_required(ingredient.IngredientCreateView.as_view()),
        name='ingredient-add'),
    url(r'^ingredient/overview/$',
        ingredient.IngredientListView.as_view(),
        name='ingredient-list'),
    url(r'^pending/$',
        permission_required('nutrition.change_ingredient')(ingredient.PendingIngredientListView.as_view()),
        name='ingredient-pending'),
    url(r'^(?P<pk>\d+)/accept/$',
        'ingredient.accept',
        name='ingredient-accept'),
    url(r'^(?P<pk>\d+)/decline/$',
        'ingredient.decline',
        name='ingredient-decline'),
    url(r'^ingredient/(?P<id>\d+)/view/$',
        'ingredient.view',
        name='ingredient-view'),
    url(r'^ingredient/(?P<id>\d+)/view/(?P<slug>[-\w]+)/$', 'ingredient.view'),
    url(r'^ingredient/search/$',
        'ingredient.search',
        name='ingredient-search'),
    url(r'^ingredient/(?P<pk>\d+)/get-units$',
        'ingredient.ajax_get_ingredient_units',
        name='ingredient-get-units'),
    url(r'^ingredient/(?P<pk>\d+)/get-nutritional-values$',
        'ingredient.ajax_get_ingredient_values',
        name='ingredient-get-values'),

    # Ingredient units
    url(r'^ingredient/unit/list/$',
        permission_required('nutrition.add_ingredientweightunit')(unit.WeightUnitListView.as_view()),
        name='weight-unit-list'),
    url(r'^ingredient/unit/add/$',
        permission_required('nutrition.add_ingredientweightunit')(unit.WeightUnitCreateView.as_view()),
        name='weight-unit-add'),
    url(r'^ingredient/unit/(?P<pk>\d+)/delete/$',
        permission_required('nutrition.delete_ingredientweightunit')(unit.WeightUnitDeleteView.as_view()),
        name='weight-unit-delete'),
    url(r'^ingredient/unit/(?P<pk>\d+)/edit/$',
        permission_required('nutrition.change_ingredientweightunit')(unit.WeightUnitUpdateView.as_view()),
        name='weight-unit-edit'),
        

    # Ingredient to weight units cross table
    url(r'^ingredient/unit-to-ingredient/add/(?P<ingredient_pk>\d+)/$',
        permission_required('nutrition.add_ingredientweightunit')(unit_ingredient.WeightUnitIngredientCreateView.as_view()),
        name='weight-unit-ingredient-add'),
    url(r'^ingredient/unit-to-ingredient/(?P<pk>\d+)/edit/$',
        permission_required('nutrition.add_ingredientweightunit')(unit_ingredient.WeightUnitIngredientUpdateView.as_view()),
        name='weight-unit-ingredient-edit'),
    url(r'^ingredient/unit-to-ingredient/(?P<pk>\d+)/delete/$',
        permission_required('nutrition.add_ingredientweightunit')(unit_ingredient.WeightUnitIngredientDeleteView.as_view()),
        name='weight-unit-ingredient-delete'),
)
