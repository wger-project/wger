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

# Standard Library
import datetime
import logging
from decimal import Decimal

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.sites.models import Site
from django.core import mail
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator
)
from django.db import models
from django.template.loader import render_to_string
from django.urls import reverse
from django.utils import (
    timezone,
    translation
)
from django.utils.text import slugify
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import Language
from wger.utils.cache import cache_mapper
from wger.utils.constants import TWOPLACES
from wger.utils.fields import Html5TimeField
from wger.utils.managers import SubmissionManager
from wger.utils.models import (
    AbstractLicenseModel,
    AbstractSubmissionModel
)
from wger.utils.units import AbstractWeight
from wger.weight.models import WeightEntry


MEALITEM_WEIGHT_GRAM = '1'
MEALITEM_WEIGHT_UNIT = '2'

ENERGY_FACTOR = {'protein': {'kg': 4,
                             'lb': 113},
                 'carbohydrates': {'kg': 4,
                                   'lb': 113},
                 'fat': {'kg': 9,
                         'lb': 225}}
"""
Simple approximation of energy (kcal) provided per gram or ounce
"""

logger = logging.getLogger(__name__)


class NutritionPlan(models.Model):
    """
    A nutrition plan
    """

    # Metaclass to set some other properties
    class Meta:

        # Order by creation_date, descending (oldest first)
        ordering = ["-creation_date", ]

    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False,
                             on_delete=models.CASCADE)
    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'),
                                 editable=False,
                                 on_delete=models.CASCADE)
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    description = models.CharField(max_length=80,
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
    """A flag indicating whether the plan has a goal amount of calories"""

    def __str__(self):
        """
        Return a more human-readable representation
        """
        if self.description:
            return "{0}".format(self.description)
        else:
            return "{0}".format(_("Nutrition plan"))

    def get_absolute_url(self):
        """
        Returns the canonical URL to view this object
        """
        return reverse('nutrition:plan:view', kwargs={'id': self.id})

    def get_nutritional_values(self):
        """
        Sums the nutritional info of all items in the plan
        """
        nutritional_representation = cache.get(cache_mapper.get_nutrition_cache_by_key(self.pk))
        if not nutritional_representation:
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
                                 'fat': 0},
                      }

            # Energy
            for meal in self.meal_set.select_related():
                values = meal.get_nutritional_values(use_metric=use_metric)
                for key in result['total'].keys():
                    result['total'][key] += values[key]

            energy = result['total']['energy']
            result['total']['energy_kilojoule'] = result['total']['energy'] * Decimal(4.184)

            # In percent
            if energy:
                for key in result['percent'].keys():
                    result['percent'][key] = \
                        result['total'][key] * ENERGY_FACTOR[key][unit] / energy * 100

            # Per body weight
            weight_entry = self.get_closest_weight_entry()
            if weight_entry:
                for key in result['per_kg'].keys():
                    result['per_kg'][key] = result['total'][key] / weight_entry.weight

            # Only 2 decimal places, anything else doesn't make sense
            for key in result.keys():
                for i in result[key]:
                    result[key][i] = Decimal(result[key][i]).quantize(TWOPLACES)
            nutritional_representation = result
            cache.set(cache_mapper.get_nutrition_cache_by_key(self.pk), nutritional_representation)
        return nutritional_representation

    def get_closest_weight_entry(self):
        """
        Returns the closest weight entry for the nutrition plan.
        Returns None if there are no entries.
        """
        target = self.creation_date
        closest_entry_gte = WeightEntry.objects.filter(user=self.user) \
            .filter(date__gte=target).order_by('date').first()
        closest_entry_lte = WeightEntry.objects.filter(user=self.user) \
            .filter(date__lte=target).order_by('-date').first()
        if closest_entry_gte is None or closest_entry_lte is None:
            return closest_entry_gte or closest_entry_lte
        if abs(closest_entry_gte.date - target) < abs(closest_entry_lte.date - target):
            return closest_entry_gte
        else:
            return closest_entry_lte

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def get_calories_approximation(self):
        """
        Calculates the deviation from the goal calories and the actual
        amount of the current plan
        """

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

    def get_log_overview(self):
        """
        Returns an overview for all logs available for this plan
        """
        result = []
        for date in self.logitem_set.datetimes('datetime', 'day', order='DESC'):
            # TODO: in python 3.5 this can be simplified as z = {**x, **y}
            tmp = self.get_log_summary(date=date).copy()
            tmp.update({'date': date.date()})
            result.append(tmp)

        return result

    def get_log_entries(self, date=None):
        """
        Convenience function that returns the log entries for a given date
        """
        if not date:
            date = datetime.date.today()

        return self.logitem_set.filter(datetime__date=date).select_related()

    def get_log_summary(self, date=None):
        """
        Sums the nutritional info of the items logged for the given date
        """
        use_metric = self.user.userprofile.use_metric
        result = {'energy': 0,
                  'protein': 0,
                  'carbohydrates': 0,
                  'carbohydrates_sugar': 0,
                  'fat': 0,
                  'fat_saturated': 0,
                  'fibres': 0,
                  'sodium': 0}

        # Perform the sums
        for item in self.get_log_entries(date):
            values = item.get_nutritional_values(use_metric=use_metric)
            for key in result.keys():
                result[key] += values[key]
        return result


