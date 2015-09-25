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
import logging
from decimal import Decimal

from django.db import models

from django.template.loader import render_to_string
from django.template.defaultfilters import slugify  # django.utils.text.slugify in django 1.5!
from django.core.validators import MaxValueValidator, MinValueValidator
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse
from django.core import mail
from django.core.cache import cache
from django.contrib.auth.models import User
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from django.utils import translation

from wger.core.models import Language
from wger.utils.constants import EMAIL_FROM, TWOPLACES
from wger.utils.cache import cache_mapper
from wger.utils.fields import Html5TimeField
from wger.utils.models import AbstractLicenseModel
from wger.utils.units import AbstractWeight

MEALITEM_WEIGHT_GRAM = '1'
MEALITEM_WEIGHT_UNIT = '2'

ENERGY_FACTOR = {'protein': {'kg': 4,
                             'lb': 113},
                 'carbohydrates': {'kg': 4,
                                   'lb': 113},
                 'fat': {'kg': 9,
                         'lb': 225}}
'''
Simple approximation of energy (kcal) provided per gram or ounce
'''


logger = logging.getLogger(__name__)


@python_2_unicode_compatible
class NutritionPlan(models.Model):
    '''
    A nutrition plan
    '''

    # Metaclass to set some other properties
    class Meta:

        # Order by creation_date, descending (oldest first)
        ordering = ["-creation_date", ]

    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False)
    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'),
                                 editable=False)
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    description = models.TextField(max_length=2000,
                                   blank=True,
                                   verbose_name=_('Description'),
                                   help_text=_('A description of the goal of the plan, e.g. '
                                               '"Gain mass" or "Prepare for summer"'))
    has_goal_calories = models.BooleanField(verbose_name=_('Use daily calories'),
                                            default=False,
                                            help_text=_("Tick the box if you want to mark this "
                                                        "plan as having a goal amount of calories. "
                                                        "You can use the calculator or enter the "
                                                        "value yourself."))
    '''A flag indicating whether the plan has a goal amount of calories'''

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        if self.description:
            return u"{0}".format(self.description)
        else:
            return u"{0}".format(_("Nutrition plan"))

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view this object
        '''
        return reverse('nutrition:plan:view', kwargs={'id': self.id})

    def get_nutritional_values(self):
        '''
        Sums the nutritional info of all items in the plan
        '''
        use_metric = self.user.userprofile.use_metric
        unit = 'kg' if use_metric else 'lb'
        result = {'total': {'energy': 0,
                            'protein': 0,
                            'carbohydrates': 0,
                            'carbohydrates_sugar': 0,
                            'fat': 0,
                            'fat_saturated': 0,
                            'fibres': 0,
                            'sodium': 0},
                  'percent': {'protein': 0,
                              'carbohydrates': 0,
                              'fat': 0},
                  'per_kg': {'protein': 0,
                             'carbohydrates': 0,
                             'fat': 0}
                  }

        # Energy
        for meal in self.meal_set.select_related():
            values = meal.get_nutritional_values(use_metric=use_metric)
            for key in result['total'].keys():
                result['total'][key] += values[key]

        energy = result['total']['energy']

        # In percent
        if energy:
            for key in result['percent'].keys():
                result['percent'][key] = \
                    result['total'][key] * ENERGY_FACTOR[key][unit] / energy * 100

        # Per body weight
        if self.user.userprofile.weight:
            weight = Decimal(self.user.userprofile.weight)
            for key in result['per_kg'].keys():
                result['per_kg'][key] = result['total'][key] / weight

        # Only 2 decimal places, anything else doesn't make sense
        for key in result.keys():
            for i in result[key]:
                result[key][i] = Decimal(result[key][i]).quantize(TWOPLACES)

        return result

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self

    def get_calories_approximation(self):
        '''
        Calculates the deviation from the goal calories and the actual
        amount of the current plan
        '''

        goal_calories = self.user.userprofile.calories
        actual_calories = self.get_nutritional_values()['total']['energy']

        # Within 3%
        if (actual_calories < goal_calories * 1.03) and (actual_calories > goal_calories * 0.97):
            return 1
        # within 7%
        elif (actual_calories < goal_calories * 1.07) and (actual_calories > goal_calories * 0.93):
            return 2
        # within 10%
        elif (actual_calories < goal_calories * 1.10) and (actual_calories > goal_calories * 0.9):
            return 3
        # even more
        else:
            return 4


@python_2_unicode_compatible
class Ingredient(AbstractLicenseModel, models.Model):
    '''
    An ingredient, with some approximate nutrition values
    '''

    ENERGY_APPROXIMATION = 15
    '''
    How much the calculated energy from protein, etc. can deviate from the
    energy amount given (in percent).
    '''

    INGREDIENT_STATUS_PENDING = '1'
    INGREDIENT_STATUS_ACCEPTED = '2'
    INGREDIENT_STATUS_DECLINED = '3'
    INGREDIENT_STATUS_ADMIN = '4'
    INGREDIENT_STATUS_SYSTEM = '5'

    INGREDIENT_STATUS_OK = (INGREDIENT_STATUS_ACCEPTED,
                            INGREDIENT_STATUS_ADMIN,
                            INGREDIENT_STATUS_SYSTEM)

    INGREDIENT_STATUS = (
        (INGREDIENT_STATUS_PENDING, _('Pending')),
        (INGREDIENT_STATUS_ACCEPTED, _('Accepted')),
        (INGREDIENT_STATUS_DECLINED, _('Declined')),
        (INGREDIENT_STATUS_ADMIN, _('Submitted by administrator')),
        (INGREDIENT_STATUS_SYSTEM, _('System ingredient')),
    )

    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]

    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'),
                                 editable=False)

    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             null=True,
                             blank=True,
                             editable=False)
    '''The user that submitted the exercise'''

    status = models.CharField(max_length=2,
                              choices=INGREDIENT_STATUS,
                              default=INGREDIENT_STATUS_PENDING,
                              editable=False)
    '''The status of an ingredient'''

    creation_date = models.DateField(_('Date'), auto_now_add=True)
    update_date = models.DateField(_('Date'),
                                   auto_now=True,
                                   blank=True,
                                   editable=False)

    name = models.CharField(max_length=200,
                            verbose_name=_('Name'),)

    energy = models.IntegerField(verbose_name=_('Energy'),
                                 help_text=_('In kcal per 100g'))

    protein = models.DecimalField(decimal_places=3,
                                  max_digits=6,
                                  verbose_name=_('Protein'),
                                  help_text=_('In g per 100g of product'),
                                  validators=[MinValueValidator(0),
                                              MaxValueValidator(100)])

    carbohydrates = models.DecimalField(decimal_places=3,
                                        max_digits=6,
                                        verbose_name=_('Carbohydrates'),
                                        help_text=_('In g per 100g of product'),
                                        validators=[MinValueValidator(0),
                                                    MaxValueValidator(100)])

    carbohydrates_sugar = models.DecimalField(decimal_places=3,
                                              max_digits=6,
                                              blank=True,
                                              null=True,
                                              verbose_name=_('Sugar content in carbohydrates'),
                                              help_text=_('In g per 100g of product'),
                                              validators=[MinValueValidator(0),
                                                          MaxValueValidator(100)])

    fat = models.DecimalField(decimal_places=3,
                              max_digits=6,
                              verbose_name=_('Fat'),
                              help_text=_('In g per 100g of product'),
                              validators=[MinValueValidator(0),
                                          MaxValueValidator(100)])

    fat_saturated = models.DecimalField(decimal_places=3,
                                        max_digits=6,
                                        blank=True,
                                        null=True,
                                        verbose_name=_('Saturated fat content in fats'),
                                        help_text=_('In g per 100g of product'),
                                        validators=[MinValueValidator(0),
                                                    MaxValueValidator(100)])

    fibres = models.DecimalField(decimal_places=3,
                                 max_digits=6,
                                 blank=True,
                                 null=True,
                                 verbose_name=_('Fibres'),
                                 help_text=_('In g per 100g of product'),
                                 validators=[MinValueValidator(0),
                                             MaxValueValidator(100)])

    sodium = models.DecimalField(decimal_places=3,
                                 max_digits=6,
                                 blank=True,
                                 null=True,
                                 verbose_name=_('Sodium'),
                                 help_text=_('In g per 100g of product'),
                                 validators=[MinValueValidator(0),
                                             MaxValueValidator(100)])

    #
    # Django methods
    #

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view this object
        '''
        return reverse('nutrition:ingredient:view',
                       kwargs={'id': self.id, 'slug': slugify(self.name)})

    def clean(self):
        '''
        Do a very broad sanity check on the nutritional values according to
        the following rules:
        - 1g of protein: 4kcal
        - 1g of carbohydrates: 4kcal
        - 1g of fat: 9kcal

        The sum is then compared to the given total energy, with ENERGY_APPROXIMATION
        percent tolerance.
        '''

        # Note: calculations in 100 grams, to save us the '/100' everywhere
        energy_protein = 0
        if self.protein:
            energy_protein = self.protein * ENERGY_FACTOR['protein']['kg']

        energy_carbohydrates = 0
        if self.carbohydrates:
            energy_carbohydrates = self.carbohydrates * ENERGY_FACTOR['carbohydrates']['kg']

        energy_fat = 0
        if self.fat:
            energy_fat = self.fat * ENERGY_FACTOR['fat']['kg']

        energy_calculated = energy_protein + energy_carbohydrates + energy_fat

        # Compare the values, but be generous
        if self.energy:
            energy_upper = self.energy * (1 + (self.ENERGY_APPROXIMATION / Decimal(100.0)))
            energy_lower = self.energy * (1 - (self.ENERGY_APPROXIMATION / Decimal(100.0)))

            if not ((energy_upper > energy_calculated) and (energy_calculated > energy_lower)):
                raise ValidationError(_('Total energy is not the approximate sum of the energy '
                                        'provided by protein, carbohydrates and fat.'))

    def save(self, *args, **kwargs):
        '''
        Reset the cache
        '''

        super(Ingredient, self).save(*args, **kwargs)
        cache.delete(cache_mapper.get_ingredient_key(self.id))

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name

    def __eq__(self, other):
        '''
        Compare ingredients based on their values, not like django on their PKs
        '''

        logger.debug('Overwritten behaviour: comparing ingredients on values, not PK.')
        equal = True
        if isinstance(other, self.__class__):
            for i in self._meta.fields:
                if (hasattr(self, i.name) and hasattr(other, i.name) and
                   (getattr(self, i.name, None) != getattr(other, i.name, None))):
                        equal = False
        else:
            equal = False
        return equal

    #
    # Own methods
    #
    def compare_with_database(self):
        '''
        Compares the current ingredient with the version saved in the database.

        If the current object has no PK, returns false
        '''
        if not self.pk:
            return False

        ingredient = Ingredient.objects.get(pk=self.pk)
        if self != ingredient:
            return False
        else:
            return True

    def send_email(self, request):
        '''
        Sends an email after being successfully added to the database (for user
        submitted ingredients only)
        '''
        if self.user and self.user.email:
            translation.activate(self.user.userprofile.notification_language.short_name)
            url = request.build_absolute_uri(self.get_absolute_url())
            subject = _('Ingredient was successfully added to the general database')
            context = {
                'ingredient': self.name,
                'url': url
            }
            message = render_to_string('ingredient/email_new.html', context)
            mail.send_mail(subject,
                           message,
                           EMAIL_FROM,
                           [self.user.email],
                           fail_silently=True)

    def get_owner_object(self):
        '''
        Ingredient has no owner information
        '''
        return False


