# Standard Library
from typing import List

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.manager.dataclasses import SetExerciseData
from wger.manager.models import DayNg


class Slot(models.Model):
    """
    Model for a set of exercises
    """

    DEFAULT_SETS = 4
    MAX_SETS = 10

    day = models.ForeignKey(
        DayNg,
        verbose_name=_('Exercise day'),
        on_delete=models.CASCADE,
    )

    order = models.IntegerField(
        default=1,
        null=False,
        verbose_name=_('Order'),
    )

    comment = models.CharField(
        max_length=200,
        verbose_name=_('Comment'),
        blank=True,
    )

    is_dropset = models.BooleanField(
        default=False,
    )

    # Metaclass to set some other properties
    class Meta:
        ordering = [
            'order',
        ]

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Set {self.id}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.day.routine

    def set_data(self, iteration: int) -> List[SetExerciseData]:
        """Calculates the set data for a specific iteration"""

        return [
            SetExerciseData(data=s.get_config(iteration), config=s)
            for s in self.slotconfig_set.all()
        ]
