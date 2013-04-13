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

import logging
import json

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext_lazy as _
from django.utils.datastructures import SortedDict
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator
from django.core.urlresolvers import reverse


from wger.exercises.models import Exercise

from wger.utils.helpers import DecimalJsonEncoder

logger = logging.getLogger('workout_manager.custom')


class TrainingSchedule(models.Model):
    '''
    Model for a training schedule
    '''

    # Metaclass to set some other properties
    class Meta:
        ordering = ["-creation_date", ]

    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    comment = models.TextField(verbose_name=_('Description'),
                               max_length=100,
                               blank=True,
                               help_text=_('''A short description or goal of the workout.
For example 'Focus on back' or 'Week 1 of program xy'.'''))
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
        return str(self.creation_date)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self


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

    training = models.ForeignKey(TrainingSchedule, verbose_name=_('Training'))
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
        return "%s for TP %s" % (self.description, unicode(self.training))

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

    exerciseday = models.ForeignKey(Day, verbose_name=_('Exercise day'))
    exercises = models.ManyToManyField(Exercise, verbose_name=_('Exercises'))
    order = models.IntegerField(max_length=1,
                                blank=True,
                                null=True,
                                verbose_name=_('Order'))
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
        return "Set-ID %s" % (self.id)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self.exerciseday.training


class Setting(models.Model):
    '''
    Settings for an exercise (weight, reps, etc.)
    '''

    set = models.ForeignKey(Set, verbose_name=_('Sets'))
    exercise = models.ForeignKey(Exercise, verbose_name=_('Exercises'))
    reps = models.IntegerField(validators=[MaxValueValidator(40)], verbose_name=_('Repetitions'))
    order = models.IntegerField(blank=True, verbose_name=_('Order'))
    comment = models.CharField(max_length=100, blank=True, verbose_name=_('Comment'))

    # Metaclass to set some other properties
    class Meta:
        ordering = ["order", "id"]

    def __unicode__(self):
        '''
        Return a more human-readable representation
        '''
        return "settings for exercise %s in set %s" % (self.exercise.id, self.set.id)

    def get_owner_object(self):
        '''
        Returns the object that has owner information
        '''
        return self.set.exerciseday.training


class WorkoutLog(models.Model):
    '''
    A log entry for an exercise
    '''

    user = models.ForeignKey(User, verbose_name=_('User'))
    exercise = models.ForeignKey(Exercise, verbose_name=_('Exercise'))
    workout = models.ForeignKey(TrainingSchedule, verbose_name=_('Workout'))

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
        return "Log entry: %s - %s kg on %s" % (self.reps,
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
    user = models.OneToOneField(User)

    # Flag to mark a temporary user (demo account)
    is_temporary = models.BooleanField(default=False)

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
        return "Profile for user %s" % (self.user)


# Every new user gets a profile
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
