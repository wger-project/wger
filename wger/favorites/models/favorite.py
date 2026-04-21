#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#  Copyright (C) 2013 - 2021 wger Team
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

# Django
from django.conf import settings
from django.db import models

# wger
from wger.exercises.models import Exercise


class Favorite(models.Model):
    """
    Model representing a favorite exercise for a user.
    This is a many-to-many relationship between User and Exercise.
    """

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='User',
    )
    """The user who favorited the exercise"""

    exercise = models.ForeignKey(
        Exercise,
        on_delete=models.CASCADE,
        related_name='favorited_by',
        verbose_name='Exercise',
    )
    """The exercise that was favorited"""

    created = models.DateTimeField(
        auto_now_add=True,
        editable=False,
        verbose_name='Created',
    )
    """When the exercise was favorited"""

    class Meta:
        unique_together = ['user', 'exercise']
        ordering = ['-created']
        verbose_name = 'Favorite'
        verbose_name_plural = 'Favorites'

    def __str__(self):
        return f'{self.user} - {self.exercise}'

    @classmethod
    def toggle_favorite(cls, user, exercise):
        """
        Toggle the favorite status for an exercise.
        If already favorited, remove it. If not, add it.
        
        Returns a tuple (is_favorited, was_created) where:
        - is_favorited: True if the exercise is now favorited
        - was_created: True if a new favorite was created
        """
        favorite, created = cls.objects.get_or_create(user=user, exercise=exercise)
        
        if not created:
            favorite.delete()
            return False, False
        
        return True, True

    @classmethod
    def is_favorited(cls, user, exercise):
        """
        Check if an exercise is favorited by a user.
        """
        if not user.is_authenticated:
            return False
        return cls.objects.filter(user=user, exercise=exercise).exists()

    @classmethod
    def get_user_favorites(cls, user):
        """
        Get all favorited exercises for a user.
        """
        if not user.is_authenticated:
            return cls.objects.none()
        return cls.objects.filter(user=user).select_related('exercise')
