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

from django.core.validators import MaxValueValidator
from django.contrib.auth.models import User
from django.utils.translation import ugettext as _

from exercises.models import Language


class NutritionPlan(models.Model):
    """ A nutrition plan
    """
    
    # Metaclass to set some other properties
    class Meta:
        
        # Order by creation_date, descending (oldest first)
        ordering = ["-creation_date", ]
    
    user = models.ForeignKey(User, verbose_name = _('User'))
    language = models.ForeignKey(Language, verbose_name = _('Language'))
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    description = models.TextField(max_length = 2000,
                                   blank = True,
                                   verbose_name = _('Description'),
                                   help_text = _('A description of the goal of the plan, e.g. "Gain mass" or "Prepare for summer"'))

    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "Nutrition plan for %s, %s" % (self.user, self.creation_date)


    def get_nutritional_values(self):
        # Sum the nutrional info
        nutritional_info = {'energy': 0,
                            'protein': 0,
                            'carbohydrates': 0,
                            'fat': 0,
                            'fibres': 0,
                            'natrium': 0}
        for meal in self.meal_set.select_related():
            for item in meal.mealitem_set.select_related():
                
                # Don't proceed if the ingredient was input by hand or has freetext units
                if item.ingredient and item.amount_gramm:
                    nutritional_info['energy'] += item.ingredient.energy * item.amount_gramm / 100
                    nutritional_info['protein'] += item.ingredient.protein  * item.amount_gramm / 100
                    nutritional_info['carbohydrates'] += item.ingredient.carbohydrates  * item.amount_gramm / 100
                    nutritional_info['fat'] += item.ingredient.fat  * item.amount_gramm / 100
                    
                    if item.ingredient.fibres:
                        nutritional_info['fibres'] += item.ingredient.fibres  * item.amount_gramm / 100
                    
                    if item.ingredient.natrium:
                        nutritional_info['natrium'] += item.ingredient.natrium  * item.amount_gramm / 100
        return nutritional_info
    
class Ingredient(models.Model):
    """ An ingredient, with some approximate nutrition values
    """
    
    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]
    
    
    name = models.CharField(max_length=100,
                            verbose_name = _('Name'),)
    
    language = models.ForeignKey(Language, verbose_name = _('Language'))
    
    energy = models.IntegerField(
                                 verbose_name = _('Energy'),
                                 help_text = _('In kcal per 100g'))
    
    protein = models.FloatField(
                                verbose_name = _('Protein'),
                                help_text = _('In g per 100g of product'))
    
    carbohydrates = models.FloatField(
                                        verbose_name = _('Carbohydrates'),
                                        help_text = _('In g per 100g of product'))
    
    fat = models.FloatField(blank = True,
                              verbose_name = _('Fat'),
                              help_text = _('In g per 100g of product'))
    
    fibres = models.FloatField(blank = True,
                               null = True,
                               verbose_name = _('Fibres'),
                               help_text = _('In g per 100g of product'))
    
    natrium = models.FloatField(blank = True,
                                null = True,
                                verbose_name = _('Natrium'),
                                help_text = _('In g per 100g of product'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "%s" % (self.name, )


class Meal(models.Model):
    """ A meal
    """
    
    plan = models.ForeignKey(NutritionPlan, verbose_name = _('Nutrition plan'))
    order = models.IntegerField(max_length = 1, blank = True, verbose_name = _('Order'))
    time = models.TimeField(null = True, blank = True, verbose_name = _('Time (approx)'))
        
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "%s Meal" % (self.order,)


class MealItem(models.Model):
    """ An item (component) of a meal
    """
    
    meal = models.ForeignKey(Meal, verbose_name = _('Nutrition plan'))
    order = models.IntegerField(max_length = 1, blank = True, verbose_name = _('Order'))
    amount_gramm = models.IntegerField(max_length=4,
                                       blank = True,
                                       validators = [MaxValueValidator(1000)],
                                       verbose_name = _('Amount in gramms'))
    #amount_freetext = models.CharField(max_length=30,
    #                                   blank = True,
    #                                   verbose_name = _('Amount (freetext)'),
    #                                   help_text = _('The amount in another unit, e.g. "a spoonfull" or "3 pieces"'))
    #ingredient_freetext = models.CharField(max_length=150,
    #                                       blank = True,
    #                                       verbose_name = _('Ingredient'),
    #                                       help_text = _('If the ingredient is not in the system, enter the name here'))
    ingredient = models.ForeignKey(Ingredient, verbose_name = _('Ingredient'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "%s %s %s" % (self.order, self.amount_gramm or self.amount_freetext, self.ingredient)
