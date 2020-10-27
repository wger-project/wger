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
from django.conf.urls import (
    include,
    url
)
from django.contrib.auth.decorators import login_required
from django.urls import path

# wger
from wger.nutrition.views import (
    bmi,
    calculator,
    ingredient,
    log,
    meal,
    meal_item,
    plan,
    unit,
    unit_ingredient
)


# sub patterns for nutritional plans
patterns_plan = [
    path('overview/',
         plan.overview,
         name='overview'),
    path('add/',
         plan.add,
         name='add'),
    path('<int:id>/view/',
         plan.view,
         name='view'),
    path('<int:pk>/copy/',
         plan.copy,
         name='copy'),
    path('<int:pk>/delete/',
         login_required(plan.PlanDeleteView.as_view()),
         name='delete'),
    path('<int:pk>/edit/',
         login_required(plan.PlanEditView.as_view()),
         name='edit'),
    url(r'^(?P<id>\d+)/pdf/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,33})',
        plan.export_pdf,
        name='export-pdf'),
    path('<int:id>/pdf/',
         plan.export_pdf,
         name='export-pdf'),
]


# sub patterns for meals
patterns_meal = [
    path('<int:plan_pk>/meal/add/',
         login_required(meal.MealCreateView.as_view()),
         name='add'),
    path('<int:pk>/edit/',
         login_required(meal.MealEditView.as_view()),
         name='edit'),
    path('<int:id>/delete/',
         meal.delete_meal,
         name='delete'),
]


# sub patterns for meal items
patterns_meal_item = [
    path('<int:meal_id>/item/add/',
         login_required(meal_item.MealItemCreateView.as_view()),
         name='add'),
    path('<int:pk>/edit/',
         login_required(meal_item.MealItemEditView.as_view()),
         name='edit'),
    path('<int:item_id>/delete/',
         meal_item.delete_meal_item,
         name='delete'),
]


# sub patterns for ingredient
patterns_ingredient = [
    path('<int:pk>/delete/',
         ingredient.IngredientDeleteView.as_view(),
         name='delete'),
    path('<int:pk>/edit/',
         ingredient.IngredientEditView.as_view(),
         name='edit'),
    path('add/',
         login_required(ingredient.IngredientCreateView.as_view()),
         name='add'),
    path('overview/',
         ingredient.IngredientListView.as_view(),
         name='list'),
    path('pending/',
         ingredient.PendingIngredientListView.as_view(),
         name='pending'),
    path('<int:pk>/accept/',
         ingredient.accept,
         name='accept'),
    path('<int:pk>/decline/',
         ingredient.decline,
         name='decline'),
    path('<int:id>/view/',
         ingredient.view,
         name='view'),
    path('<int:id>/view/<slug:slug>/',
         ingredient.view,
         name='view'),
]


# sub patterns for weight units
patterns_weight_unit = [
    path('list/',
         unit.WeightUnitListView.as_view(),
         name='list'),
    path('add/',
         unit.WeightUnitCreateView.as_view(),
         name='add'),
    path('<int:pk>/delete/',
         unit.WeightUnitDeleteView.as_view(),
         name='delete'),
    path('<int:pk>/edit/',
         unit.WeightUnitUpdateView.as_view(),
         name='edit'),
]


# sub patterns for weight units / ingredient cross table
patterns_unit_ingredient = [
    path('add/<int:ingredient_pk>/',
         unit_ingredient.WeightUnitIngredientCreateView.as_view(),
         name='add'),
    path('<int:pk>/edit/',
         unit_ingredient.WeightUnitIngredientUpdateView.as_view(),
         name='edit'),
    path('<int:pk>/delete/',
         unit_ingredient.WeightUnitIngredientDeleteView.as_view(),
         name='delete'),
]


# sub patterns for BMI calculator
patterns_bmi = [
    path('',
         bmi.view,
         name='view'),
    path('calculate',
         bmi.calculate,
         name='calculate'),
    path('chart-data',
         bmi.chart_data,
         name='chart-data'),  # JS
]


# sub patterns for calories calculator
patterns_calories = [
    path('',
         calculator.view,
         name='view'),
    path('bmr',
         calculator.calculate_bmr,
         name='bmr'),
    path('activities',
         calculator.calculate_activities,
         name='activities'),  # JS
]

# sub patterns for calories dairy
patterns_diary = [
    path('<int:pk>',
         log.overview,
         name='overview'),
    url(r'^(?P<pk>\d+)/(?P<year>\d{4})-(?P<month>\d{1,2})-(?P<day>\d{1,2})$',
        log.detail,
        name='detail'),
    path('entry/<int:pk>/delete',
         log.LogDeleteView.as_view(),
         name='delete'),
    path('plan/<int:plan_pk>/add',
         log.LogCreateView.as_view(),
         name='add'),
    path('log-meal/<int:meal_pk>',
         log.log_meal,
         name='log_meal'),
    path('log-plan/<int:plan_pk>',
         log.log_plan,
         name='log_plan')
]


urlpatterns = [
    path('', include((patterns_plan, "plan"), namespace="plan")),
    path('meal/', include((patterns_meal, "meal"), namespace="meal")),
    path('meal/item/', include((patterns_meal_item, "meal_item"), namespace="meal_item")),
    path('ingredient/', include((patterns_ingredient, "ingredient"), namespace="ingredient")),
    path('unit/', include((patterns_weight_unit, "weight_unit"), namespace="weight_unit")),
    path('unit-to-ingredient/', include((patterns_unit_ingredient, "unit_ingredient"), namespace="unit_ingredient")),
    path('calculator/bmi/', include((patterns_bmi, "bmi"), namespace="bmi")),
    path('calculator/calories/', include((patterns_calories, "calories"), namespace="calories")),
    path('diary/', include((patterns_diary, "log"), namespace="log")),
]