class IngredientCategory(models.Model):
    """
    Model for an Ingredient category
    """
    name = models.CharField(max_length=100,
                            verbose_name=_('Name'))

    # Metaclass to set some other properties
    class Meta:
        verbose_name_plural = _("Ingredient Categories")
        ordering = ["name", ]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def get_owner_object(self):
        """
        Category has no owner information
        """
        return False


class Ingredient(AbstractSubmissionModel, AbstractLicenseModel, models.Model):
    """
    An ingredient, with some approximate nutrition values
    """
    objects = SubmissionManager()
    """Custom manager"""

    ENERGY_APPROXIMATION = 15
    """
    How much the calculated energy from protein, etc. can deviate from the
    energy amount given (in percent).
    """

    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]

    # Meta data
    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'),
                                 editable=False,
                                 on_delete=models.CASCADE)

    creation_date = models.DateField(_('Date'), auto_now_add=True)
    update_date = models.DateField(_('Date'),
                                   auto_now=True,
                                   blank=True,
                                   editable=False)

    # Product infos
    name = models.CharField(max_length=200,
                            verbose_name=_('Name'),
                            validators=[MinLengthValidator(3)])

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

    code = models.CharField(max_length=200,
                            null=True,
                            blank=True,
                            db_index=True)
    """Internal ID of the source database, e.g. a barcode or similar"""

    source_name = models.CharField(max_length=200,
                                   null=True,
                                   blank=True)
    """Name of the source, such as Open Food Facts"""

    source_url = models.URLField(verbose_name=_('Link'),
                                 help_text=_('Link to product'),
                                 blank=True,
                                 null=True)
    """URL of the product at the source"""

    last_imported = models.DateTimeField(_('Date'), auto_now_add=True, null=True, blank=True)

    common_name = models.CharField(max_length=200,
                                   null=True,
                                   blank=True)

    category = models.ForeignKey(IngredientCategory,
                                 verbose_name=_('Category'),
                                 on_delete=models.CASCADE,
                                 null=True,
                                 blank=True)

    brand = models.CharField(max_length=200,
                             verbose_name=_('Brand name of product'),
                             null=True,
                             blank=True)

    #
    # Django methods
    #

    def get_absolute_url(self):
        """
        Returns the canonical URL to view this object.

        Since some names consist of only non-ascii characters (e.g. 감자깡), the
        resulting slug would be empty and no URL would match. In that case, use
        the regular URL with only the ID.
        """
        slug = slugify(self.name)
        if not slug:
            return reverse('nutrition:ingredient:view', kwargs={'id': self.id})
        else:
            return reverse('nutrition:ingredient:view',
                           kwargs={'id': self.id, 'slug': slug})

    def clean(self):
        """
        Do a very broad sanity check on the nutritional values according to
        the following rules:
        - 1g of protein: 4kcal
        - 1g of carbohydrates: 4kcal
        - 1g of fat: 9kcal

        The sum is then compared to the given total energy, with ENERGY_APPROXIMATION
        percent tolerance.
        """

        # Note: calculations in 100 grams, to save us the '/100' everywhere
        energy_protein = 0
        if self.protein:
            energy_protein = self.protein * ENERGY_FACTOR['protein']['kg']

        energy_carbohydrates = 0
        if self.carbohydrates:
            energy_carbohydrates = self.carbohydrates * ENERGY_FACTOR['carbohydrates']['kg']

        energy_fat = 0
        if self.fat:
            # TODO: for some reason, during the tests the fat value is not
            #       converted to decimal (django 1.9)
            energy_fat = Decimal(self.fat * ENERGY_FACTOR['fat']['kg'])

        energy_calculated = energy_protein + energy_carbohydrates + energy_fat

        # Compare the values, but be generous
        if self.energy:
            energy_upper = self.energy * (1 + (self.ENERGY_APPROXIMATION / Decimal(100.0)))
            energy_lower = self.energy * (1 - (self.ENERGY_APPROXIMATION / Decimal(100.0)))

            if not ((energy_upper > energy_calculated) and (energy_calculated > energy_lower)):
                raise ValidationError(
                    _('The total energy ({energy}kcal) is not the approximate sum of the '
                      'energy provided by protein, carbohydrates and fat ({energy_calculated}kcal '
                      '+/-{energy_approx}%)'.format(energy=self.energy,
                                                    energy_calculated=energy_calculated,
                                                    energy_approx=self.ENERGY_APPROXIMATION)))

    def save(self, *args, **kwargs):
        """
        Reset the cache
        """

        super(Ingredient, self).save(*args, **kwargs)
        cache.delete(cache_mapper.get_ingredient_key(self.id))

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def __eq__(self, other):
        """
        Compare ingredients based on their values, not like django on their PKs
        """

        logger.debug('Overwritten behaviour: comparing ingredients on values, not PK.')
        equal = True
        if isinstance(other, self.__class__):
            for i in self._meta.fields:
                if (hasattr(self, i.name)
                   and hasattr(other, i.name)
                   and (getattr(self, i.name, None) != getattr(other, i.name, None))):
                    equal = False
        else:
            equal = False
        return equal

    def __hash__(self):
        """
        Define a hash function

        This is rather unnecessary, but it seems that newer versions of django
        have a problem when the __eq__ function is implemented, but not the
        __hash__ one. Returning hash(pk) is also django's default.

        :return: hash(pk)
        """
        return hash(self.pk)

    #
    # Own methods
    #
    def compare_with_database(self):
        """
        Compares the current ingredient with the version saved in the database.

        If the current object has no PK, returns false
        """
        if not self.pk:
            return False

        ingredient = Ingredient.objects.get(pk=self.pk)
        if self != ingredient:
            return False
        else:
            return True

    def send_email(self, request):
        """
        Sends an email after being successfully added to the database (for user
        submitted ingredients only)
        """
        try:
            user = User.objects.get(username=self.license_author)
        except User.DoesNotExist:
            return

        if self.license_author and user.email:
            translation.activate(user.userprofile.notification_language.short_name)
            url = request.build_absolute_uri(self.get_absolute_url())
            subject = _('Ingredient was successfully added to the general database')
            context = {
                'ingredient': self.name,
                'url': url,
                'site': Site.objects.get_current().domain
            }
            message = render_to_string('ingredient/email_new.tpl', context)
            mail.send_mail(subject,
                           message,
                           settings.WGER_SETTINGS['EMAIL_FROM'],
                           [user.email],
                           fail_silently=True)

    def set_author(self, request):
        if request.user.has_perm('nutrition.add_ingredient'):
            self.status = Ingredient.STATUS_ACCEPTED
            if not self.license_author:
                self.license_author = request.get_host().split(':')[0]
        else:
            if not self.license_author:
                self.license_author = request.user.username

            # Send email to administrator
            subject = _('New user submitted ingredient')
            message = _("""The user {0} submitted a new ingredient "{1}".""".format(
                request.user.username, self.name))
            mail.mail_admins(subject,
                             message,
                             fail_silently=True)

    def get_owner_object(self):
        """
        Ingredient has no owner information
        """
        return False

    @property
    def energy_kilojoule(self):
        """
        returns kilojoules for current ingredient, 0 if energy is uninitialized
        """
        if self.energy:
            return Decimal(self.energy * 4.184).quantize(TWOPLACES)
        else:
            return 0


