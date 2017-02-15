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

import datetime
import decimal

from django.db import models
from django.db.models import IntegerField
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.encoding import python_2_unicode_compatible
from django.utils.translation import ugettext_lazy as _
from wger.gym.models import Gym

from wger.utils.constants import TWOPLACES
from wger.utils.units import AbstractWeight

from wger.weight.models import WeightEntry


@python_2_unicode_compatible
class Language(models.Model):
    '''
    Language of an item (exercise, workout, etc.)
    '''

    # e.g. 'de'
    short_name = models.CharField(max_length=2,
                                  verbose_name=_('Language short name'))

    # e.g. 'Deutsch'
    full_name = models.CharField(max_length=30,
                                 verbose_name=_('Language full name'))

    class Meta:
        '''
        Set Meta options
        '''
        ordering = ["full_name", ]

    #
    # Django methods
    #
    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0} ({1})".format(self.full_name, self.short_name)

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view a language
        '''
        return reverse('core:language:view', kwargs={'pk': self.id})

    #
    # Own methods
    #
    def get_owner_object(self):
        '''
        Muscle has no owner information
        '''
        return False


@python_2_unicode_compatible
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
        (UNITS_LB, _('Imperial (pound)'))
    )

    user = models.OneToOneField(User,
                                editable=False)
    '''
    The user
    '''

    gym = models.ForeignKey(Gym,
                            editable=False,
                            null=True,
                            blank=True)
    '''
    The gym this user belongs to, if any
    '''

    is_temporary = models.BooleanField(default=False,
                                       editable=False)
    '''
    Flag to mark a temporary user (demo account)
    '''

    #
    # User preferences
    #

    show_comments = models.BooleanField(verbose_name=_('Show exercise comments'),
                                        help_text=_('Check to show exercise comments on the '
                                                    'workout view'),
                                        default=True)
    '''
    Show exercise comments on workout view
    '''

    # Also show ingredients in english while composing a nutritional plan
    # (obviously this is only meaningful if the user has a language other than english)
    show_english_ingredients = models.BooleanField(
        verbose_name=_('Also use ingredients in English'),
        help_text=_('''Check to also show ingredients in English while creating
