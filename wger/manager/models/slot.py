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
        db_index=True,
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
        entries = getattr(self, 'prefetched_entries', self.entries.all())
        return len(entries) > 1

    def set_data(self, iteration: int) -> List[SetExerciseData]:
        """Calculates the set data for a specific iteration"""
        entries = getattr(self, 'prefetched_entries', self.entries.all())

        result = [SetExerciseData(data=e.get_config_data(iteration), config=e) for e in entries]

        return result

    def set_data_gym(self, iteration: int) -> list[SetConfigData]:
        """
        Calculates the sets as they would be performed in the gym

        * For supersets:
        The sets will be interleaved as well as possible, e.g.:
        - Exercise 1, 4 sets
        - Exercise 2, 3 sets
        - Exercise 3, 2 sets
        (the other weight, reps, etc. settings are not important here)

        Would result in:
        - Exercise 1, 1 set
        - Exercise 2, 1 set
        - Exercise 3, 1 set
        - Exercise 1, 1 set
        - Exercise 2, 1 set
        - Exercise 3, 1 set
        - Exercise 1, 1 set
        - Exercise 2, 1 set
        - Exercise 1, 1 set

        * For regular sets:
        The sets are just repeated, e.g.:
        - Exercise 1, 4 sets

        Would result in:
        - Exercise 1, 1 set
        - Exercise 1, 1 set
        - Exercise 1, 1 set
        - Exercise 1, 1 set
        """
        set_data = self.set_data(iteration)

        # If this is not a superset, adjust the sets and just return the data
        if len(set_data) == 1:
            data = set_data[0].data
            nr_sets = int(data.sets)
            data.sets = 1
            return [data] * nr_sets

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
