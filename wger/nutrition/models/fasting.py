# wger/nutrition/models/fasting.py

import datetime

from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone
from django.utils.translation import gettext_lazy as _


class FastingWindow(models.Model):
    """
    A time window where the user is fasting.

    If `end` is null, the fast is currently in progress.
    """

    user = models.ForeignKey(
        User,
        verbose_name=_('User'),
        on_delete=models.CASCADE,
    )

    start = models.DateTimeField(
        verbose_name=_('Start of fast'),
        default=timezone.now,
    )

    end = models.DateTimeField(
        verbose_name=_('End of fast'),
        null=True,
        blank=True,
    )

    goal_duration_minutes = models.PositiveIntegerField(
        verbose_name=_('Goal duration (minutes)'),
        null=True,
        blank=True,
        help_text=_('Optional target length for this fast.'),
    )

    note = models.CharField(
        verbose_name=_('Notes'),
        max_length=255,
        blank=True,
    )

    created = models.DateTimeField(auto_now_add=True)
    updated = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-start']
        verbose_name = _('Fasting window')
        verbose_name_plural = _('Fasting windows')

    def __str__(self):
        return f'{self.user} fast starting {self.start}'

    def get_owner_object(self):
        """
        Used by wger's permission helpers.
        """
        return self

    @property
    def is_active(self) -> bool:
        return self.end is None

    @property
    def duration(self) -> datetime.timedelta:
        end = self.end or timezone.now()
        return end - self.start

    @property
    def duration_seconds(self) -> int:
        return int(self.duration.total_seconds())
