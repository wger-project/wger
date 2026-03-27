#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import logging
import uuid as uuid
from decimal import (
    ROUND_HALF_UP,
    Decimal,
)
from json import JSONDecodeError

# Django
from django.conf import settings
from django.contrib.postgres.indexes import GinIndex
from django.core.cache import cache
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinLengthValidator,
    MinValueValidator,
)
from django.db import models
from django.http import HttpRequest
from django.urls import reverse
from django.utils.text import slugify

# Third Party
from openfoodfacts import API
from requests import (
    ConnectTimeout,
    HTTPError,
    ReadTimeout,
)

# wger
from wger.core.models import Language
from wger.nutrition.consts import (
    ENERGY_FACTOR,
    KJ_PER_KCAL,
)
from wger.nutrition.managers import ApproximateCountManager
from wger.nutrition.models.ingredient_category import IngredientCategory
from wger.nutrition.models.sources import Source
from wger.utils.cache import cache_mapper
from wger.utils.constants import TWOPLACES
from wger.utils.language import load_language
from wger.utils.models import AbstractLicenseModel
from wger.utils.requests import wger_user_agent


logger = logging.getLogger(__name__)


class Ingredient(AbstractLicenseModel, models.Model):
    """
    An ingredient, with some approximate nutrition values
    """

    class Meta:
        ordering = [
            'name',
        ]
        indexes = (
            GinIndex(
                fields=['name'],
                name='nutrition_i_search__f274b7_gin',
            ),
            models.Index(
                fields=['last_update'],
                name='idx_ingredient_last_update',
            ),
            models.Index(
                fields=['last_imported'],
                name='idx_ingredient_last_imported',
            ),
            models.Index(
                fields=['is_vegan'],
                name='idx_ingredient_vegan',
                condition=models.Q(is_vegan=True),
            ),
            models.Index(
                fields=['is_vegetarian'],
                name='idx_ingredient_vegetarian',
                condition=models.Q(is_vegetarian=True),
            ),
            models.Index(
                fields=['nutriscore'],
                name='idx_ingredient_nutriscore',
            ),
        )

    ENERGY_APPROXIMATION = 15
    """
    How much the calculated energy from protein, etc. can deviate from the
    energy amount given (in percent).
    """

    objects = ApproximateCountManager()

    language = models.ForeignKey(
        Language,
        verbose_name='Language',
        editable=False,
        on_delete=models.CASCADE,
    )

    created = models.DateTimeField(
        verbose_name='Date',
        auto_now_add=True,
    )
    """Date when the ingredient was created"""

    last_update = models.DateTimeField(
        'Date',
        auto_now=True,
        blank=True,
        editable=False,
    )
    """Last update time"""

    last_image_check = models.DateTimeField(
        blank=True,
        editable=False,
        default=None,
        null=True,
    )
    """
    Last time we checked for an image.

    This is used to prevent trying to fetch images over and over again from an
    ingredient that does not have any.

    In the future, this field can be used to renew existing images.
    """

    uuid = models.UUIDField(
        default=uuid.uuid4,
        unique=True,
        editable=False,
        verbose_name='UUID',
    )
    """Globally unique ID, to identify the ingredient across installations"""

    # Product infos
    name = models.CharField(
        max_length=200,
        verbose_name='Name',
        validators=[MinLengthValidator(3)],
    )

    energy = models.IntegerField(
        verbose_name='Energy',
        help_text='In kcal per 100g',
    )

    protein = models.DecimalField(
        decimal_places=3,
        max_digits=6,
        verbose_name='Protein',
        help_text='In g per 100g of product',
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(100))],
    )

    carbohydrates = models.DecimalField(
        decimal_places=3,
        max_digits=6,
        verbose_name='Carbohydrates',
        help_text='In g per 100g of product',
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(100))],
    )

    carbohydrates_sugar = models.DecimalField(
        decimal_places=3,
        max_digits=6,
        blank=True,
        null=True,
        verbose_name='Sugar content in carbohydrates',
        help_text='In g per 100g of product',
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(100))],
    )

    fat = models.DecimalField(
        decimal_places=3,
        max_digits=6,
        verbose_name='Fat',
        help_text='In g per 100g of product',
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(100))],
    )

    fat_saturated = models.DecimalField(
        decimal_places=3,
        max_digits=6,
        blank=True,
        null=True,
        verbose_name='Saturated fat content in fats',
        help_text='In g per 100g of product',
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(100))],
    )

    fiber = models.DecimalField(
        decimal_places=3,
        max_digits=6,
        blank=True,
        null=True,
        verbose_name='Fiber',
        help_text='In g per 100g of product',
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(100))],
    )

    sodium = models.DecimalField(
        decimal_places=3,
        max_digits=6,
        blank=True,
        null=True,
        verbose_name='Sodium',
        help_text='In g per 100g of product',
        validators=[MinValueValidator(Decimal(0)), MaxValueValidator(Decimal(100))],
    )

    code = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_index=True,
    )
    """The product's barcode"""

    remote_id = models.CharField(
        max_length=200,
        null=True,
        blank=True,
        db_index=True,
    )
    """ID of the product in the external source database. Used for updated during imports."""

    source_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    """Name of the source, such as Open Food Facts"""

    source_url = models.URLField(
        verbose_name='Link',
        help_text='Link to product',
        blank=True,
        null=True,
    )
    """URL of the product at the source"""

    last_imported = models.DateTimeField(
        'Date',
        auto_now_add=True,
        null=True,
        blank=True,
    )

    common_name = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )

    category = models.ForeignKey(
        IngredientCategory,
        verbose_name='Category',
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )

    brand = models.CharField(
        max_length=200,
        verbose_name='Brand name of product',
        null=True,
        blank=True,
    )

    is_vegan = models.BooleanField(
        verbose_name='Vegan',
        help_text='Whether the ingredient is suitable for a vegan diet',
        null=True,
        blank=True,
        default=None,
    )
    """Dietary classification from Open Food Facts ingredients_analysis_tags"""

    is_vegetarian = models.BooleanField(
        verbose_name='Vegetarian',
        help_text='Whether the ingredient is suitable for a vegetarian diet',
        null=True,
        blank=True,
        default=None,
    )
    """Dietary classification from Open Food Facts ingredients_analysis_tags"""

    NUTRISCORE_CHOICES = [
        ('a', 'A'),
        ('b', 'B'),
        ('c', 'C'),
        ('d', 'D'),
        ('e', 'E'),
    ]

    nutriscore = models.CharField(
        max_length=1,
        choices=NUTRISCORE_CHOICES,
        verbose_name='Nutri-Score',
        help_text='Nutri-Score grade from Open Food Facts',
        null=True,
        blank=True,
        default=None,
    )
    """Nutri-Score from Open Food Facts"""

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
            return reverse('nutrition:ingredient:view', kwargs={'pk': self.id})
        else:
            return reverse('nutrition:ingredient:view', kwargs={'pk': self.id, 'slug': slug})

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
                    f'The total energy ({self.energy}kcal) is not the approximate sum of the '
                    f'energy provided by protein, carbohydrates and fat ({energy_calculated}kcal'
                    f' +/-{self.ENERGY_APPROXIMATION}%)'
                )

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
            for i in (
                'carbohydrates',
                'carbohydrates_sugar',
                'creation_date',
                'energy',
                'fat',
                'fat_saturated',
                'fiber',
                'name',
                'protein',
                'sodium',
            ):
                if (
                    hasattr(self, i)
                    and hasattr(other, i)
                    and (getattr(self, i, None) != getattr(other, i, None))
                ):
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
    def set_author(self, request):
        if not self.license_author:
            self.license_author = request.get_host().split(':')[0]

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
            return Decimal(self.energy * KJ_PER_KCAL).quantize(TWOPLACES)
        else:
            return 0

    @property
    def off_link(self):
        if self.source_name == Source.OPEN_FOOD_FACTS.value:
            return f'https://world.openfoodfacts.org/product/{self.code}/'

    def get_image(self, request: HttpRequest):
        """
        Returns the ingredient image

        If it is not available locally, it is fetched from Open Food Facts servers
        """

        if hasattr(self, 'image'):
            return self.image

        if not request.user.is_authenticated:
            return

        if not settings.WGER_SETTINGS['USE_CELERY']:
            logger.info('Celery deactivated, skipping retrieving ingredient image')
            return

        # Let celery fetch the image
        # wger
        from wger.nutrition.tasks import fetch_ingredient_image_task

        fetch_ingredient_image_task.delay(self.pk)

    def update_or_create_serving_unit_from_off(self, ingredient_data):
        """
        Fetch serving size from OFF and update or create a record of it.

        Returns (boolean, boolean). First boolean is whether serving unit was created,
        second boolean whether it was updated.
        """
        if not ingredient_data.serving_size_unit:
            return False, False

        gram = ingredient_data.serving_size_gram
        if not gram:
            gram = self._derive_serving_size_gram(
                ingredient_data.serving_size_amount,
                ingredient_data.serving_size_unit,
            )

        if not gram:
            return False, False

        # Local imports to avoid model import cycles.
        # wger
        from wger.nutrition.models import (
            IngredientWeightUnit,
            WeightUnit,
        )

        unit = WeightUnit.objects.filter(
            language_id=self.language_id,
            name__iexact=ingredient_data.serving_size_unit,
        ).first()
        if not unit:
            unit = WeightUnit.objects.create(
                language_id=self.language_id,
                name=ingredient_data.serving_size_unit,
            )

        amount = ingredient_data.serving_size_amount or 1  # if no amount is given, assume 1.
        amount = Decimal(str(amount)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)

        existing_weight_unit = IngredientWeightUnit.objects.filter(
            ingredient=self,
            unit=unit,
        ).first()

        if existing_weight_unit:
            existing_weight_unit.gram = gram
            existing_weight_unit.amount = amount
            existing_weight_unit.save(update_fields=['gram', 'amount'])
            return False, True  # (created, updated)
        else:
            IngredientWeightUnit.objects.create(
                ingredient=self,
                unit=unit,
                gram=gram,
                amount=amount,
            )
            return True, False  # (created, updated)

    @staticmethod
    def _derive_serving_size_gram(amount, unit):
        """
        Derive gram equivalents for volume-based servings using 1 g/ml fallback.
        """
        if not amount or not unit:
            return None

        normalized_unit = unit.strip().lower()
        conversion = {
            'ml': 1,
            'milliliter': 1,
            'millilitre': 1,
            'cl': 10,
            'centiliter': 10,
            'centilitre': 10,
            'dl': 100,
            'deciliter': 100,
            'decilitre': 100,
            'l': 1000,
            'liter': 1000,
            'litre': 1000,
        }

        if normalized_unit not in conversion:
            return None

        try:
            return int(round(float(amount) * conversion[normalized_unit]))
        except (TypeError, ValueError):
            return None

    @staticmethod
    def _fetch_off_product(code: str, context: str = ''):
        """
        Fetch product data from OFF and handle transient API errors.
        """
        try:
            api = API(user_agent=wger_user_agent(), timeout=3)
            return api.product.get(code)
        except JSONDecodeError as e:
            logger.info(f'Got JSONDecodeError from OFF{context}: {e}')
        except (ReadTimeout, ConnectTimeout):
            logger.info(f'Timeout from OFF{context}')
        except HTTPError as e:
            logger.info(f'Got HTTPError from OFF{context}: {e}')

        return None

    @staticmethod
    def _extract_off_ingredient_data(result: dict, language_id: int):
        """
        Extract normalized ingredient data from an OFF payload.
        """
        # wger
        from wger.nutrition.extract_info.off import extract_info_from_off

        try:
            return extract_info_from_off(result, language_id)
        except (KeyError, ValueError) as e:
            logger.debug(f'Error extracting data from OFF: {e}')
            return None

    def sync_serving_unit_from_off_if_missing(self):
        """
        Fetch serving-size data from OFF for existing ingredients missing local units.
        """
        if self.source_name != Source.OPEN_FOOD_FACTS.value or not self.code:
            return (False, False)

        if self.ingredientweightunit_set.exists():
            return (False, False)

        result = self._fetch_off_product(self.code, ' while syncing serving size')

        if not result:
            return (False, False)

        ingredient_data = self._extract_off_ingredient_data(result, self.language_id)
        if not ingredient_data:
            return (False, False)

        return self.update_or_create_serving_unit_from_off(ingredient_data)

    @classmethod
    def fetch_ingredient_from_off(cls, code: str):
        """
        Searches OFF by barcode and creates a local ingredient from the result
        """
        logger.info(f'Searching for ingredient {code} in OFF')
        result = cls._fetch_off_product(code)

        if not result:
            logger.info('Product not found')
            return None

        language = load_language(result.get('lang'))
        if not language:
            return None

        ingredient_data = cls._extract_off_ingredient_data(result, language.pk)
        if not ingredient_data:
            return None

        if not ingredient_data.name:
            return None

        ingredient = cls(**ingredient_data.dict())
        ingredient.save()
        ingredient.update_or_create_serving_unit_from_off(ingredient_data)
        logger.info(f'Ingredient found and saved to local database: {ingredient.uuid}')
        return ingredient
