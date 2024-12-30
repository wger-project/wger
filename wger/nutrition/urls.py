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
from django.conf.urls import include
from django.contrib.auth.decorators import login_required
from django.urls import (
    path,
    re_path,
)

# wger
from wger.core.views.react import ReactView
from wger.nutrition.views import (
    calculator,
    ingredient,
    plan,
    unit,
    unit_ingredient,
)


# sub patterns for nutritional plans
patterns_plan = [
    path(
        'overview/',
        ReactView.as_view(login_required=True),
        name='overview',
    ),
    path(
        '<int:id>/view/',
        ReactView.as_view(login_required=True),
        name='view',
    ),
    path(
        '<int:pk>/copy',
        plan.copy,
        name='copy',
    ),
    path(
        '<int:id>/pdf',
        plan.export_pdf,
        name='export-pdf',
    ),
]

# sub patterns for ingredient
patterns_ingredient = [
    path(
        '<int:pk>/delete/',
        ingredient.IngredientDeleteView.as_view(),
        name='delete',
    ),
    path(
        '<int:pk>/edit/',
        ingredient.IngredientEditView.as_view(),
        name='edit',
    ),
    path(
        'add/',
        login_required(ingredient.IngredientCreateView.as_view()),
        name='add',
    ),
    path(
        'overview/',
        ingredient.IngredientListView.as_view(),
        name='list',
    ),
    path(
        '<int:pk>/view/',
        ingredient.view,
        name='view',
    ),
    path(
        '<int:pk>/view/<slug:slug>/',
        ingredient.view,
        name='view',
    ),
]

# sub patterns for weight units
patterns_weight_unit = [
    path(
        'list/',
        unit.WeightUnitListView.as_view(),
        name='list',
    ),
    path(
        'add/',
        unit.WeightUnitCreateView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>/delete/',
        unit.WeightUnitDeleteView.as_view(),
        name='delete',
    ),
    path(
        '<int:pk>/edit/',
        unit.WeightUnitUpdateView.as_view(),
        name='edit',
    ),
]

# sub patterns for weight units / ingredient cross table
patterns_unit_ingredient = [
    path(
        'add/<int:ingredient_pk>/',
        unit_ingredient.WeightUnitIngredientCreateView.as_view(),
        name='add',
    ),
    path(
        '<int:pk>/edit/',
        unit_ingredient.WeightUnitIngredientUpdateView.as_view(),
        name='edit',
    ),
    path(
        '<int:pk>/delete/',
        unit_ingredient.WeightUnitIngredientDeleteView.as_view(),
        name='delete',
    ),
]

# sub patterns for BMI calculator
patterns_bmi = [
    path(
        '',
        ReactView.as_view(),
        name='view',
    ),
]

# sub patterns for calories calculator
patterns_calories = [
    path(
        '',
        calculator.view,
        name='view',
    ),
    path(
        'bmr',
        calculator.calculate_bmr,
        name='bmr',
    ),
    path(
        'activities',
        calculator.calculate_activities,
        name='activities',
    ),  # JS
]

urlpatterns = [
    path(
        '',
        include(
            (patterns_plan, 'plan'),
            namespace='plan',
        ),
    ),
    path(
        'ingredient/',
        include(
            (patterns_ingredient, 'ingredient'),
            namespace='ingredient',
        ),
    ),
    path(
        'unit/',
        include(
            (patterns_weight_unit, 'weight_unit'),
            namespace='weight_unit',
        ),
    ),
    path(
        'unit-to-ingredient/',
        include(
            (patterns_unit_ingredient, 'unit_ingredient'),
            namespace='unit_ingredient',
        ),
    ),
    path(
        'calculator/bmi/',
        include(
            (patterns_bmi, 'bmi'),
            namespace='bmi',
        ),
    ),
    path(
        'calculator/calories/',
        include(
            (patterns_calories, 'calories'),
            namespace='calories',
        ),
    ),
]
