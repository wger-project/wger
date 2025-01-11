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
import datetime
import decimal

# Django
from django.conf import settings
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.core.validators import (
    MaxValueValidator,
    MinValueValidator,
)
from django.db import models
from django.db.models import IntegerField
from django.utils.translation import gettext_lazy as _

# wger
from wger.gym.models import Gym
from wger.utils.constants import TWOPLACES
from wger.utils.units import (
    AbstractHeight,
    AbstractWeight,
)
from wger.weight.models import WeightEntry

# Local
from .language import Language


def birthdate_validator(birthdate):
    """
    Checks to see if entered birthdate (datetime.date object) is
    between 10 and 100 years of age.
    """
    max_year = birthdate.replace(year=(birthdate.year + 100))
    min_year = birthdate.replace(year=(birthdate.year + 10))
    today = datetime.date.today()
    if today > max_year or today < min_year:
        raise ValidationError(
            _('%(birthdate)s is not a valid birthdate'),
            params={'birthdate': birthdate},
        )


class UserProfile(models.Model):
    GENDER_MALE = '1'
    GENDER_FEMALE = '2'
    GENDER = (
        (GENDER_MALE, _('Male')),
        (GENDER_FEMALE, _('Female')),
    )

    INTENSITY_LOW = '1'
    INTENSITY_MEDIUM = '2'
    INTENSITY_HIGH = '3'
    INTENSITY = (
        (INTENSITY_LOW, _('Low')),
        (INTENSITY_MEDIUM, _('Medium')),
        (INTENSITY_HIGH, _('High')),
    )

    UNITS_KG = 'kg'
    UNITS_LB = 'lb'
    UNITS = (
        (UNITS_KG, _('Metric (kilogram)')),
        (UNITS_LB, _('Imperial (pound)')),
    )

    user = models.OneToOneField(
        User,
        editable=False,
        on_delete=models.CASCADE,
    )
    """
    The user
    """

    gym = models.ForeignKey(
        Gym,
        editable=False,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
    )
    """
    The gym this user belongs to, if any
    """

    email_verified = models.BooleanField(default=False)
    """Flag indicating whether the user's email has been verified"""

    is_temporary = models.BooleanField(default=False, editable=False)
    """
    Flag to mark a temporary user (demo account)
    """

    #
    # User preferences
    #

    show_comments = models.BooleanField(
        verbose_name=_('Show exercise comments'),
        help_text=_('Check to show exercise comments on the workout view'),
        default=True,
    )
    """
    Show exercise comments on workout view
    """

    # Also show ingredients in english while composing a nutritional plan
    # (obviously this is only meaningful if the user has a language other than english)
    show_english_ingredients = models.BooleanField(
        verbose_name=_('Also use ingredients in English'),
        help_text=_(
            """Check to also show ingredients in English while creating
a nutritional plan. These ingredients are extracted from a list provided
by the US Department of Agriculture. It is extremely complete, with around
7000 entries, but can be somewhat overwhelming and make the search difficult."""
        ),
        default=True,
    )

    workout_reminder_active = models.BooleanField(
        verbose_name=_('Activate workout reminders'),
        help_text=_(
            'Check to activate automatic '
            'reminders for workouts. You need '
            'to provide a valid email for this '
            'to work.'
        ),
        default=False,
    )

    workout_reminder = IntegerField(
        verbose_name=_('Remind before expiration'),
        help_text=_('The number of days you want to be reminded before a workout expires.'),
        default=14,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
    )
    workout_duration = IntegerField(
        verbose_name=_('Default duration of workouts'),
        help_text=_(
            'Default duration in weeks of workouts not '
            'in a schedule. Used for email workout '
            'reminders.'
        ),
        default=12,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
    )
    last_workout_notification = models.DateField(editable=False, blank=False, null=True)
    """
    The last time the user got a workout reminder email

    This is needed e.g. to check daily per cron for old workouts but only
    send users an email once per week
    """

    notification_language = models.ForeignKey(
        Language,
        verbose_name=_('Notification language'),
        help_text=_(
            'Language to use when sending you email '
            'notifications, e.g. email reminders for '
            'workouts. This does not affect the '
            'language used on the website.'
        ),
        default=2,
        on_delete=models.CASCADE,
    )

    @property
    def is_trustworthy(self) -> bool:
        """
        Flag indicating whether the user "is trustworthy" and can submit or edit exercises

        At the moment the criteria are:
        - the account has existed for 3 weeks
        - the email address has been verified
        """

        # Superusers are always trustworthy
        if self.user.is_superuser:
            return True

        # Temporary users are never trustworthy
        if self.is_temporary:
            return False

        days_since_joined = datetime.date.today() - self.user.date_joined.date()
        minimum_account_age = settings.WGER_SETTINGS['MIN_ACCOUNT_AGE_TO_TRUST']

        return days_since_joined.days > minimum_account_age and self.email_verified

    #
    # User statistics
    #
    age = IntegerField(
        verbose_name=_('Age'),
        blank=False,
        null=True,
        validators=[MinValueValidator(10), MaxValueValidator(100)],
    )
    """The user's age"""

    birthdate = models.DateField(
        verbose_name=_('Date of Birth'),
        blank=False,
        null=True,
        validators=[birthdate_validator],
    )
    """The user's date of birth"""

    height = IntegerField(
        verbose_name=_('Height (cm)'),
        blank=False,
        validators=[MinValueValidator(140), MaxValueValidator(230)],
        null=True,
    )
    """The user's height"""

    gender = models.CharField(
        max_length=1,
        choices=GENDER,
        default=GENDER_MALE,
        blank=False,
        null=True,
    )
    """Gender"""

    sleep_hours = IntegerField(
        verbose_name=_('Hours of sleep'),
        help_text=_('The average hours of sleep per day'),
        default=7,
        blank=False,
        null=True,
        validators=[MinValueValidator(4), MaxValueValidator(10)],
    )
    """The average hours of sleep per day"""

    work_hours = IntegerField(
        verbose_name=_('Work'),
        help_text=_('Average hours per day'),
        default=8,
        blank=False,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(15)],
    )
    """The average hours at work per day"""

    work_intensity = models.CharField(
        verbose_name=_('Physical intensity'),
        help_text=_('Approximately'),
        max_length=1,
        choices=INTENSITY,
        default=INTENSITY_LOW,
        blank=False,
        null=True,
    )
    """Physical intensity of work"""

    sport_hours = IntegerField(
        verbose_name=_('Sport'),
        help_text=_('Average hours per week'),
        default=3,
        blank=False,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(30)],
    )
    """The average hours performing sports per week"""

    sport_intensity = models.CharField(
        verbose_name=_('Physical intensity'),
        help_text=_('Approximately'),
        max_length=1,
        choices=INTENSITY,
        default=INTENSITY_MEDIUM,
        blank=False,
        null=True,
    )
    """Physical intensity of sport activities"""

    freetime_hours = IntegerField(
        verbose_name=_('Free time'),
        help_text=_('Average hours per day'),
        default=8,
        blank=False,
        null=True,
        validators=[MinValueValidator(1), MaxValueValidator(15)],
    )
    """The average hours of free time per day"""

    freetime_intensity = models.CharField(
        verbose_name=_('Physical intensity'),
        help_text=_('Approximately'),
        max_length=1,
        choices=INTENSITY,
        default=INTENSITY_LOW,
        blank=False,
        null=True,
    )
    """Physical intensity during free time"""

    calories = IntegerField(
        verbose_name=_('Total daily calories'),
        help_text=_('Total caloric intake, including e.g. any surplus'),
        default=2500,
        blank=False,
        null=True,
        validators=[MinValueValidator(1500), MaxValueValidator(5000)],
    )
    """Basic caloric intake based on physical activity"""

    #
    # Others
    #
    weight_unit = models.CharField(
        verbose_name=_('Weight unit'),
        max_length=2,
        choices=UNITS,
        default=UNITS_KG,
    )
    """Preferred weight unit"""

    ro_access = models.BooleanField(
        verbose_name=_('Allow external access'),
        help_text=_(
            'Allow external users to access your workouts and '
            'logs in a read-only mode. You need to set this '
            'before you can share links e.g. to social media.'
        ),
        default=False,
    )
    """Allow anonymous read-only access"""

    num_days_weight_reminder = models.IntegerField(
        verbose_name=_('Automatic reminders for weight entries'),
        help_text=_('Number of days after the last weight entry (enter 0 to deactivate)'),
        validators=[MinValueValidator(0), MaxValueValidator(30)],
        default=0,
    )
    """Number of Days for email weight reminder"""

    #
    # API
    #
    added_by = models.ForeignKey(
        User,
        editable=False,
        null=True,
        related_name='added_by',
        on_delete=models.CASCADE,
    )
    """User that originally registered this user via REST API"""

    can_add_user = models.BooleanField(default=False, editable=False)
    """
    Flag to indicate whether the (app) user can register other users on his
    behalf over the REST API
    """

    @property
    def weight(self):
        """
        Returns the last weight entry, done here to make the behaviour
        more consistent with the other settings (age, height, etc.)
        """
        try:
            weight = WeightEntry.objects.filter(user=self.user).latest().weight
        except WeightEntry.DoesNotExist:
            weight = 0
        return weight

    @property
    def address(self):
        """
        Return the address as saved in the current contract (user's gym)
        """
        out = {
            'zip_code': '',
            'city': '',
            'street': '',
            'phone': '',
        }
        if self.user.contract_member.exists():
            last_contract = self.user.contract_member.last()
            out['zip_code'] = last_contract.zip_code
            out['city'] = last_contract.city
            out['street'] = last_contract.street
            out['phone'] = last_contract.phone

        return out

    def clean(self):
        """
        Make sure the total amount of hours is 24
        """
        if (self.sleep_hours and self.freetime_hours and self.work_hours) and (
            self.sleep_hours + self.freetime_hours + self.work_hours
        ) > 24:
            raise ValidationError(_('The sum of all hours has to be 24'))

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Profile for user {self.user}'

    @property
    def use_metric(self):
        """
        Simple helper that checks whether the user uses metric units or not
        :return: Boolean
        """
        return self.weight_unit == 'kg'

    def calculate_bmi(self):
        """
        Calculates the user's BMI

        Formula: weight/height^2
        - weight in kg
        - height in m
        """

        # If not all the data is available, return 0, otherwise the result
        # of the calculation below breaks django's template filters
        if not self.weight or not self.height:
            return 0

        weight = self.weight if self.use_metric else AbstractWeight(self.weight, 'lb').kg
        height = self.height if self.use_metric else AbstractHeight(self.height, 'inches').inches
        return weight / pow(height / decimal.Decimal(100), 2)

    def calculate_basal_metabolic_rate(self, formula=1):
        """
        Calculates the basal metabolic rate.

        Currently only the Mifflin-St.Jeor formula is supported
        """
        factor = 5 if self.gender == self.GENDER_MALE else -161
        weight = self.weight if self.use_metric else AbstractWeight(self.weight, 'lb').kg

        try:
            rate = (
                (10 * weight)  # in kg
                + (decimal.Decimal(6.25) * self.height)  # in cm
                - (5 * self.age)  # in years
                + factor
            )
        # Any of the entries is missing
        except TypeError:
            rate = 0

        return decimal.Decimal(str(rate)).quantize(TWOPLACES)

    def calculate_activities(self):
        """
        Calculates the calories needed by additional physical activities

        Factors taken from
        * https://en.wikipedia.org/wiki/Physical_activity_level
        * http://www.fao.org/docrep/007/y5686e/y5686e07.htm
        """
        # Sleep
        sleep = self.sleep_hours * 0.95

        # Work
        if self.work_intensity == self.INTENSITY_LOW:
            work_factor = 1.5
        elif self.work_intensity == self.INTENSITY_MEDIUM:
            work_factor = 1.8
        else:
            work_factor = 2.2
        work = self.work_hours * work_factor

        # Sport (entered in hours/week, so we must divide)
        if self.sport_intensity == self.INTENSITY_LOW:
            sport_factor = 4
        elif self.sport_intensity == self.INTENSITY_MEDIUM:
            sport_factor = 6
        else:
            sport_factor = 10
        sport = (self.sport_hours / 7.0) * sport_factor

        # Free time
        if self.freetime_intensity == self.INTENSITY_LOW:
            freetime_factor = 1.3
        elif self.freetime_intensity == self.INTENSITY_MEDIUM:
            freetime_factor = 1.9
        else:
            freetime_factor = 2.4
        freetime = self.freetime_hours * freetime_factor

        # Total
        total = (sleep + work + sport + freetime) / 24.0
        return decimal.Decimal(str(total)).quantize(TWOPLACES)

    def user_bodyweight(self, weight):
        """
        Create a new weight entry as needed
        """
        if not WeightEntry.objects.filter(user=self.user).exists() or (
            datetime.date.today() - WeightEntry.objects.filter(user=self.user).latest().date
            > datetime.timedelta(days=3)
        ):
            entry = WeightEntry()
            entry.weight = weight
            entry.user = self.user
            entry.date = datetime.date.today()
            entry.save()

        # Update the last entry
        else:
            entry = WeightEntry.objects.filter(user=self.user).latest()
            entry.weight = weight
            entry.save()
        return entry

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self
