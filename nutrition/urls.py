from django.conf.urls import patterns, include, url
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required

from nutrition.views import IngredientDeleteView
from nutrition.views import PlanDeleteView
from nutrition.views import PlanEditView
from nutrition.views import MealCreateView
from nutrition.views import MealEditView


urlpatterns = patterns('nutrition.views',
    url(r'^nutrition/overview/$', 'overview'),
    
    # Plans
    url(r'^nutrition/add/$', 'add'),
    url(r'^nutrition/(?P<id>\d+)/view/$', 'view'),
    url(r'^nutrition/(?P<pk>\d+)/delete/$',
        login_required(PlanDeleteView.as_view()),
        name='nutrition-delete'),
    url(r'^nutrition/(?P<pk>\d+)/edit/$',
        login_required(PlanEditView.as_view()),
        name='nutrition-edit'),
    url(r'^nutrition/(?P<id>\d+)/pdf/$', 'export_pdf'),
    
    # Meals
    url(r'^nutrition/(?P<plan_pk>\d+)/meal/add/$',
        login_required(MealCreateView.as_view()),
        name='meal-add'),
    url(r'^nutrition/meal/(?P<pk>\d+)/edit/$',
        login_required(MealEditView.as_view()),
        name='meal-edit'),
    
    url(r'^nutrition/(?P<id>\d+)/delete/meal/$', 'delete_meal'),
    
    # Meal items
    url(r'^nutrition/(?P<id>\d+)/edit/meal/(?P<meal_id>\d+)/item/(?P<item_id>\w*)$', 'edit_meal_item'),
    url(r'^nutrition/delete/meal/item/(?P<item_id>\d+)$', 'delete_meal_item'),
    
    # Ingredients
    url(r'^nutrition/ingredient/(?P<pk>\d+)/deleteGV/$',
        permission_required('exercises.change_exercise')(IngredientDeleteView.as_view()),
        name='ingredient-delete'),
    
    url(r'^nutrition/ingredient/overview/$', 'ingredient_overview'),
    url(r'^nutrition/ingredient/(?P<id>\d+)/view/$', 'ingredient_view'),
    url(r'^nutrition/ingredient/(?P<id>\w*)/edit/$', 'ingredient_edit'),
    url(r'^nutrition/ingredient/search/$', 'ingredient_search'),
)