@python_2_unicode_compatible
class WeightUnit(models.Model):
    '''
    A more human usable weight unit (spoon, table, slice...)
    '''

    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'),
                                 editable=False)
    name = models.CharField(max_length=200,
                            verbose_name=_('Name'),)

    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name

    def get_owner_object(self):
        '''
        Weight unit has no owner information
        '''
        return None


@python_2_unicode_compatible
class IngredientWeightUnit(models.Model):
    '''
    A specific human usable weight unit for an ingredient
    '''

    ingredient = models.ForeignKey(Ingredient,
                                   verbose_name=_('Ingredient'),
                                   editable=False)
    unit = models.ForeignKey(WeightUnit, verbose_name=_('Weight unit'))

    gram = models.IntegerField(verbose_name=_('Amount in grams'))
    amount = models.DecimalField(decimal_places=2,
                                 max_digits=5,
                                 default=1,
                                 verbose_name=_('Amount'),
                                 help_text=_('Unit amount, e.g. "1 Cup" or "1/2 spoon"'))

    def get_owner_object(self):
        '''
        Weight unit has no owner information
        '''
        return None

    def __str__(self):
        '''
        Return a more human-readable representation
        '''

        return u"{0}{1} ({2}g)".format(self.amount if self.amount > 1 else '',
                                       self.unit.name,
                                       self.gram)