class WeightUnit(models.Model):
    """
    A more human usable weight unit (spoon, table, slice...)
    """

    language = models.ForeignKey(Language,
                                 verbose_name=_('Language'),
                                 editable=False,
                                 on_delete=models.CASCADE)
    name = models.CharField(max_length=200,
                            verbose_name=_('Name'), )

    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.name

    def get_owner_object(self):
        """
        Weight unit has no owner information
        """
        return None


class IngredientWeightUnit(models.Model):
    """
    A specific human usable weight unit for an ingredient
    """

    ingredient = models.ForeignKey(Ingredient,
                                   verbose_name=_('Ingredient'),
                                   editable=False,
                                   on_delete=models.CASCADE)
    unit = models.ForeignKey(WeightUnit, verbose_name=_('Weight unit'), on_delete=models.CASCADE)

    gram = models.IntegerField(verbose_name=_('Amount in grams'))
    amount = models.DecimalField(decimal_places=2,
                                 max_digits=5,
                                 default=1,
                                 verbose_name=_('Amount'),
                                 help_text=_('Unit amount, e.g. "1 Cup" or "1/2 spoon"'))

    def get_owner_object(self):
        """
        Weight unit has no owner information
        """
        return None

    def __str__(self):
        """
        Return a more human-readable representation
        """

        return "{0}{1} ({2}g)".format(self.amount if self.amount > 1 else '',
                                      self.unit.name,
                                      self.gram)


