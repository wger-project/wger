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

import datetime
import logging
import json
import decimal

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist
from django.core.exceptions import ValidationError
from django.core.cache import cache
from django.core.validators import MinValueValidator

from wger.exercises.models import Exercise
from wger.exercises.models import Language

from wger.utils.helpers import DecimalJsonEncoder
from wger.utils.helpers import disable_for_loaddata
from wger.utils.cache import delete_template_fragment_cache
from wger.utils.cache import cache_mapper
from wger.weight.models import WeightEntry
from wger.utils.fields import Html5DateField
from wger.utils.fields import Html5DecimalField
from wger.utils.fields import Html5IntegerField

logger = logging.getLogger('wger.custom')


#
# Helper functions
#
def reset_workout_muscle_bg_cache(workout_id):
    cache.delete(cache_mapper.get_workout_muscle_bg(workout_id))


def reset_day_template_cache(day_id):
    delete_template_fragment_cache('day-view', day_id)


#
# Classes
#
class Workout(models.Model):
    '''
    Model for a training schedule
    '''

    class Meta:
        '''
        Meta class to set some other properties
        '''
        ordering = ["-creation_date", ]

    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    comment = models.CharField(verbose_name=_('Description'),
                               max_length=100,
                               blank=True,
                               help_text=_("A short description or goal of the workout. For "
                                           "example 'Focus on back' or 'Week 1 of program xy'."))
    user = models.ForeignKey(User, verbose_name=_('User'))

    def get_absolute_url(self):
        '''
        Returns the canonical URL to view a workout
        '''
        return reverse('workout-view', kwargs={'id': self.id})

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        if self.comment:
            return u"{0}".format(self.comment)
        else:
            return u"{0} ({1})".format(_('Workout'), self.creation_date)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self

    @property
    def canonical_representation(self):
        '''
        Returns a canonical representation of the workout
        '''
        canonical_repr = []
        for day in self.day_set.select_related():
            tmp_days_of_week = []
            for day_of_week in day.day.select_related():
                tmp_days_of_week.append(day_of_week)

            canonical_repr.append({'obj': day,
                                   'days_of_week': {
                                       'text': u', '.join([unicode(_(i.day_of_week))
                                                           for i in tmp_days_of_week]),
                                       'day_list': tmp_days_of_week},
                                   'set_list': day.canonical_representation})
        return canonical_repr


class ScheduleManager(models.Manager):
    '''
    Custom manager for workout schedules
    '''

    def get_current_workout(self, user):
        '''
        Finds the currently active workout for the user, by checking the schedules
        and the workouts
        :rtype : list
        '''

        # Try first to find an active schedule that has steps
        try:
            schedule = Schedule.objects.filter(user=user).get(is_active=True)
            if schedule.schedulestep_set.count():
                # The schedule might exist and have steps, but if it's too far in
                # the past and is not a loop, we won't use it. Doing it like this
                # is kind of wrong, but lets us continue to the correct place
                if not schedule.get_current_scheduled_workout():
                    raise ObjectDoesNotExist

                active_workout = schedule.get_current_scheduled_workout().workout
            else:
                # same as above
                raise ObjectDoesNotExist

        # there are no active schedules, just return the last workout
        except ObjectDoesNotExist:

            schedule = False
            try:
                active_workout = Workout.objects.filter(user=user).latest('creation_date')

            # no luck, there aren't even workouts for the user
            except ObjectDoesNotExist:
                active_workout = False

        return (active_workout, schedule)


