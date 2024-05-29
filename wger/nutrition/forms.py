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

# Standard Library
import logging
from datetime import datetime
from decimal import Decimal

# Django
from django import forms
from django.forms import BooleanField
from django.urls import reverse
from django.utils.translation import (
    gettext as _,
    gettext_lazy,
)

# Third Party
from crispy_forms.helper import FormHelper
from crispy_forms.layout import (
    HTML,
    ButtonHolder,
    Column,
    Layout,
    Row,
    Submit,
)

# wger
from wger.core.models import UserProfile
from wger.nutrition.models import (
    Ingredient,
    IngredientWeightUnit,
    LogItem,
    Meal,
    MealItem,
)
from wger.utils.widgets import Html5NumberInput


logger = logging.getLogger(__name__)


class UnitChooserForm(forms.Form):
    """
    A small form to select an amount and a unit for an ingredient
    """

    amount = forms.DecimalField(
        decimal_places=2, label=gettext_lazy('Amount'), max_digits=5, localize=True
    )
    unit = forms.ModelChoiceField(
        queryset=IngredientWeightUnit.objects.none(),
        label=gettext_lazy('Unit'),
        empty_label='g',
        required=False,
    )

    def __init__(self, *args, **kwargs):
        super(UnitChooserForm, self).__init__(*args, **kwargs)

        if len(args) and args[0].get('ingredient'):
            ingredient_id = args[0]['ingredient']

        elif kwargs.get('data'):
            ingredient_id = kwargs['data']['ingredient_id']

        else:
            ingredient_id = -1

        self.fields['unit'].queryset = IngredientWeightUnit.objects.filter(
            ingredient_id=ingredient_id
        ).select_related()

        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('amount', css_class='col-6'),
                Column('unit', css_class='col-6'),
                css_class='form-row',
            )
        )
        self.helper.form_tag = False


class BmiForm(forms.ModelForm):
    height = forms.DecimalField(
        widget=Html5NumberInput(),
        max_value=Decimal(999),
    )
    weight = forms.DecimalField(
        widget=Html5NumberInput(),
        max_value=Decimal(999),
    )

    class Meta:
        model = UserProfile
        fields = ('height',)

    def __init__(self, *args, **kwargs):
        super(BmiForm, self).__init__(*args, **kwargs)

        if 'initial' in kwargs:  # if the form is rendering for the first time
            self['height'].label = (
                _('Height (cm)') if kwargs['initial']['use_metric'] else _('Height (in)')
            )
            self['weight'].label = (
                _('Weight (kg)') if kwargs['initial']['use_metric'] else _('Weight (lbs)')
            )

        self.helper = FormHelper()
        self.helper.form_action = reverse('nutrition:bmi:calculate')
        self.helper.form_class = 'wger-form'
        self.helper.form_id = 'bmi-form'
        self.helper.layout = Layout(
            Row(
                Column('height', css_class='col-6'),
                Column('weight', css_class='col-6'),
                css_class='form-row',
            ),
            ButtonHolder(Submit('submit', _('Calculate'), css_class='btn-success')),
        )


class BmrForm(forms.ModelForm):
    """
    Form for the basal metabolic rate
    """

    weight = forms.DecimalField(widget=Html5NumberInput())

    class Meta:
        model = UserProfile
        fields = ('age', 'height', 'gender')

    def __init__(self, *args, **kwargs):
        super(BmrForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'age',
            'height',
            'gender',
            'weight',
        )
        self.helper.form_tag = False


class PhysicalActivitiesForm(forms.ModelForm):
    """
    Form for the additional physical activities
    """

    class Meta:
        model = UserProfile
        fields = (
            'sleep_hours',
            'work_hours',
            'work_intensity',
            'sport_hours',
            'sport_intensity',
            'freetime_hours',
            'freetime_intensity',
        )

    def __init__(self, *args, **kwargs):
        super(PhysicalActivitiesForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'sleep_hours',
            Row(
                Column('work_hours', css_class='col-6'),
                Column('work_intensity', css_class='col-6'),
                css_class='form-row',
            ),
            Row(
                Column('sport_hours', css_class='col-6'),
                Column('sport_intensity', css_class='col-6'),
                css_class='form-row',
            ),
            Row(
                Column('freetime_hours', css_class='col-6'),
                Column('freetime_intensity', css_class='col-6'),
                css_class='form-row',
            ),
        )
        self.helper.form_tag = False


