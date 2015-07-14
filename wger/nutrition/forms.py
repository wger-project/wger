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

import logging

from django import forms
from django.utils.translation import ugettext as _
from wger.core.models import UserProfile

from wger.nutrition.models import IngredientWeightUnit, Ingredient, MealItem
from wger.utils.widgets import Html5NumberInput


logger = logging.getLogger(__name__)


class UnitChooserForm(forms.Form):
    '''
    A small form to select an amount and a unit for an ingredient
    '''
    amount = forms.DecimalField(decimal_places=2,
                                max_digits=5,
                                localize=True)
    unit = forms.ModelChoiceField(queryset=IngredientWeightUnit.objects.none(),
                                  empty_label="g",
                                  required=False)

    def __init__(self, *args, **kwargs):
        super(UnitChooserForm, self).__init__(*args, **kwargs)

        if len(args) and args[0].get('ingredient'):
            ingredient_id = args[0]['ingredient']

        elif kwargs.get('data'):
            ingredient_id = kwargs['data']['ingredient_id']

        else:
            ingredient_id = -1

        self.fields['unit'].queryset = IngredientWeightUnit.objects.filter(
            ingredient_id=ingredient_id).select_related()


class BmiForm(forms.ModelForm):
    height = forms.DecimalField(widget=Html5NumberInput(),
                                max_value=999,
                                label=_('Height (cm)'))
    weight = forms.DecimalField(widget=Html5NumberInput(),
                                max_value=999)

    class Meta:
        model = UserProfile
        fields = ('height', )


class BmrForm(forms.ModelForm):
    '''
    Form for the basal metabolic rate
    '''
    weight = forms.DecimalField(widget=Html5NumberInput())

    class Meta:
        model = UserProfile
        fields = ('age', 'height', 'gender')


class PhysicalActivitiesForm(forms.ModelForm):
    '''
    Form for the additional physical activities
    '''
    class Meta:
        model = UserProfile
        fields = ('sleep_hours',
                  'work_hours',
                  'work_intensity',
                  'sport_hours',
                  'sport_intensity',
                  'freetime_hours',
                  'freetime_intensity')


class DailyCaloriesForm(forms.ModelForm):
    '''
    Form for the total daily calories needed
    '''

    base_calories = forms.IntegerField(label=_('Basic caloric intake'),
                                       help_text=_('Your basic caloric intake as calculated for '
                                                   'your data'),
                                       required=False,
                                       widget=Html5NumberInput())
    additional_calories = forms.IntegerField(label=_('Additional calories'),
                                             help_text=_('Additional calories to add to the base '
                                                         'rate (to substract, enter a negative '
                                                         'number)'),
                                             initial=0,
                                             required=False,
                                             widget=Html5NumberInput())

    class Meta:
        model = UserProfile
        fields = ('calories',)


class MealItemForm(forms.ModelForm):
    weight_unit = forms.ModelChoiceField(queryset=IngredientWeightUnit.objects.none(),
                                         empty_label="g",
                                         required=False)
    ingredient = forms.ModelChoiceField(queryset=Ingredient.objects.all(),
                                        widget=forms.HiddenInput)

    class Meta:
        model = MealItem
        fields = '__all__'

    def __init__(self, *args, **kwargs):
        super(MealItemForm, self).__init__(*args, **kwargs)

        # Get the ingredient_id
        ingredient_id = None

        if kwargs.get('instance'):
            ingredient_id = kwargs['instance'].ingredient_id

        if kwargs.get('data'):
            ingredient_id = kwargs['data']['ingredient']

        # Filter the available ingredients
        if ingredient_id:
            self.fields['weight_unit'].queryset = \
                IngredientWeightUnit.objects.filter(ingredient_id=ingredient_id)