class Schedule(models.Model):
    '''
    Model for a workout schedule.

    A schedule is a collection of workous that are done for a certain time.
    E.g. workouts A, B, C, A, B, C, and so on.
    '''

    objects = ScheduleManager()
    '''Custom manager'''

    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False)
    '''
    The user this schedule belongs to. This could be accessed through a step
    that points to a workout, that points to a user, but this is more straight
    forward and performant
    '''

    name = models.CharField(verbose_name=_('Name'),
                            max_length=100,
                            help_text=_("Name or short description of the schedule. "
                                        "For example 'Program XYZ'."))
    '''Name or short description of the schedule.'''

    start_date = Html5DateField(verbose_name=_('Start date'),
                                default=datetime.date.today)
    '''The start date of this schedule'''

    is_active = models.BooleanField(verbose_name=_('Schedule active'),
                                    default=True,
                                    help_text=_("Tick the box if you want to mark this schedule "
                                                "as your active one (will be shown e.g. on your "
                                                "dashboard). All other schedules will then be "
                                                "marked as inactive"))
    '''A flag indicating whether the schedule is active (needed for dashboard)'''

    is_loop = models.BooleanField(verbose_name=_('Is loop'),
                                  default=False,
                                  help_text=_("Tick the box if you want to repeat the schedules "
                                              "in a loop (i.e. A, B, C, A, B, C, and so on)"))
    '''A flag indicating whether the schedule should act as a loop'''

    def get_absolute_url(self):
        return reverse('schedule-view', kwargs={'pk': self.id})

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self

    def save(self, *args, **kwargs):
        '''
        Only one schedule can be marked as active at a time
        '''
        if self.is_active:
            Schedule.objects.filter(user=self.user).update(is_active=False)
            self.is_active = True

        super(Schedule, self).save(*args, **kwargs)

    def get_current_scheduled_workout(self):
        '''
        Returns the currently active schedule step for a user
        '''
        steps = self.schedulestep_set.all()
        start_date = self.start_date
        found = False
        if not steps:
            return False
        while not found:
            for step in steps:
                current_limit = start_date + datetime.timedelta(weeks=step.duration)
                if current_limit >= datetime.date.today():
                    found = True
                    return step
                start_date = current_limit

            # If it's not a loop, there's no workout that matches, return
            if not self.is_loop:
                return False

    def get_end_date(self):
        '''
        Calculates the date when the schedule is over or None is the schedule
        is a loop.
        '''
        if self.is_loop:
            return None

        end_date = self.start_date
        for step in self.schedulestep_set.all():
            end_date = end_date + datetime.timedelta(weeks=step.duration)
        return end_date


class ScheduleStep(models.Model):
    '''
    Model for a step in a workout schedule.

    A step is basically a workout a with a bit of metadata (next and previous
    steps, duration, etc.)
    '''

    class Meta:
        '''
        Set default ordering
        '''
        ordering = ["order", ]

    schedule = models.ForeignKey(Schedule,
                                 verbose_name=_('schedule'),
                                 editable=False)
    '''The schedule is step belongs to'''

    workout = models.ForeignKey(Workout)
    '''The workout this step manages'''

    duration = Html5IntegerField(max_length=1,
                                 verbose_name=_('Duration'),
                                 help_text=_('The duration in weeks'),
                                 default=4)
    '''The duration in weeks'''

    order = models.IntegerField(verbose_name=_('Order'),
                                max_length=1,
                                default=1,
                                editable=False)

    #comment = models.CharField(verbose_name=_('Comment'),
    #                           max_length=100,
    #                           help_text=_("A short comment or description"),
    #                           blank=True)
    #'''Short comment about the step'''

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self.workout

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"ID: {0}".format(self.id)


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


