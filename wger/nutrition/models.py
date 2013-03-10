# -*- coding: utf-8 -*-

# This file is part of Workout Manager.
#
# Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.


from django.db import models

from django.template.defaultfilters import slugify  # django.utils.text.slugify in django 1.5!
from django.core.validators import MaxValueValidator
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.utils.translation import ugettext_lazy as _

from wger.exercises.models import Language


class NutritionPlan(models.Model):
    '''
    A nutrition plan
    '''

    # Metaclass to set some other properties
    class Meta:

        # Order by creation_date, descending (oldest first)
        ordering = ["-creation_date", ]

    user = models.ForeignKey(User, verbose_name=_('User'))
    language = models.ForeignKey(Language, verbose_name=_('Language'))
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    description = models.TextField(max_length=2000,
                                   blank=True,
                                   verbose_name=_('Description'),
                                   help_text=_('A description of the goal of the plan, e.g. '
                                   '"Gain mass" or "Prepare for summer"'))

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "Nutrition plan for %s, %s" % (self.user, self.creation_date)

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view this object
        '''
        return reverse('wger.nutrition.views.plan.view', kwargs={'id': self.id})

    def get_nutritional_values(self):
        # Sum the nutrional info
        nutritional_info = {'energy': 0,
                            'protein': 0,
                            'carbohydrates': 0,
                            'carbohydrates_sugar': 0,
                            'fat': 0,
                            'fat_saturated': 0,
                            'fibres': 0,
                            'sodium': 0}
        for meal in self.meal_set.select_related():
            for item in meal.mealitem_set.select_related():

                # Calculate the base weight of the item
                if item.weight_type == MEALITEM_WEIGHT_GRAM:
                    item_weight = item.amount_gramm
                else:
                    item_weight = (item.amount_gramm *
                                   float(item.weight_unit.amount) *
                                   item.weight_unit.gramm)

                nutritional_info['energy'] += item.ingredient.energy * item_weight / 100
                nutritional_info['protein'] += item.ingredient.protein * item_weight / 100
                nutritional_info['carbohydrates'] += item.ingredient.carbohydrates * \
                    item_weight / 100

                if item.ingredient.carbohydrates_sugar:
                    nutritional_info['carbohydrates_sugar'] += \
                        item.ingredient.carbohydrates_sugar * \
                        item_weight / 100

                nutritional_info['fat'] += item.ingredient.fat * item_weight / 100
                if item.ingredient.fat_saturated:
                    nutritional_info['fat_saturated'] += item.ingredient.fat_saturated * \
                        item_weight / 100

                if item.ingredient.fibres:
                    nutritional_info['fibres'] += item.ingredient.fibres * \
                        item_weight / 100

                if item.ingredient.sodium:
                    nutritional_info['sodium'] += item.ingredient.sodium * \
                        item_weight / 100
        return nutritional_info

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self


class Ingredient(models.Model):
    '''
    An ingredient, with some approximate nutrition values
    '''

    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]

    language = models.ForeignKey(Language, verbose_name=_('Language'))

    name = models.CharField(max_length=200,
                            verbose_name=_('Name'),)

    energy = models.IntegerField(verbose_name=_('Energy'),
                                 help_text=_('In kcal per 100g'))

    protein = models.FloatField(verbose_name=_('Protein'),
                                help_text=_('In g per 100g of product'))

    carbohydrates = models.FloatField(verbose_name=_('Carbohydrates'),
                                      help_text=_('In g per 100g of product'))

    carbohydrates_sugar = models.FloatField(blank=True,
                                            null=True,
                                            verbose_name=_('Sugar content in carbohydrates'),
                                            help_text=_('In g per 100g of product'))

    fat = models.FloatField(blank=True,
                            verbose_name=_('Fat'),
                            help_text=_('In g per 100g of product'))

    fat_saturated = models.FloatField(blank=True,
                                      null=True,
                                      verbose_name=_('Saturated fat content in fats'),
                                      help_text=_('In g per 100g of product'))

    fibres = models.FloatField(blank=True,
                               null=True,
                               verbose_name=_('Fibres'),
                               help_text=_('In g per 100g of product'))

    sodium = models.FloatField(blank=True,
                               null=True,
                               verbose_name=_('Sodium'),
                               help_text=_('In g per 100g of product'))

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view this object
        '''
        return reverse('wger.nutrition.views.ingredient.ingredient_view',
                       kwargs={'id': self.id, 'slug': slugify(self.name)})

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "%s" % (self.name, )

    def get_owner_object(self):
        '''
        Ingredient has no owner information
        '''
        return False


class WeightUnit(models.Model):
    '''
    A more human usable weight unit (spoon, table, slice...)
    '''

    language = models.ForeignKey(Language, verbose_name=_('Language'))
    name = models.CharField(max_length=200,
                            verbose_name=_('Name'),)

    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "{0}".format(self.name)

    def get_owner_object(self):
        '''
        Weight unit has no owner information
        '''
        return None


class IngredientWeightUnit(models.Model):
    '''
    A specific human usable weight unit for an ingredient
    '''

    ingredient = models.ForeignKey(Ingredient, verbose_name=_('Ingredient'))
    unit = models.ForeignKey(WeightUnit, verbose_name=_('Weight unit'))

    gramm = models.IntegerField(verbose_name=_('Amount in gramms'))
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

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''

        return u"{0}: {1}{2} á {3}g".format(self.ingredient.name,
                                             self.amount,
                                             self.unit.name,
                                             self.gramm)


class Meal(models.Model):
    '''
    A meal
    '''

    # Metaclass to set some other properties
    class Meta:
        ordering = ["time", ]

    plan = models.ForeignKey(NutritionPlan, verbose_name=_('Nutrition plan'))
    order = models.IntegerField(max_length=1, blank=True, verbose_name=_('Order'))
    time = models.TimeField(null=True, blank=True, verbose_name=_('Time (approx)'))

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "%s Meal" % (self.order,)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self.plan


MEALITEM_WEIGHT_GRAM = '1'
MEALITEM_WEIGHT_UNIT = '2'

MEALITEM_WEIGHT_TYPES = (
    (MEALITEM_WEIGHT_GRAM, _('Weight in grams')),
    (MEALITEM_WEIGHT_UNIT, _('Weight in units')),
)


class MealItem(models.Model):
    '''
    An item (component) of a meal
    '''

    meal = models.ForeignKey(Meal, verbose_name=_('Nutrition plan'))
    ingredient = models.ForeignKey(Ingredient, verbose_name=_('Ingredient'))
    weight_unit = models.ForeignKey(IngredientWeightUnit,
                                    verbose_name=_('Weight unit'),
                                    null=True)

    order = models.IntegerField(max_length=1, blank=True, verbose_name=_('Order'))
    amount_gramm = models.IntegerField(max_length=4,
                                       blank=True,
                                       validators=[MaxValueValidator(1000)],
                                       verbose_name=_('Amount in gramms'))
    weight_type = models.CharField(max_length=2,
                                   choices=MEALITEM_WEIGHT_TYPES,
                                   default=MEALITEM_WEIGHT_GRAM)

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "%sg ingredient %s" % (self.amount_gramm, self.ingredient_id)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self.meal.plan
