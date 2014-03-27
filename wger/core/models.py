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
from django.db.models.signals import post_save
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
from django.core.exceptions import ValidationError
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils.translation import ugettext_lazy as _

from wger.utils.helpers import disable_for_loaddata
from wger.utils.constants import TWOPLACES
from wger.utils.fields import Html5IntegerField

from wger.weight.models import WeightEntry


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
    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0} ({1})".format(self.full_name, self.short_name)

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view a language
        '''
        return reverse('config:language-view', kwargs={'pk': self.id})

    #
    # Own methods
    #
    def get_owner_object(self):
        '''
        Muscle has no owner information
        '''
        return False


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

    # This field is required.
    user = models.OneToOneField(User,
                                editable=False)

    # Flag to mark a temporary user (demo account)
    is_temporary = models.BooleanField(default=False,
                                       editable=False)

    #
    # User preferences
    #

    # Show exercise comments on workout view
    show_comments = models.BooleanField(verbose_name=_('Show exercise comments'),
                                        help_text=_('Check to show exercise comments on the '
                                                    'workout view'),
                                        default=True)

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

    workout_reminder = Html5IntegerField(verbose_name=_('Remind before expiration'),
                                         help_text=_('The number of days you want to be reminded '
                                                     'before a workout expires.'),
                                         default=14,
                                         validators=[MinValueValidator(1), MaxValueValidator(30)])
    workout_duration = Html5IntegerField(verbose_name=_('Default duration of workouts'),
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

    timer_pause = Html5IntegerField(verbose_name=_('Default duration of workout pauses'),
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
    age = Html5IntegerField(max_length=2,
                            verbose_name=_('Age'),
                            blank=False,
                            null=True,
                            validators=[MinValueValidator(10), MaxValueValidator(100)])
    '''The user's age'''

    height = Html5IntegerField(max_length=2,
                               verbose_name=_('Height (cm)'),
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

    sleep_hours = Html5IntegerField(verbose_name=_('Hours of sleep'),
                                    help_text=_('The average hours of sleep per day'),
                                    default=7,
                                    blank=False,
                                    null=True,
                                    validators=[MinValueValidator(4), MaxValueValidator(10)])
    '''The average hours of sleep per day'''

    work_hours = Html5IntegerField(verbose_name=_('Work'),
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

    sport_hours = Html5IntegerField(verbose_name=_('Sport'),
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

    freetime_hours = Html5IntegerField(verbose_name=_('Free time'),
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

    calories = Html5IntegerField(verbose_name=_('Total daily calories'),
                                 help_text=_('Total caloric intake, including e.g. any surplus'),
                                 default=2500,
                                 blank=False,
                                 null=True,
                                 validators=[MinValueValidator(1500), MaxValueValidator(5000)])
    '''Basic caloric intake based on physical activity'''

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

    def clean(self):
        '''
        Make sure the total amount of hours is 24
        '''
        if ((self.sleep_hours and self.freetime_hours and self.work_hours)
           and (self.sleep_hours + self.freetime_hours + self.work_hours) > 24):
                raise ValidationError(_('The sum of all hours has to be 24'))

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"Profile for user {0}".format(self.user)

    def calculate_bmi(self):
        '''
        Calculates the user's BMI

        Formula: weight/height^2
        - weight in kg
        - height in m
        '''
        return self.weight / (self.height / 100.0 * self.height / 100.0)

    def calculate_basal_metabolic_rate(self, formula=1):
        '''
        Calculates the basal metabolic rate.

        Currently only the Mifflin-St.Jeor formula is supported
        '''

        if self.gender == self.GENDER_MALE:
            factor = 5
        else:
            factor = -161

        try:
            rate = ((10 * self.weight)  # in kg
                    + (6.25 * self.height)  # in cm
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
                - WeightEntry.objects.filter(user=self.user).latest().creation_date
                > datetime.timedelta(days=3))):
            entry = WeightEntry()
            entry.weight = weight
            entry.user = self.user
            entry.creation_date = datetime.date.today()
            entry.save()

        # Update the last entry
        else:
            entry = WeightEntry.objects.filter(user=self.user).latest()
            entry.weight = weight
            entry.save()
        return entry


# Every new user gets a profile
@disable_for_loaddata
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)


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

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return self.day_of_week


class License(models.Model):
    '''
    License for an item (exercise, ingredient, etc.)
    '''

    full_name = models.CharField(max_length=60,
                                 verbose_name=_('Full name'))
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
    def __unicode__(self):
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