@python_2_unicode_compatible
class Meal(models.Model):
    '''
    A meal
    '''

    # Metaclass to set some other properties
    class Meta:
        ordering = ["time", ]

    plan = models.ForeignKey(NutritionPlan,
                             verbose_name=_('Nutrition plan'),
                             editable=False)
    order = models.IntegerField(verbose_name=_('Order'),
                                blank=True,
                                editable=False)
    time = Html5TimeField(null=True,
                          blank=True,
                          verbose_name=_('Time (approx)'))

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0} Meal".format(self.order)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self.plan

    def get_nutritional_values(self, use_metric=True):
        '''
        Sums the nutrional info of all items in the meal

        :param use_metric Flag that controls the units used
        '''
        nutritional_info = {'energy': 0,
                            'protein': 0,
                            'carbohydrates': 0,
                            'carbohydrates_sugar': 0,
                            'fat': 0,
                            'fat_saturated': 0,
                            'fibres': 0,
                            'sodium': 0}

        # Get the calculated values from the meal item and add them
        for item in self.mealitem_set.select_related():

            values = item.get_nutritional_values(use_metric=use_metric)
            for key in nutritional_info.keys():
                nutritional_info[key] += values[key]

        # Only 2 decimal places, anything else doesn't make sense
        for i in nutritional_info:
            nutritional_info[i] = Decimal(nutritional_info[i]).quantize(TWOPLACES)

        return nutritional_info