class Meal(models.Model):
    """
    A meal
    """

    # Metaclass to set some other properties
    class Meta:
        ordering = ["time", ]

    plan = models.ForeignKey(NutritionPlan,
                             verbose_name=_('Nutrition plan'),
                             editable=False,
                             on_delete=models.CASCADE)
    order = models.IntegerField(verbose_name=_('Order'),
                                blank=True,
                                editable=False)
    time = Html5TimeField(null=True,
                          blank=True,
                          verbose_name=_('Time (approx)'))

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return "{0} Meal".format(self.order)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.plan

    def get_nutritional_values(self, use_metric=True):
        """
        Sums the nutrional info of all items in the meal

        :param use_metric Flag that controls the units used
        """
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

        nutritional_info['energy_kilojoule'] = Decimal(nutritional_info['energy']) * Decimal(4.184)

        # Only 2 decimal places, anything else doesn't make sense
        for i in nutritional_info:
            nutritional_info[i] = Decimal(nutritional_info[i]).quantize(TWOPLACES)

        return nutritional_info


class BaseMealItem(object):
    """
    Base class for an item (component) of a meal or log

    This just provides some common helper functions
    """

    def get_unit_type(self):
        """
        Returns the type of unit used:
        - a value in grams
        - a 'human' unit like 'a cup' or 'a slice'
        """

        if self.weight_unit:
            return MEALITEM_WEIGHT_UNIT
        else:
            return MEALITEM_WEIGHT_GRAM

    def get_nutritional_values(self, use_metric=True):
        """
        Sums the nutritional info for the ingredient in the MealItem

        :param use_metric Flag that controls the units used
        """
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
            item_weight = (self.amount
                           * self.weight_unit.amount
                           * self.weight_unit.gram)

        nutritional_info['energy'] += self.ingredient.energy * item_weight / 100
        nutritional_info['protein'] += self.ingredient.protein * item_weight / 100
        nutritional_info['carbohydrates'] += self.ingredient.carbohydrates * item_weight / 100
        nutritional_info['fat'] += self.ingredient.fat * item_weight / 100

        if self.ingredient.carbohydrates_sugar:
            nutritional_info['carbohydrates_sugar'] += \
                self.ingredient.carbohydrates_sugar * item_weight / 100

        if self.ingredient.fat_saturated:
            nutritional_info['fat_saturated'] += self.ingredient.fat_saturated * item_weight / 100

        if self.ingredient.fibres:
            nutritional_info['fibres'] += self.ingredient.fibres * item_weight / 100

        if self.ingredient.sodium:
            nutritional_info['sodium'] += self.ingredient.sodium * item_weight / 100

        # If necessary, convert weight units
        if not use_metric:
            for key, value in nutritional_info.items():

                # Energy is not a weight!
                if key == 'energy':
                    continue

                # Everything else, to ounces
                nutritional_info[key] = AbstractWeight(value, 'g').oz

        nutritional_info['energy_kilojoule'] = Decimal(nutritional_info['energy']) * Decimal(4.184)

        # Only 2 decimal places, anything else doesn't make sense
        for i in nutritional_info:
            nutritional_info[i] = Decimal(nutritional_info[i]).quantize(TWOPLACES)

        return nutritional_info


