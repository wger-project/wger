from django.conf.urls import patterns, url
from django.contrib.auth.decorators import permission_required
from django.contrib.auth.decorators import login_required

from nutrition.views import IngredientCreateView
from nutrition.views import IngredientEditView
from nutrition.views import IngredientDeleteView
from nutrition.views import PlanDeleteView
from nutrition.views import PlanEditView
from nutrition.views import MealCreateView
from nutrition.views import MealEditView


urlpatterns = patterns('nutrition.views',
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
)