a nutritional plan. These ingredients are extracted from a list provided
by the US Department of Agriculture. It is extremely complete, with around
7000 entries, but can be somewhat overwhelming and make the search difficult.'''),
        default=True)

    workout_reminder_active = models.BooleanField(verbose_name=_('Activate workout reminders'),
                                                  help_text=_('Check to activate automatic '
                                                              'reminders for workouts. You need '
                                                              'to provide a valid email for this '
                                                              'to work.'),
                                                  default=False)

    workout_reminder = IntegerField(verbose_name=_('Remind before expiration'),
                                    help_text=_('The number of days you want to be reminded '
                                                'before a workout expires.'),
                                    default=14,
                                    validators=[MinValueValidator(1), MaxValueValidator(30)])
    workout_duration = IntegerField(verbose_name=_('Default duration of workouts'),
                                    help_text=_('Default duration in weeks of workouts not '
                                                'in a schedule. Used for email workout '
                                                'reminders.'),
                                    default=12,
                                    validators=[MinValueValidator(1), MaxValueValidator(30)])
    last_workout_notification = models.DateField(editable=False,
                                                 blank=False,
                                                 null=True)
    '''
    The last time the user got a workout reminder email

    This is needed e.g. to check daily per cron for old workouts but only
    send users an email once per week
    '''

    notification_language = models.ForeignKey(Language,
                                              verbose_name=_('Notification language'),
                                              help_text=_('Language to use when sending you email '
                                                          'notifications, e.g. email reminders for '
                                                          'workouts. This does not affect the '
                                                          'language used on the website.'),
                                              default=2)

    timer_active = models.BooleanField(verbose_name=_('Use pauses in workout timer'),
                                       help_text=_('Check to activate timer pauses between '
                                                   'exercises.'),
                                       default=True)
    '''
    Switch to activate pauses in the gym view
    '''

    timer_pause = IntegerField(verbose_name=_('Default duration of workout pauses'),
                               help_text=_('Default duration in seconds of pauses used by '
                                           'the timer in the gym mode.'),
                               default=90,
                               validators=[MinValueValidator(10), MaxValueValidator(400)])
    '''
    Default duration of workout pauses in the gym view
    '''

    #
    # User statistics
    #
    age = IntegerField(verbose_name=_('Age'),
                       blank=False,
                       null=True,
                       validators=[MinValueValidator(10), MaxValueValidator(100)])
    '''The user's age'''

    height = IntegerField(verbose_name=_('Height (cm)'),
                          blank=False,
                          validators=[MinValueValidator(140), MaxValueValidator(230)],
                          null=True)
    '''The user's height'''

    gender = models.CharField(max_length=1,
                              choices=GENDER,
                              default=GENDER_MALE,
                              blank=False,
                              null=True)
    '''Gender'''

    sleep_hours = IntegerField(verbose_name=_('Hours of sleep'),
                               help_text=_('The average hours of sleep per day'),
                               default=7,
                               blank=False,
                               null=True,
                               validators=[MinValueValidator(4), MaxValueValidator(10)])
    '''The average hours of sleep per day'''

    work_hours = IntegerField(verbose_name=_('Work'),
                              help_text=_('Average hours per day'),
                              default=8,
                              blank=False,
                              null=True,
                              validators=[MinValueValidator(1), MaxValueValidator(15)])
    '''The average hours at work per day'''

    work_intensity = models.CharField(verbose_name=_('Physical intensity'),
                                      help_text=_('Approximately'),
                                      max_length=1,
                                      choices=INTENSITY,
                                      default=INTENSITY_LOW,
                                      blank=False,
                                      null=True)
    '''Physical intensity of work'''

    sport_hours = IntegerField(verbose_name=_('Sport'),
                               help_text=_('Average hours per week'),
                               default=3,
                               blank=False,
                               null=True,
                               validators=[MinValueValidator(1), MaxValueValidator(30)])
    '''The average hours performing sports per week'''

    sport_intensity = models.CharField(verbose_name=_('Physical intensity'),
                                       help_text=_('Approximately'),
                                       max_length=1,
                                       choices=INTENSITY,
                                       default=INTENSITY_MEDIUM,
                                       blank=False,
                                       null=True)
    '''Physical intensity of sport activities'''

    freetime_hours = IntegerField(verbose_name=_('Free time'),
                                  help_text=_('Average hours per day'),
                                  default=8,
                                  blank=False,
                                  null=True,
                                  validators=[MinValueValidator(1), MaxValueValidator(15)])
    '''The average hours of free time per day'''

    freetime_intensity = models.CharField(verbose_name=_('Physical intensity'),
                                          help_text=_('Approximately'),
                                          max_length=1,
                                          choices=INTENSITY,
                                          default=INTENSITY_LOW,
                                          blank=False,
                                          null=True)
    '''Physical intensity during free time'''

    calories = IntegerField(verbose_name=_('Total daily calories'),
                            help_text=_('Total caloric intake, including e.g. any surplus'),
                            default=2500,
                            blank=False,
                            null=True,
                            validators=[MinValueValidator(1500), MaxValueValidator(5000)])
    '''Basic caloric intake based on physical activity'''

    #
    # Others
    #
    weight_unit = models.CharField(verbose_name=_('Weight unit'),
                                   max_length=2,
                                   choices=UNITS,
                                   default=UNITS_KG)
    '''Preferred weight unit'''

    ro_access = models.BooleanField(verbose_name=_('Allow external access'),
                                    help_text=_('Allow external users to access your workouts and '
                                                'logs in a read-only mode. You need to set this '
                                                'before you can share links e.g. to social media.'),
                                    default=False)
    '''Allow anonymous read-only access'''

    num_days_weight_reminder = models.IntegerField(verbose_name=_('Automatic reminders for weight '
                                                                  'entries'),
                                                   help_text=_('Number of days after the last '
                                                               'weight entry (enter 0 to '
                                                               'deactivate)'),
                                                   validators=[MinValueValidator(0),
                                                               MaxValueValidator(30)],
                                                   default=0)
    '''Number of Days for email weight reminder'''

    @property
    def weight(self):
        '''
        Returns the last weight entry, done here to make the behaviour
        more consistent with the other settings (age, height, etc.)
        '''
        try:
            weight = WeightEntry.objects.filter(user=self.user).latest().weight
        except WeightEntry.DoesNotExist:
            weight = 0
        return weight

    @property
    def address(self):
        '''
        Return the address as saved in the current contract (user's gym)
        '''
        out = {'zip_code': '',
               'city': '',
               'street': '',
               'phone': ''}
        if self.user.contract_member.exists():
            last_contract = self.user.contract_member.last()
            out['zip_code'] = last_contract.zip_code
            out['city'] = last_contract.city
            out['street'] = last_contract.street
            out['phone'] = last_contract.phone

        return out

    def clean(self):
        '''
        Make sure the total amount of hours is 24
        '''
        if ((self.sleep_hours and self.freetime_hours and self.work_hours)
           and (self.sleep_hours + self.freetime_hours + self.work_hours) > 24):
                raise ValidationError(_('The sum of all hours has to be 24'))

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"Profile for user {0}".format(self.user)

    @property
    def use_metric(self):
        '''
        Simple helper that checks whether the user uses metric units or not
        :return: Boolean
        '''
        return self.weight_unit == 'kg'

    def calculate_bmi(self):
        '''
        Calculates the user's BMI

        Formula: weight/height^2
        - weight in kg
        - height in m
        '''

        # If not all the data is available, return 0, otherwise the result
        # of the calculation below breaks django's template filters
        if not self.weight or not self.height:
            return 0

        weight = self.weight if self.use_metric else AbstractWeight(self.weight, 'lb').kg
        return weight / (self.height / decimal.Decimal(100) *
                         self.height / decimal.Decimal(100.0))

    def calculate_basal_metabolic_rate(self, formula=1):
        '''
        Calculates the basal metabolic rate.

        Currently only the Mifflin-St.Jeor formula is supported
        '''
        factor = 5 if self.gender == self.GENDER_MALE else -161
        weight = self.weight if self.use_metric else AbstractWeight(self.weight, 'lb').kg

        try:
            rate = ((10 * weight)  # in kg
                    + (decimal.Decimal(6.25) * self.height)  # in cm
                    - (5 * self.age)  # in years
                    + factor)
        # Any of the entries is missing
        except TypeError:
            rate = 0

        return decimal.Decimal(str(rate)).quantize(TWOPLACES)

    def calculate_activities(self):
        '''
        Calculates the calories needed by additional physical activities

        Factors taken from
        * https://en.wikipedia.org/wiki/Physical_activity_level
        * http://www.fao.org/docrep/007/y5686e/y5686e07.htm
        '''
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
        '''
        Create a new weight entry as needed
        '''
        if (not WeightEntry.objects.filter(user=self.user).exists()
            or (datetime.date.today()
                - WeightEntry.objects.filter(user=self.user).latest().date
                > datetime.timedelta(days=3))):
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
        '''
        Returns the object that has owner information
        '''
        return self