class Day(models.Model):
    '''
    Model for a training day
    '''

    training = models.ForeignKey(Workout,
                                 verbose_name=_('Workout'),
                                 editable=False)
    description = models.CharField(max_length=100,
                                   verbose_name=_('Description'),
                                   help_text=_('Ususally a description about what parts are '
                                               'trained, like "Arms" or "Pull Day"'))
    day = models.ManyToManyField(DaysOfWeek,
                                 verbose_name=_('Day'))

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0} for TP {1}".format(self.description, unicode(self.training))

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self.training

    @property
    def get_first_day_id(self):
        '''
        Return the PK of the first day of the week, this is used in the template
        to order the days in the template
        '''
        return self.day.all()[0].pk

    def save(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        reset_day_template_cache(self.pk)
        super(Day, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        reset_day_template_cache(self.pk)
        super(Day, self).delete(*args, **kwargs)

    @property
    def canonical_representation(self):
        '''
        Returns a canonical representation of the day
        '''
        canonical_repr = []

        for set_obj in self.set_set.select_related():
            exercise_tmp = []
            for exercise in set_obj.exercises.select_related():
                setting_tmp = []
                for setting in Setting.objects.filter(set=set_obj,
                                                      exercise=exercise).order_by('order'):
                    setting_tmp.append(setting)

                if len(setting_tmp) > 1:
                    tmp_reps_text = []
                    tmp_reps = []
                    for i in setting_tmp:
                        reps = str(i.reps) if i.reps != 99 else '∞'
                        tmp_reps_text.append(reps)
                        tmp_reps.append(i.reps)

                    setting_text = ' – '.join(tmp_reps_text)
                    setting_list = tmp_reps
                else:
                    reps = setting_tmp[0].reps if setting_tmp[0].reps != 99 else '∞'
                    setting_text = u'{0} × {1}'.format(set_obj.sets, reps)
                    setting_list = [reps] * set_obj.sets
                exercise_tmp.append({'obj': exercise,
                                     'setting_obj_list': setting_tmp,
                                     'setting_list': setting_list,
                                     'setting_text': setting_text})

            if len(exercise_tmp) > 1:
                is_superset = True
            else:
                is_superset = False
            canonical_repr.append({'obj': set_obj,
                                   'exercise_list': exercise_tmp,
                                   'is_superset': is_superset})

        return canonical_repr


class Set(models.Model):
    '''
    Model for a set of exercises
    '''
    DEFAULT_SETS = 4
    MAX_SETS = 7

    exerciseday = models.ForeignKey(Day,
                                    verbose_name=_('Exercise day'),
                                    editable=False)
    exercises = models.ManyToManyField(Exercise, verbose_name=_('Exercises'))
    order = Html5IntegerField(max_length=1,
                              blank=True,
                              null=True,
                              verbose_name=_('Order'),
                              editable=False)
    sets = Html5IntegerField(validators=[MaxValueValidator(MAX_SETS)],
                             verbose_name=_('Number of sets'),
                             default=DEFAULT_SETS)

    # Metaclass to set some other properties
    class Meta:
        ordering = ["order", ]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"Set-ID {0}".format(self.id)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self.exerciseday.training

    def save(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        reset_workout_muscle_bg_cache(self.exerciseday.training_id)
        reset_day_template_cache(self.exerciseday_id)
        super(Set, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        reset_workout_muscle_bg_cache(self.exerciseday.training_id)
        reset_day_template_cache(self.exerciseday_id)
        super(Set, self).delete(*args, **kwargs)


class Setting(models.Model):
    '''
    Settings for an exercise (weight, reps, etc.)
    '''

    set = models.ForeignKey(Set, verbose_name=_('Sets'), editable=False)
    exercise = models.ForeignKey(Exercise, verbose_name=_('Exercises'), editable=False)
    reps = Html5IntegerField(validators=[MaxValueValidator(100)], verbose_name=_('Repetitions'))
    order = Html5IntegerField(blank=True, verbose_name=_('Order'), editable=False)
    comment = models.CharField(max_length=100, blank=True, verbose_name=_('Comment'))

    # Metaclass to set some other properties
    class Meta:
        ordering = ["order", "id"]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"settings for exercise {0} in set {1}".format(self.exercise.id, self.set.id)

    def save(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        reset_day_template_cache(self.set.exerciseday_id)
        super(Setting, self).save(*args, **kwargs)

    def delete(self, *args, **kwargs):
        '''
        Reset all cached infos
        '''

        reset_day_template_cache(self.set.exerciseday_id)
        super(Setting, self).delete(*args, **kwargs)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self.set.exerciseday.training


class WorkoutLog(models.Model):
    '''
    A log entry for an exercise
    '''

    user = models.ForeignKey(User,
                             verbose_name=_('User'),
                             editable=False)
    exercise = models.ForeignKey(Exercise, verbose_name=_('Exercise'))
    workout = models.ForeignKey(Workout,
                                verbose_name=_('Workout'),
                                editable=False)

    reps = Html5IntegerField(verbose_name=_('Repetitions'))
    weight = Html5DecimalField(decimal_places=2,
                               max_digits=5,
                               verbose_name=_('Weight'))
    date = Html5DateField(verbose_name=_('Date'))

    # Metaclass to set some other properties
    class Meta:
        ordering = ["date", "reps"]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"Log entry: {0} - {1} kg on {2}".format(self.reps,
                                                        self.weight,
                                                        self.date)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self

    def process_log_entries(self, logs):
        '''
        Processes and regroups a list of log entries so they can be rendered
        and passed to the D3 library to render a chart
        '''

        reps = []
        entry_log = SortedDict()
        chart_data = []
        max_weight = {}

        # Group by date
        for entry in logs:
            if entry.reps not in reps:
                reps.append(entry.reps)

            if not entry_log.get(entry.date):
                entry_log[entry.date] = []
            entry_log[entry.date].append(entry)

            # Find the maximum weight per date per repetition.
            # If on a day there are several entries with the same number of
            # repetitions, but different weights, only the entry with the
            # higher weight is shown in the chart
            if not max_weight.get(entry.date):
                max_weight[entry.date] = {entry.reps: entry.weight}

            if not max_weight[entry.date].get(entry.reps):
                max_weight[entry.date][entry.reps] = entry.weight

            if entry.weight > max_weight[entry.date][entry.reps]:
                max_weight[entry.date][entry.reps] = entry.weight

        # Group by repetitions
        for entry in logs:
            temp = {'date': '%s' % entry.date,
                    'id': 'workout-log-%s' % entry.id}

            for rep in reps:
                if entry.reps == rep:

                    # Only add if entry is the maximum for the day
                    if entry.weight == max_weight[entry.date][entry.reps]:
                        temp[rep] = entry.weight
                else:
                    temp[rep] = 0
            chart_data.append(temp)

        return (entry_log, json.dumps(chart_data, cls=DecimalJsonEncoder))


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
                                         default=14)
    workout_duration = Html5IntegerField(verbose_name=_('Default duration of workouts'),
                                         help_text=_('Default duration in weeks of workouts not '
                                                     'in a schedule. Used for email workout '
                                                     'reminders.'),
                                         default=12)
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

    #
    # User statistics
    #
    age = Html5IntegerField(max_length=2,
                            verbose_name=_('Age'),
                            blank=False,
                            null=True)
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
                                    null=True)
    '''The average hours of sleep per day'''

    work_hours = Html5IntegerField(verbose_name=_('Work'),
                                   help_text=_('Average hours per day'),
                                   default=8,
                                   blank=False,
                                   null=True)
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
                                    null=True)
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
                                       null=True)
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
                                 null=True)
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
        except TypeError:
        # Any of the entries is missing
            rate = 0

        return decimal.Decimal(str(rate)).quantize(decimal.Decimal('.01'))

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
        return decimal.Decimal(str(total)).quantize(decimal.Decimal('.01'))

    def user_bodyweight(self, weight):
        '''
        Create a new weight entry as needed
        '''

        if (not WeightEntry.objects.filter(user=self.user).exists()
            or (datetime.date.today()
                - WeightEntry.objects.filter(user=self.user).latest().creation_date
                > datetime.timedelta(1))):
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


# Every new user gets a profile
@disable_for_loaddata
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)


post_save.connect(create_user_profile, sender=User)
