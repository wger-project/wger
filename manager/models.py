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
from django.db.models.signals import post_save
from django.utils.translation import ugettext as _
from django.contrib.auth.models import User


from exercises.models import Exercise

import calendar

class TrainingSchedule(models.Model):
    """Model for a training schedule
    """
    creation_date = models.DateField(_('Creation date'), auto_now_add=True)
    comment = models.CharField(_('Comment'), max_length=100, blank=True)
    user = models.ForeignKey(User, verbose_name = _('User'))

    
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

    training = models.ForeignKey(TrainingSchedule, verbose_name = _('Training'))
    description = models.CharField(max_length=100,
                                   verbose_name = _('Description'),
                                   help_text=_('Ususally a description about what parts are trained, like "Arms" or "Pull Day"'))
    day = models.IntegerField(max_length=1, choices=CHOICES, verbose_name = _('Day'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "%s for TP %s" % (self.description, unicode(self.training))



class Set(models.Model):
    """Model for a set of exercises
    """

    exerciseday = models.ForeignKey(Day, verbose_name = _('Exercise day'))
    exercises = models.ManyToManyField(Exercise, verbose_name = _('Exercises'))
    order = models.IntegerField(max_length=1, blank=True, null=True, verbose_name = _('Order')) #TODO: null=True???
    sets = models.IntegerField(verbose_name = _('Sets'))
    
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
    reps = models.IntegerField(verbose_name = _('Repetitions'))
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
    show_comments = models.BooleanField()

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)