@python_2_unicode_compatible
class UserCache(models.Model):
    '''
    A table used to cache expensive queries or similar
    '''

    user = models.OneToOneField(User, editable=False)
    '''
    The user
    '''

    last_activity = models.DateField(null=True)
    '''
    The user's last activity.

    Values for this entry are saved by signals as calculated by the
    get_user_last_activity helper function.
    '''

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"Cache for user {0}".format(self.user)


@python_2_unicode_compatible
class DaysOfWeek(models.Model):
    '''
    Model for the days of the week

    This model is needed so that 'Day' can have multiple days of the week selected
    '''

    day_of_week = models.CharField(max_length=9,
                                   verbose_name=_('Day of the week'))

    class Meta:
        '''
        Order by day-ID, this is needed for some DBs
        '''
        ordering = ["pk", ]

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return self.day_of_week


@python_2_unicode_compatible
class License(models.Model):
    '''
    License for an item (exercise, ingredient, etc.)
    '''

    full_name = models.CharField(max_length=60,
                                 verbose_name=_('Full name'),
                                 help_text=_('If a license has been localized, e.g. the Creative '
                                             'Commons licenses for the different countries, add '
                                             'them as separate entries here.'))
    '''Full name'''

    short_name = models.CharField(max_length=15,
                                  verbose_name=_('Short name, e.g. CC-BY-SA 3'))
    '''Short name, e.g. CC-BY-SA 3'''

    url = models.URLField(verbose_name=_('Link'),
                          help_text=_('Link to license text or other information'),
                          blank=True,
                          null=True)
    '''URL to full license text or other information'''

    class Meta:
        '''
        Set Meta options
        '''
        ordering = ["full_name", ]

    #
    # Django methods
    #
    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0} ({1})".format(self.full_name, self.short_name)

    #
    # Own methods
    #
    def get_owner_object(self):
        '''
        License has no owner information
        '''
        return None


@python_2_unicode_compatible
class RepetitionUnit(models.Model):
    '''
    Setting unit, used in combination with an amount such as '10 reps', '5 km'
    '''
    class Meta:
        '''
        Set Meta options
        '''
        ordering = ["name", ]

    name = models.CharField(max_length=100,
                            verbose_name=_('Name'))

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name

    #
    # Own methods
    #
    def get_owner_object(self):
        '''
        Unit has no owner information
        '''
        return None

    @property
    def is_repetition(self):
        '''
        Checks that the repetition unit is a repetition proper

        This is done basically to not litter the code with magic IDs
        '''
        return self.id == 1


@python_2_unicode_compatible
class WeightUnit(models.Model):
    '''
    Weight unit, used in combination with an amount such as '10 kg', '5 plates'
    '''
    class Meta:
        '''
        Set Meta options
        '''
        ordering = ["name", ]

    name = models.CharField(max_length=100,
                            verbose_name=_('Name'))

    def __str__(self):
        '''
        Return a more human-readable representation
        '''
        return self.name

    #
    # Own methods
    #
    def get_owner_object(self):
        '''
        Unit has no owner information
        '''
        return None

    @property
    def is_weight(self):
        '''
        Checks that the unit is a weight proper

        This is done basically to not litter the code with magic IDs
        '''
        return self.id in (1, 2)
