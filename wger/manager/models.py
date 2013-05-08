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

import datetime
import logging
import json

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.core.urlresolvers import reverse
from django.core.exceptions import ObjectDoesNotExist

from wger.exercises.models import Exercise

from wger.utils.helpers import DecimalJsonEncoder

logger = logging.getLogger('workout_manager.custom')


class Workout(models.Model):
    '''
    Model for a training schedule
    '''

    # Metaclass to set some other properties
    class Meta:
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
        return reverse('wger.manager.views.workout.view', kwargs={'id': self.id})

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"{0}".format(self.comment)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self


class ScheduleManager(models.Manager):
    '''
    Custom manager for workout schedules
    '''

    def get_current_workout(self, user):
        '''
        Finds the currently active workout for the user, by checking the schedules
        and the workouts
        '''

        # Try first to find an active schedule that has steps
        try:
            schedule = Schedule.objects.filter(user=user).get(is_active=True)
            if schedule.schedulestep_set.count():
                active_workout = schedule.get_current_scheduled_workout().workout

                # The schedule might exist and have steps, but if it's too far in
                # the past and is not a loop, we won't use it. Doing it like this
                # is kind of wrong, but lets us continue to the correct place
                if not active_workout:
                    raise ObjectDoesNotExist
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

    start_date = models.DateField(verbose_name=_('Start date'),
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

    duration = models.IntegerField(max_length=1,
                                   verbose_name=_('Duration'),
                                   help_text=_('The duration in weeks'),
                                   default=4)
    '''The duration in weeks'''

    order = models.IntegerField(verbose_name=_('Order'),
                                max_length=1,
                                default=1,
                                editable=False)

    comment = models.CharField(verbose_name=_('Comment'),
                               max_length=100,
                               help_text=_("A short comment or description"),
                               blank=True)
    '''Short comment about the step'''

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
                                 verbose_name=_('Training'),
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
    order = models.IntegerField(max_length=1,
                                blank=True,
                                null=True,
                                verbose_name=_('Order'),
                                editable=False)
    sets = models.IntegerField(validators=[MaxValueValidator(MAX_SETS)],
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


class Setting(models.Model):
    '''
    Settings for an exercise (weight, reps, etc.)
    '''

    set = models.ForeignKey(Set, verbose_name=_('Sets'), editable=False)
    exercise = models.ForeignKey(Exercise, verbose_name=_('Exercises'), editable=False)
    reps = models.IntegerField(validators=[MaxValueValidator(40)], verbose_name=_('Repetitions'))
    order = models.IntegerField(blank=True, verbose_name=_('Order'), editable=False)
    comment = models.CharField(max_length=100, blank=True, verbose_name=_('Comment'))

    # Metaclass to set some other properties
    class Meta:
        ordering = ["order", "id"]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"settings for exercise {0} in set {1}".format(self.exercise.id, self.set.id)

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

    reps = models.IntegerField(verbose_name=_('Repetitions'))
    weight = models.DecimalField(decimal_places=2,
                                 max_digits=5,
                                 verbose_name=_('Weight'))
    date = models.DateField(verbose_name=_('Date'))

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
                                                    'workout view'))

    # Also show ingredients in english while composing a nutritional plan
    # (obviously this is only meaningful if the user has a language other than english)
    show_english_ingredients = models.BooleanField(
        verbose_name=_('Also use ingredients in English'),
        help_text=_('''Check to also show ingredients in English while creating
a nutritional plan. These ingredients are extracted from a list provided
by the US Department of Agriculture. It is extremely complete, with around
7000 entries, but can be somewhat overwhelming and make the search difficult.'''))

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return u"Profile for user {0}".format(self.user)


# Every new user gets a profile
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