class DailyCaloriesForm(forms.ModelForm):
    """
    Form for the total daily calories needed
    """

    base_calories = forms.IntegerField(
        label=_('Basic caloric intake'),
        help_text=_('Your basic caloric intake as calculated for ' 'your data'),
        required=False,
        widget=Html5NumberInput(),
    )
    additional_calories = forms.IntegerField(
        label=_('Additional calories'),
        help_text=_(
            'Additional calories to add to the base '
            'rate (to substract, enter a negative '
            'number)'
        ),
        initial=0,
        required=False,
        widget=Html5NumberInput(),
    )

    class Meta:
        model = UserProfile
        fields = ('calories',)

    def __init__(self, *args, **kwargs):
        super(DailyCaloriesForm, self).__init__(*args, **kwargs)

        self.helper = FormHelper()
        self.helper.form_tag = False


class MealItemForm(forms.ModelForm):
    weight_unit = forms.ModelChoiceField(
        queryset=IngredientWeightUnit.objects.none(),
        empty_label='g',
        required=False,
    )
    ingredient = forms.ModelChoiceField(
        queryset=Ingredient.objects.all(),
        widget=forms.HiddenInput,
    )

    ingredient_searchfield = forms.CharField(
        required=False,
        label=gettext_lazy('Ingredient'),
    )

    english_results = BooleanField(
        label=gettext_lazy('Also search for names in English'),
        initial=True,
        required=False,
    )

    class Meta:
        model = MealItem
        fields = [
            'ingredient',
            'english_results',
            'weight_unit',
            'amount',
        ]

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
            self.fields['weight_unit'].queryset = IngredientWeightUnit.objects.filter(
                ingredient_id=ingredient_id
            )

        self.helper = FormHelper()
        self.helper.layout = Layout(
            'ingredient',
            'ingredient_searchfield',
            'english_results',
            HTML('<div id="ingredient_name"></div>'),
            Row(
                Column('amount', css_class='col-6'),
                Column('weight_unit', css_class='col-6'),
                css_class='form-row',
            ),
        )


class MealLogItemForm(MealItemForm):
    datetime_format = '%Y-%m-%dT%H:%M'
    now = datetime.now().strftime(datetime_format)

    datetime = forms.DateTimeField(
        input_formats=[datetime_format],
        widget=forms.DateTimeInput(
            attrs={'type': 'datetime-local', 'class': 'form-control', 'value': now},
            format=datetime_format,
        ),
    )

    class Meta:
        model = LogItem
        fields = [
            'ingredient',
            'weight_unit',
            'amount',
            'datetime',
        ]

    def __init__(self, *args, **kwargs):
        super(MealLogItemForm, self).__init__(*args, **kwargs)

        self.helper.layout = Layout(
            'ingredient',
            'ingredient_searchfield',
            'english_results',
            Row(
                Column('amount', css_class='col-6'),
                Column('weight_unit', css_class='col-6'),
            ),
            Row(Column('datetime', css_class='col-6'), css_class='form-row'),
        )


class IngredientForm(forms.ModelForm):
    class Meta:
        model = Ingredient
        fields = [
            'name',
            'brand',
            'energy',
            'protein',
            'carbohydrates',
            'carbohydrates_sugar',
            'fat',
            'fat_saturated',
            'fiber',
            'sodium',
            'license',
            'license_author',
        ]
        widgets = {'category': forms.TextInput}

    def __init__(self, *args, **kwargs):
        super(IngredientForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            Row(
                Column('name', css_class='col-6'),
                Column('brand', css_class='col-6'),
                css_class='form-row',
            ),
            'energy',
            'protein',
            Row(
                Column('carbohydrates', css_class='col-6'),
                Column('carbohydrates_sugar', css_class='col-6'),
                css_class='form-row',
            ),
            Row(
                Column('fat', css_class='col-6'),
                Column('fat_saturated', css_class='col-6'),
                css_class='form-row',
            ),
            'fiber',
            'sodium',
            Row(
                Column('license', css_class='col-6'),
                Column('license_author', css_class='col-6'),
                css_class='form-row',
            ),
        )
