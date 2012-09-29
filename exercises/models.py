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

from django.db import models
from django.utils.translation import ugettext as _

class Language(models.Model):
    """Language of an item (exercise, workout, etc.)
    """
    
    #e.g. 'de'
    short_name = models.CharField(max_length = 2, verbose_name = _('Language short name'))
    
    #e.g. 'Deutsch'
    full_name  = models.CharField(max_length = 30, verbose_name = _('Language full name'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return "%s (%s)" % (self.full_name, self.short_name)


class Muscle(models.Model):
    """Muscle an exercise works out
    """
    
    # Name, in latin, e.g. "Pectoralis major"
    name = models.CharField(max_length = 50, verbose_name = _('Name'))
    
    # Whether to use the front or the back image for background
    is_front = models.BooleanField(default=1)
    
    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.name


class ExerciseCategory(models.Model):
    """Model for an exercise category
    """
    name = models.CharField(max_length=100, verbose_name = _('Name'),)
    language = models.ForeignKey(Language, verbose_name = _('Language'))
    
    # Metaclass to set some other properties
    class Meta:
        verbose_name_plural = _("Exercise Categories")
        ordering = ["name", ]
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.name



class Exercise(models.Model):
    """Model for an exercise
    """
    category = models.ForeignKey(ExerciseCategory, verbose_name = _('Category'))
    description = models.TextField(max_length = 2000,
                                   blank = True,
                                   verbose_name = _('Description'))
    name = models.CharField(max_length = 200, verbose_name = _('Name'))
    
    muscles = models.ManyToManyField(Muscle, verbose_name = _('Muscles'))
    
    # Metaclass to set some other properties
    class Meta:
        ordering = ["name", ]
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.name

class ExerciseComment(models.Model):
    """Model for an exercise comment
    """
    exercise = models.ForeignKey(Exercise, verbose_name = _('Exercise'))
    comment = models.CharField(max_length=200,
                               verbose_name = _('Comment'),
                               help_text=_('Some comment about how to correctly do this exercise'))
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.comment