@python_2_unicode_compatible
class MealItem(models.Model):
    '''
    An item (component) of a meal
    '''

    meal = models.ForeignKey(Meal,
                             verbose_name=_('Nutrition plan'),
                             editable=False)
    ingredient = models.ForeignKey(Ingredient, verbose_name=_('Ingredient'))
    weight_unit = models.ForeignKey(IngredientWeightUnit,
                                    verbose_name=_('Weight unit'),
                                    null=True,
                                    blank=True,
                                    )

    order = models.IntegerField(verbose_name=_('Order'),
                                blank=True,
                                editable=False)
    amount = models.DecimalField(decimal_places=2,
                                 max_digits=6,
                                 verbose_name=_('Amount'),
                                 validators=[MinValueValidator(1),
                                             MaxValueValidator(1000)])

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0}g ingredient {1}".format(self.amount, self.ingredient_id)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self.meal.plan

    def get_unit_type(self):
        '''
        Returns the type of unit used:
        - a value in grams
        - a 'human' unit like 'a cup' or 'a slice'
        '''

        if self.weight_unit:
            return MEALITEM_WEIGHT_UNIT
        else:
            return MEALITEM_WEIGHT_GRAM

    def get_nutritional_values(self, use_metric=True):
        '''
        Sums the nutrional info for the ingredient in the MealItem

        :param use_metric Flag that controls the units used
        '''
        nutritional_info = {'energy': 0,
                            'protein': 0,
                            'carbohydrates': 0,
                            'carbohydrates_sugar': 0,
                            'fat': 0,
                            'fat_saturated': 0,
                            'fibres': 0,
                            'sodium': 0}
        # Calculate the base weight of the item
        if self.get_unit_type() == MEALITEM_WEIGHT_GRAM:
            item_weight = self.amount
        else:
            item_weight = (self.amount *
                           self.weight_unit.amount *
                           self.weight_unit.gram)

        nutritional_info['energy'] += self.ingredient.energy * item_weight / 100
        nutritional_info['protein'] += self.ingredient.protein * item_weight / 100
        nutritional_info['carbohydrates'] += self.ingredient.carbohydrates * item_weight / 100

        if self.ingredient.carbohydrates_sugar:
            nutritional_info['carbohydrates_sugar'] += self.ingredient.carbohydrates_sugar \
                * item_weight / 100

        nutritional_info['fat'] += self.ingredient.fat * item_weight / 100

        if self.ingredient.fat_saturated:
            nutritional_info['fat_saturated'] += self.ingredient.fat_saturated * item_weight / 100

        if self.ingredient.fibres:
            nutritional_info['fibres'] += self.ingredient.fibres * item_weight / 100

        if self.ingredient.sodium:
            nutritional_info['sodium'] += self.ingredient.sodium * item_weight / 100

        # If necessary, convert weight units
        if not use_metric:
            for key, value in nutritional_info.iteritems():

                # Energy is not a weight!
                if key == 'energy':
                    continue

                # Everything else, to ounces
                nutritional_info[key] = AbstractWeight(value, 'g').oz

        # Only 2 decimal places, anything else doesn't make sense
        for i in nutritional_info:
            nutritional_info[i] = Decimal(nutritional_info[i]).quantize(TWOPLACES)

        return nutritional_info