class MealItem(BaseMealItem, models.Model):
    """
    An item (component) of a meal
    """

    meal = models.ForeignKey(Meal,
                             verbose_name=_('Nutrition plan'),
                             editable=False,
                             on_delete=models.CASCADE)
    ingredient = models.ForeignKey(Ingredient,
                                   verbose_name=_('Ingredient'),
                                   on_delete=models.CASCADE)
    weight_unit = models.ForeignKey(IngredientWeightUnit,
                                    verbose_name=_('Weight unit'),
                                    null=True,
                                    blank=True,
                                    on_delete=models.CASCADE)

    order = models.IntegerField(verbose_name=_('Order'),
                                blank=True,
                                editable=False)
    amount = models.DecimalField(decimal_places=2,
                                 max_digits=6,
                                 verbose_name=_('Amount'),
                                 validators=[MinValueValidator(1),
                                             MaxValueValidator(1000)])

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return "{0}g ingredient {1}".format(self.amount, self.ingredient_id)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.meal.plan


class LogItem(BaseMealItem, models.Model):
    """
    An item (component) of a log
    """
    # Metaclass to set some other properties
    class Meta:
        ordering = ["datetime", ]

    plan = models.ForeignKey(NutritionPlan,
                             verbose_name=_('Nutrition plan'),
                             on_delete=models.CASCADE)
    """
    The plan this log belongs to
    """

    datetime = models.DateTimeField(default=timezone.now)
    """
    Time and date when the log was added
    """

    comment = models.TextField(verbose_name=_('Comment'),
                               blank=True,
                               null=True)
    """
    Comment field, for additional information
    """

    ingredient = models.ForeignKey(Ingredient,
                                   verbose_name=_('Ingredient'),
                                   on_delete=models.CASCADE)
    """
    Ingredient
    """

    weight_unit = models.ForeignKey(IngredientWeightUnit,
                                    verbose_name=_('Weight unit'),
                                    null=True,
                                    blank=True,
                                    on_delete=models.CASCADE)
    """
    Weight unit used (grams, slices, etc.)
    """

    amount = models.DecimalField(decimal_places=2,
                                 max_digits=6,
                                 verbose_name=_('Amount'),
                                 validators=[MinValueValidator(1),
                                             MaxValueValidator(1000)])
    """
    The amount of units
    """

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return "Diary entry for {}, plan {}".format(self.datetime, self.plan.pk)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.plan
