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

from django.contrib.auth.decorators import login_required
from django.conf.urls import (
    patterns,
    url,
    include
)

from wger.nutrition.views import (
    ingredient,
    bmi,
    calculator,
    plan,
    meal,
    meal_item,
    unit,
    unit_ingredient
)

# sub patterns for nutritional plans
patterns_plan = [
    url(r'^overview/$',
        plan.overview,
        name='overview'),
    url(r'^add/$',
        plan.add,
        name='add'),
    url(r'^(?P<id>\d+)/view/$',
        plan.view,
        name='view'),
    url(r'^(?P<pk>\d+)/copy/$',
        plan.copy,
        name='copy'),
    url(r'^(?P<pk>\d+)/delete/$',
        login_required(plan.PlanDeleteView.as_view()),
        name='delete'),
    url(r'^(?P<pk>\d+)/edit/$',
        login_required(plan.PlanEditView.as_view()),
        name='edit'),
    url(r'^(?P<id>\d+)/pdf/(?P<uidb64>[0-9A-Za-z_\-]+)/(?P<token>[0-9A-Za-z]{1,13}-[0-9A-Za-z]{1,20})$',
        plan.export_pdf,
        name='export-pdf'),
    url(r'^(?P<id>\d+)/pdf/$',
        plan.export_pdf,
        name='export-pdf'),
]


# sub patterns for meals
patterns_meal = [
    url(r'^(?P<plan_pk>\d+)/meal/add/$',
        login_required(meal.MealCreateView.as_view()),
        name='add'),
    url(r'^(?P<pk>\d+)/edit/$',
        login_required(meal.MealEditView.as_view()),
        name='edit'),
    url(r'^(?P<id>\d+)/delete/$',
        meal.delete_meal,
        name='delete'),
]


# sub patterns for meal items
patterns_meal_item = [
    url(r'^(?P<meal_id>\d+)/item/add/$',
        login_required(meal_item.MealItemCreateView.as_view()),
        name='add'),
    url(r'^(?P<pk>\d+)/edit/$',
        login_required(meal_item.MealItemEditView.as_view()),
        name='edit'),
    url(r'^(?P<item_id>\d+)/delete/$',
        meal_item.delete_meal_item,
        name='delete'),
]


# sub patterns for ingredient
patterns_ingredient = [
    url(r'^(?P<pk>\d+)/delete/$',
        ingredient.IngredientDeleteView.as_view(),
        name='delete'),
    url(r'^(?P<pk>\d+)/edit/$',
        ingredient.IngredientEditView.as_view(),
        name='edit'),
    url(r'^add/$',
        login_required(ingredient.IngredientCreateView.as_view()),
        name='add'),
    url(r'^overview/$',
        ingredient.IngredientListView.as_view(),
        name='list'),
    url(r'^pending/$',
        ingredient.PendingIngredientListView.as_view(),
        name='pending'),
    url(r'^(?P<pk>\d+)/accept/$',
        ingredient.accept,
        name='accept'),
    url(r'^(?P<pk>\d+)/decline/$',
        ingredient.decline,
        name='decline'),
    url(r'^(?P<id>\d+)/view/$',
        ingredient.view,
        name='view'),
    url(r'^(?P<id>\d+)/view/(?P<slug>[-\w]+)/$',
        ingredient.view,
        name='view'),
]


# sub patterns for weight units
patterns_weight_unit = [
    url(r'^list/$',
        unit.WeightUnitListView.as_view(),
        name='list'),
    url(r'^add/$',
        unit.WeightUnitCreateView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/delete/$',
        unit.WeightUnitDeleteView.as_view(),
        name='delete'),
    url(r'^(?P<pk>\d+)/edit/$',
        unit.WeightUnitUpdateView.as_view(),
        name='edit'),
]


# sub patterns for weight units / ingredient cross table
patterns_unit_ingredient = [
    url(r'^add/(?P<ingredient_pk>\d+)/$',
        unit_ingredient.WeightUnitIngredientCreateView.as_view(),
        name='add'),
    url(r'^(?P<pk>\d+)/edit/$',
        unit_ingredient.WeightUnitIngredientUpdateView.as_view(),
        name='edit'),
    url(r'^(?P<pk>\d+)/delete/$',
        unit_ingredient.WeightUnitIngredientDeleteView.as_view(),
        name='delete'),
]


# sub patterns for BMI calculator
patterns_bmi = [
    url(r'^$',
        bmi.view,
        name='view'),
    url(r'^calculate$',
        bmi.calculate,
        name='calculate'),
    url(r'^chart-data$',
        bmi.chart_data,
        name='chart-data'),  # JS
]


# sub patterns for calories calculator
patterns_calories = [
    url(r'^$',
        calculator.view,
        name='view'),
    url(r'^bmr$',
        calculator.calculate_bmr,
        name='bmr'),
    url(r'^activities$',
        calculator.calculate_activities,
        name='activities'),  # JS
]


urlpatterns = [
   url(r'^', include(patterns_plan, namespace="plan")),
   url(r'^meal/', include(patterns_meal, namespace="meal")),
   url(r'^meal/item/', include(patterns_meal_item, namespace="meal_item")),
   url(r'^ingredient/', include(patterns_ingredient, namespace="ingredient")),
   url(r'^unit/', include(patterns_weight_unit, namespace="weight_unit")),
   url(r'^unit-to-ingredient/', include(patterns_unit_ingredient, namespace="unit_ingredient")),
   url(r'^calculator/bmi/', include(patterns_bmi, namespace="bmi")),
   url(r'^calculator/calories/', include(patterns_calories, namespace="calories")),
]
