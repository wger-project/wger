# Standard Library
from typing import List

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.manager.dataclasses import (
    SetConfigData,
    SetExerciseData,
)
from wger.manager.models import Day


class Slot(models.Model):
    """
    Model for a set of exercises
    """

    DEFAULT_SETS = 4
    MAX_SETS = 10

    day = models.ForeignKey(
        Day,
        verbose_name=_('Exercise day'),
        on_delete=models.CASCADE,
        related_name='slots',
    )

    order = models.PositiveIntegerField(
        default=1,
        null=False,
        verbose_name=_('Order'),
    )

    comment = models.CharField(
        max_length=200,
        verbose_name=_('Comment'),
        blank=True,
    )

    config = models.JSONField(
        default=None,
        null=True,
    )
    """JSON configuration field for custom behaviour"""

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

    @property
    def is_superset(self) -> bool:
        """
        Checks whether this slot is a superset or not
        """
        return self.entries.count() > 1

    def set_data(self, iteration: int) -> List[SetExerciseData]:
        """Calculates the set data for a specific iteration"""

        return [SetExerciseData(data=s.get_config(iteration), config=s) for s in self.entries.all()]

    def get_sets(self, iteration: int) -> list[SetConfigData]:
        """
        Calculates the sets as they would be performed in the gym

        Note that this is only different from the list of sets in supersets, since
        they will be "interleaved". E.g.:
        - Exercise 1, 4 Sets
        - Exercise 2, 3 Sets
        - Exercise 3, 2 Sets
        (the other weight, reps, etc. settings are not important here)

        Would result in:
        - Exercise 1
        - Exercise 2
        - Exercise 3
        - Exercise 1
        - Exercise 2
        - Exercise 3
        - Exercise 1
        - Exercise 2
        - Exercise 1
        """
        set_data = self.set_data(iteration)

        # If this is not a superset, just return the data
        if len(set_data) == 1:
            return [
                set_data[0].data,
            ]

        result = []
        sets = [slot.data.sets for slot in set_data]

        while any(repeat > 0 for repeat in sets):
            for i, slot in enumerate(set_data):
                if sets[i] > 0:
                    # Override the number of sets. After all, each of the individual
                    # sets here is only done once
                    slot.data.sets = 1

                    result.append(slot.data)
                    sets[i] -= 1
        return result

    def get_exercises(self) -> List[int]:
        """
        Returns the list of distinct exercises in the configs
        """
        return [slot.exercise.id for slot in self.entries.all()]
