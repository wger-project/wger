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

class ExerciseComment(models.Model):
    """Model for an exercise comment
    """
    exercise = models.ForeignKey(Exercise)
    comment = models.CharField(max_length=200)
    
    def __unicode__(self):
        """Return a more human-readable representation
        """
        return self.comment


