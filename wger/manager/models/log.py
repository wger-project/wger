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
from django.contrib.auth.models import User
from django.core.exceptions import ValidationError
from django.db import models
from django.utils import timezone

# wger
from wger.core.models import (
    RepetitionUnit,
    WeightUnit,
)
from wger.exercises.models import Exercise
from wger.manager.consts import (
    REP_UNIT_REPETITIONS,
    WEIGHT_UNIT_KG,
)
from wger.manager.managers import WorkoutLogManager
from wger.manager.models.session import WorkoutSession
from wger.manager.validators import (
    NullMinValueValidator,
    validate_rir,
)
from wger.utils.uuid import uuid7


class WorkoutLog(models.Model):
    """
    A log entry for an exercise
    """

    objects = WorkoutLogManager()

    id = models.UUIDField(
        default=uuid7,
        null=False,
        primary_key=True,
    )

    date = models.DateTimeField(
        verbose_name='Date',
        default=timezone.now,
    )

    user = models.ForeignKey(
        User,
        verbose_name='User',
        editable=False,
        on_delete=models.CASCADE,
    )

    next_log = models.ForeignKey(
        'self',
        editable=True,
        on_delete=models.CASCADE,
        null=True,
        default=None,
    )
    """
    If this is a log entry for a dropset or similar, this field will contain the
    next log entry in the series
    """

    session = models.ForeignKey(
        'WorkoutSession',
        verbose_name='Session',
        on_delete=models.CASCADE,
        null=True,
        related_name='logs',
    )
    """
    The session this log belongs to.

    If none is given, one will be automatically created on save.
    """

    exercise = models.ForeignKey(
        Exercise,
        verbose_name='Exercise',
        on_delete=models.CASCADE,
    )

    routine = models.ForeignKey(
        'Routine',
        verbose_name='Workout',
        on_delete=models.CASCADE,
        null=True,
    )

    slot_entry = models.ForeignKey(
        'SlotEntry',
        on_delete=models.CASCADE,
        null=True,
    )

    iteration = models.PositiveIntegerField(
        null=True,
    )

    repetitions_unit = models.ForeignKey(
        RepetitionUnit,
        verbose_name='Repetitions unit',
        default=REP_UNIT_REPETITIONS,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    """
    The repetition unit of the log. This can be e.g. a repetition, a minute, etc.
    """

    repetitions = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[NullMinValueValidator(0)],
        blank=True,
        null=True,
    )
    """
    Logged amount of repetitions
    """

    repetitions_target = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='Repetitions target',
        validators=[NullMinValueValidator(0)],
        null=True,
        blank=True,
    )
    """
    Target amount of repetitions
    """

    weight_unit = models.ForeignKey(
        WeightUnit,
        verbose_name='Weight unit',
        default=WEIGHT_UNIT_KG,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
    )
    """
    The weight unit of the log. This can be e.g. kg, lb, km/h, etc.
    """

    weight = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        validators=[NullMinValueValidator(0)],
        blank=True,
        null=True,
    )
    """
    Logged amount of weight
    """

    weight_target = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        verbose_name='Weight target',
        validators=[NullMinValueValidator(0)],
        null=True,
        blank=True,
    )
    """
    Target amount of weight
    """

    rir = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[NullMinValueValidator(0), validate_rir],
        null=True,
        blank=True,
    )
    """
    Reps in Reserve, RiR. The amount of reps that could realistically still be
    done in the set.
    """

    rir_target = models.DecimalField(
        max_digits=2,
        decimal_places=1,
        validators=[NullMinValueValidator(0), validate_rir],
        null=True,
        blank=True,
    )
    """
    Target Reps in Reserve
    """

    rest = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    """
    Logged rest time
    """

    rest_target = models.PositiveIntegerField(
        blank=True,
        null=True,
    )
    """
    Target rest time
    """

    # Metaclass to set some other properties
    class Meta:
        ordering = ['date', 'repetitions', 'weight']

    def __str__(self):
        """
        Return a more human-readable representation
        """
        return f'Log entry: {self.repetitions} - {self.weight} kg on {self.date}'

    def get_owner_object(self):
        """
        Returns the object that has owner information
        """
        return self

    def clean(self):
        super().clean()
        if self.repetitions is None and self.weight is None:
            raise ValidationError('Both repetitions and weight cannot be null at the same time.')

        if self.repetitions is not None and self.repetitions_unit is None:
            raise ValidationError('Repetitions unit must be present if repetitions have a value.')

        if self.weight is not None and self.weight_unit is None:
            raise ValidationError('Weight unit must be present if weight has a value.')

    def save(self, *args, **kwargs):
        """
        Plumbing
        """
        self.clean()

        # If the routine does not belong to this user, do not save
        if self.routine and self.routine.user != self.user:
            return

        # Same check for slot_entry's owning routine
        if self.slot_entry and self.slot_entry.slot.day.routine.user != self.user:
            return

        # If a session was explicitly provided but belongs to a different
        # user, drop the reference so we don't accidentally tie this log
        # to someone else's session. The auto-create branch below will
        # then provide the correct one.
        if self.session_id and self.session.user_id != self.user_id:
            self.session = None

        # Auto-create a session only if the client didn't provide one.
        if not self.session_id:
            # The day is only a default: an existing session for the date keeps
            # its day, and the (user, date, routine) dedup semantics stay unchanged.
            day = None
            if self.slot_entry and self.slot_entry.slot.day.routine_id == self.routine_id:
                day = self.slot_entry.slot.day

            try:
                self.session = WorkoutSession.objects.get_or_create(
                    user=self.user,
                    date=self.date,
                    routine=self.routine,
                    defaults={'day': day},
                )[0]
            except WorkoutSession.MultipleObjectsReturned:
                # TODO: duplicate sessions can exist for the same (user, date, routine)
                #       when routine is NULL, as the unique_together does not cover a NULL
                #       routine in PostgreSQL.
                #       This is a fix till we correctly take care of the problem, we just
                #       reuse one session (ids are uuid7, so ordering by id yields the
                #       earliest) instead of crashing the log POST with MultipleObjectsReturned.
                self.session = (
                    WorkoutSession.objects.filter(
                        user=self.user,
                        date=self.date,
                        routine=self.routine,
                    )
                    .order_by('id')
                    .first()
                )

        # If the user of next_log is not this user, remove foreign key
        if self.next_log and self.next_log.user != self.user:
            self.next_log = None

        # Save to db
        super().save(*args, **kwargs)

        # The app creates its sessions itself and can leave the day empty, which
        # hides them from days with need_logs_to_advance. Only filled in when all
        # logs of the session agree on one day, like migration 0028 does: a wrong
        # day would open the gate on a day the user never trained.
        #
        # Can be removed once the app versions that set the day are widely adopted.
        if self.session_id and self.slot_entry and self.session.day_id is None:
            days = list(
                WorkoutLog.objects.filter(
                    session_id=self.session_id,
                    slot_entry__isnull=False,
                )
                .values_list('slot_entry__slot__day_id', 'slot_entry__slot__day__routine_id')
                .distinct()
            )

            if len(days) == 1 and days[0][1] == self.session.routine_id:
                self.session.day_id = days[0][0]
                self.session.save(update_fields=['day'])
