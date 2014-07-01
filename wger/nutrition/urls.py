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

from django.conf.urls import patterns, url
from django.contrib.auth.decorators import login_required

from wger.nutrition.views import ingredient
from wger.nutrition.views import bmi
from wger.nutrition.views import calculator
from wger.nutrition.views import plan
from wger.nutrition.views import meal
from wger.nutrition.views import meal_item
from wger.nutrition.views import unit
from wger.nutrition.views import unit_ingredient

urlpatterns = patterns('wger.nutrition.views',
    # Plans
    url(r'^overview/$',
        plan.overview,
        name='nutrition-overview'),
    url(r'^add/$',
        plan.add,
        name='nutrition-add'),
    url(r'^(?P<id>\d+)/view/$',
        plan.view,
        name='nutrition-view'),
    url(r'^(?P<pk>\d+)/copy/$',
        plan.copy,
        name='nutrition-copy'),
    url(r'^(?P<pk>\d+)/delete/$',
        login_required(plan.PlanDeleteView.as_view()),
        name='nutrition-delete'),
    url(r'^(?P<pk>\d+)/edit/$',
        login_required(plan.PlanEditView.as_view()),
        name='nutrition-edit'),
    url(r'^(?P<id>\d+)/pdf/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        plan.export_pdf,
        name='nutrition-export-pdf'),
    url(r'^(?P<id>\d+)/pdf/$',
        plan.export_pdf,
        name='nutrition-export-pdf'),

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
        ingredient.IngredientDeleteView.as_view(),
        name='ingredient-delete'),
    url(r'^ingredient/(?P<pk>\d+)/edit/$',
        ingredient.IngredientEditView.as_view(),
        name='ingredient-edit'),
    url(r'^ingredient/add/$',
        login_required(ingredient.IngredientCreateView.as_view()),
        name='ingredient-add'),
    url(r'^ingredient/overview/$',
        ingredient.IngredientListView.as_view(),
        name='ingredient-list'),
    url(r'^pending/$',
        ingredient.PendingIngredientListView.as_view(),
        name='ingredient-pending'),
    url(r'^(?P<pk>\d+)/accept/$',
        ingredient.accept,
        name='ingredient-accept'),
    url(r'^(?P<pk>\d+)/decline/$',
        ingredient.decline,
        name='ingredient-decline'),
    url(r'^ingredient/(?P<id>\d+)/view/$',
        ingredient.view,
        name='ingredient-view'),
    url(r'^ingredient/(?P<id>\d+)/view/(?P<slug>[-\w]+)/$',
        ingredient.view,
        name='ingredient-view'),

    # Ingredient units
    url(r'^ingredient/unit/list/$',
        unit.WeightUnitListView.as_view(),
        name='weight-unit-list'),
    url(r'^ingredient/unit/add/$',
        unit.WeightUnitCreateView.as_view(),
        name='weight-unit-add'),
    url(r'^ingredient/unit/(?P<pk>\d+)/delete/$',
        unit.WeightUnitDeleteView.as_view(),
        name='weight-unit-delete'),
    url(r'^ingredient/unit/(?P<pk>\d+)/edit/$',
        unit.WeightUnitUpdateView.as_view(),
        name='weight-unit-edit'),

    # Ingredient to weight units cross table
    url(r'^ingredient/unit-to-ingredient/add/(?P<ingredient_pk>\d+)/$',
        unit_ingredient.WeightUnitIngredientCreateView.as_view(),
        name='weight-unit-ingredient-add'),
    url(r'^ingredient/unit-to-ingredient/(?P<pk>\d+)/edit/$',
        unit_ingredient.WeightUnitIngredientUpdateView.as_view(),
        name='weight-unit-ingredient-edit'),
    url(r'^ingredient/unit-to-ingredient/(?P<pk>\d+)/delete/$',
        unit_ingredient.WeightUnitIngredientDeleteView.as_view(),
        name='weight-unit-ingredient-delete'),

    # BMI
    url(r'^calculator/bmi$',
        bmi.view,
        name='bmi-view'),
    url(r'^calculator/bmi/calculate$',
        bmi.calculate,
        name='bmi-calculate'),
    url(r'^calculator/bmi/chart-data$',
        bmi.chart_data,
        name='bmi-chart-data'),  # JS

    # Calories calculator
    url(r'^calculator/calories$',
        calculator.view,
        name='calories-calculator'),
    url(r'^calculator/calories/bmr$',
        calculator.calculate_bmr,
        name='calories-calculate-bmr'),
    url(r'^calculator/calories/activities$',
        calculator.calculate_activities,
        name='calories-calculate-activities'),  # JS
)
