# This file is part of Workout Manager.
# 
# Foobar is free software: you can redistribute it and/or modify
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
from django.utils.translation import ugettext as _

import calendar

class TrainingSchedule(models.Model):
    """Model for a training schedule
    """
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    comment = models.CharField(_('Comment'), max_length=100, blank=True)

    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return str(self.creation_date)


# Mhh...
DAYS_OF_WEEK_CHOICES = []
cal = calendar.Calendar()
for i in cal.iterweekdays():
     DAYS_OF_WEEK_CHOICES.append((int(i), calendar.day_name[i]))

class Day(models.Model):
    """Model for a training day
    """
    CHOICES = DAYS_OF_WEEK_CHOICES

    training = models.ForeignKey(TrainingSchedule, verbose_name =_ ('Training'))
    description = models.CharField(max_length=100, verbose_name =_ ('Description'))
    day = models.IntegerField(max_length=1, choices=CHOICES, verbose_name =_ ('Day'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "%s for TP %s" % (self.description, unicode(self.training))



class ExerciseCategory(models.Model):
    """Model for an exercise category
    """
    name = models.CharField(_('Name'), max_length=100)
    
    class Meta:
        verbose_name_plural = _("Exercise Categories")
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.name



class Exercise(models.Model):
    """Model for an exercise
    """
    category = models.ForeignKey(ExerciseCategory, verbose_name =_ ('Category'))
    name = models.CharField(max_length=200, verbose_name =_ ('Name'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.name



class ExerciseComment(models.Model):
    """Model for an exercise comment
    """
    exercise = models.ForeignKey(Exercise, verbose_name =_ ('Exercise'))
    comment = models.CharField(max_length=200,
                               blank=True,
                               verbose_name =_ ('Comment'),
                               help_text=_('Some comment about how to correctly do this exercise'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.comment



class Set(models.Model):
    """Model for a set of exercises
    """

    exerciseday = models.ForeignKey(Day, verbose_name =_ ('Exercise day'))
    exercises = models.ManyToManyField(Exercise, verbose_name =_ ('Exercises'))
    order = models.IntegerField(max_length=1, blank=True, null=True, verbose_name =_ ('Order')) #TODO: null=True???
    sets = models.IntegerField(verbose_name =_ ('Sets'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "Set %s for %s" % (self.order or '-/-', unicode(self.exerciseday))



class Setting(models.Model):
    """Settings for an exercise (weight, reps, etc.)
    """
    
    reps = models.IntegerField(verbose_name =_ ('Repetitions'))
    sets = models.ForeignKey(Set, verbose_name =_ ('Sets'))
    exercises = models.ForeignKey(Exercise, verbose_name =_ ('Exercises'))
    #individual_exercises = models.ForeignKey(IndividualSetting, verbose_name =_ ('Individual Exercises'))
    #individual_exercises = models.ManyToManyField(IndividualSetting, verbose_name =_ ('Individual Exercises'))
    
    comment = models.CharField(max_length=100, blank=True, verbose_name =_ ('Comment'))
    
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "setings for %s" % (unicode(self.exercises),)

class IndividualSetting(models.Model):
    """Setting for an exercise on a set (weight, reps, etc.)
    """
    
    setting = models.ForeignKey(Setting, verbose_name = _('Setting'))
    weight = models.IntegerField(verbose_name = _('Weight'))
    reps = models.IntegerField(verbose_name = _('Repetitions'))
    comment = models.CharField(max_length=100, blank=True, verbose_name = _('Comment'))
    order = models.IntegerField(max_length=1, blank=True, verbose_name = _('Order'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "reps: %s" % (self.reps)