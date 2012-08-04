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
import calendar

class TrainingSchedule(models.Model):
    """Model for a training schedule
    """
    creation_date = models.DateField('creation date', auto_now_add=True)
    comment = models.CharField(max_length=100)
    
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

    training = models.ForeignKey(TrainingSchedule)
    description = models.CharField(max_length=100)
    day = models.IntegerField(max_length=1, choices=CHOICES)
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "%s for TP %s" % (self.description, unicode(self.training))

class ExerciseCategory(models.Model):
    """Model for an exercise category
    """
    name = models.CharField(max_length=100)
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.name
        
class Exercise(models.Model):
    """Model for an exercise
    """
    category = models.ForeignKey(ExerciseCategory)
    
    name = models.CharField(max_length=200)
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.name

class Settings(models.Model):
    """Settings for an exercise (weight, reps, etc.)
    """
    
    sets = models.ForeignKey('Set')
    exercises = models.ForeignKey(Exercise)
    weight = models.IntegerField()
    reps = models.IntegerField()
    comment = models.CharField(max_length=100)
    
    
    #def __unicode__(self):
        #"""Return a more human-readable representation
        #"""
        #return "settings for %s for TP %s" % (self.description, unicode(self.training))

class Set(models.Model):
    """Model for a set of exercises
    """

    excersise_day = models.ForeignKey(Day)
    exercises = models.ManyToManyField(Exercise, through=Settings)
    order = models.IntegerField(max_length=1)
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "Set %d for %s" % (self.order, unicode(self.excersise_day))

        




class ExerciseComment(models.Model):
    """Model for an exercise comment
    """
    exercise = models.ForeignKey(Exercise)
    comment = models.CharField(max_length=200)
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.comment


