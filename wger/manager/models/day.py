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

# Standard Library
import datetime
from typing import List

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.manager.dataclasses import SlotData


class DayType(models.TextChoices):
    CUSTOM = 'custom'
    ENOM = 'enom'
    AMRAP = 'amrap'
    HIIT = 'hiit'
    TABATA = 'tabata'
    EDT = 'edt'
    RFT = 'rft'
    AFAP = 'afap'


class Day(models.Model):
    """
    Model for a training day
    """

    class Meta:
        ordering = [
            'order',
        ]

    routine = models.ForeignKey(
        'Routine',
        verbose_name=_('Routine'),
        on_delete=models.CASCADE,
        related_name='days',
    )

    order = models.PositiveIntegerField(
        default=1,
        null=False,
        verbose_name=_('Order'),
        db_index=True,
    )

    type = models.CharField(
        choices=DayType.choices,
        max_length=10,
        default=DayType.CUSTOM,
        null=False,
    )

    name = models.CharField(
        max_length=20,
        verbose_name=_('Name'),
        blank=True,  # needed for rest days
    )

    description = models.CharField(
        max_length=1000,
        verbose_name=_('Description'),
        blank=True,
    )

    is_rest = models.BooleanField(
        default=False,
    )
    """
    Flag indicating that this day is a rest day.

    Rest days have no exercises
    """

    need_logs_to_advance = models.BooleanField(
        default=False,
    )
    """
    Needs logs to advance to the next day
    """

    config = models.JSONField(
        default=None,
        null=True,
    )
    """JSON configuration field for custom behaviour"""

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return self.description

    def save(self, *args, **kwargs):
        # Rest days have no exercises
        if self.pk and self.is_rest:
            for slot in self.slots.all():
                slot.delete()

        return super().save(*args, **kwargs)

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self.routine

    def can_proceed(self, date: datetime.date) -> bool:
        """
        Checks whether the user can proceed to the next day in the sequence

        This is possible if
        - the day doesn't require logs
        - the day requires logs, and they exist
        - the date is in the future (used e.g. for calendars where we assume we will proceed)
        """
        if (
            not self.need_logs_to_advance
            # or self.workoutsession_set.filter(date=date).exists()
            or date > datetime.date.today()
        ):
            return True

        return False

    def get_slots_gym_mode(self, iteration: int) -> List[SlotData]:
        """
        Return the sets for this day
        """
        slots = getattr(self, 'prefetched_slots', self.slots.all())

        return [SlotData(comment=s.comment, sets=s.set_data_gym(iteration)) for s in slots]

    def get_slots_display_mode(self, iteration: int) -> List[SlotData]:
        """
        Return the sets for this day.

        The difference to get_slots above is that here some data massaging happens
        so that we can better display the data in the template. Specially, we
        collect the sets for the same exercise in the same slot.

        This only happens for slots that have only one exercise.

        Instead of
        * Slot1 -> Exercise1, [Config1]
        * Slot2 -> Exercise1, [Config2]
        * Slot3 -> Exercise1, [Config3]

        We return
        * Slot1 -> Exercise1, [Config1, Config2, Config3]

        """
        out = []
        last_exercise_id = None
        current_slot = None

        slots = getattr(self, 'prefetched_slots', self.slots.all())

        for slot in slots:
            # for slot in self.slots.all():
            slot_data = SlotData(
                comment=slot.comment,
                sets=[s.data for s in slot.set_data(iteration)],
            )
            exercises = slot_data.exercises

            # slot is superset
            if len(exercises) > 1:
                out.append(slot_data)
                current_slot = None

            # empty slot
            elif not exercises:
                continue

            # one exercise
            else:
                exercise_id = exercises[0]
                if exercise_id != last_exercise_id:
                    current_slot = slot_data
                    out.append(slot_data)
                    last_exercise_id = exercise_id
                else:
                    current_slot.sets.extend(slot_data.sets)

        return out
