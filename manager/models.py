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

from django.db import models
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator

from exercises.models import Exercise

logger = logging.getLogger('workout_manager.custom')

# Days of the week
DAYS_OF_WEEK_CHOICES = [(1, _('Monday')),
                        (2, _('Tuesday')),
                        (3, _('Wednesday')),
                        (4, _('Thursday')),
                        (5, _('Friday')),
                        (6, _('Saturday')),
                        (7, _('Sunday'))]


class TrainingSchedule(models.Model):
    """Model for a training schedule
    """
    
    # Metaclass to set some other properties
    class Meta:
        ordering = ["-creation_date", ]
    
    
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    comment = models.TextField(verbose_name = _('Description'),
                               max_length=100,
                               blank=True,
                               help_text = _('''A short description or goal of the workout.
For example 'Focus on back' or 'Week 1 of program xy'.'''))
    user = models.ForeignKey(User, verbose_name = _('User'))

    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return str(self.creation_date)

class DaysOfWeek(models.Model):
    """Model for the days of the week
    
    This model is needed so that 'Day' can have multiple days of the week selected
    """

    day_of_week = models.CharField(max_length=9,
                                   verbose_name = _('Day of the week'))
    
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.day_of_week


class Day(models.Model):
    """Model for a training day
    """

    training = models.ForeignKey(TrainingSchedule, verbose_name = _('Training'))
    description = models.CharField(max_length=100,
                                   verbose_name = _('Description'),
                                   help_text=_('Ususally a description about what parts are trained, like "Arms" or "Pull Day"'))
    day = models.ManyToManyField(DaysOfWeek,
                                 verbose_name = _('Day'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "%s for TP %s" % (self.description, unicode(self.training))


class Set(models.Model):
    """Model for a set of exercises
    """

    exerciseday = models.ForeignKey(Day, verbose_name = _('Exercise day'))
    exercises = models.ManyToManyField(Exercise, verbose_name = _('Exercises'))
    order = models.IntegerField(max_length = 1, blank = True, verbose_name = _('Order'))
    sets = models.IntegerField(validators = [MaxValueValidator(6)], verbose_name = _('Sets'))
    
    # Metaclass to set some other properties
    class Meta:
        ordering = ["order", ]
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "Set %s for %s" % (self.order or '-/-', unicode(self.exerciseday))



class Setting(models.Model):
    """Settings for an exercise (weight, reps, etc.)
    """
    
    set = models.ForeignKey(Set, verbose_name = _('Sets'))
    exercise = models.ForeignKey(Exercise, verbose_name = _('Exercises'))
    reps = models.IntegerField(validators = [MaxValueValidator(40)], verbose_name = _('Repetitions'))
    order = models.IntegerField(blank = True, verbose_name = _('Repetitions'))
    comment = models.CharField(max_length=100, blank=True, verbose_name = _('Comment'))
    
    # Metaclass to set some other properties
    class Meta:
        ordering = ["order", "id"]
    
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "settings for exercise %s in set %s" % (self.exercise.id, self.set.id)


class UserProfile(models.Model):
    # This field is required.
    user = models.OneToOneField(User)

    #
    # User preferences
    #

    # Show exercise comments on workout view
    show_comments = models.BooleanField(verbose_name = _('Show exercise comments'),
                        help_text=_('Check to show exercise comments on the workout view'))
    
    # Also show ingredients in english while composing a nutritional plan
    # (obviously this is only meaningful if the user has a language other than english)
    show_english_ingredients = models.BooleanField(verbose_name = _('Also use ingredients in English'),
                        help_text=_('''Check to also show ingredients in English while creating
a nutritional plan. These ingredients are extracted from a list provided by the US Department
of Agriculture. It is extremely complete, with around 7000 entries, but can be somewhat
overwhelming and make the search difficult.'''))

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
