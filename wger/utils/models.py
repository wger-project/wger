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

# Django
from django.db import models
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import License
from wger.utils.constants import DEFAULT_LICENSE_ID


"""
Abstract model classes
"""


class AbstractLicenseModel(models.Model):
    """
    Abstract class that adds license information to a model
    """

    class Meta:
        abstract = True

    license = models.ForeignKey(
        License,
        verbose_name=_('License'),
        default=DEFAULT_LICENSE_ID,
        on_delete=models.CASCADE,
    )
    """The item's license"""

    license_author = models.CharField(
        verbose_name=_('Author'),
        max_length=60,
        blank=True,
        null=True,
        help_text=_(
            'If you are not the author, enter the name or '
            'source here. This is needed for some licenses '
            'e.g. the CC-BY-SA.'
        )
    )
    """The author if it is not the uploader"""


class AbstractSubmissionModel(models.Model):
    """
    Abstract class used for model for user submitted data.

    These models have to be approved first by an administrator before they are
    shows in the website. There is also a manager that can be used:
    utils.managers.SubmissionManager
    """

    class Meta:
        abstract = True

    STATUS_PENDING = '1'
    STATUS_ACCEPTED = '2'
    STATUS_DECLINED = '3'

    STATUS = (
        (STATUS_PENDING, _('Pending')),
        (STATUS_ACCEPTED, _('Accepted')),
        (STATUS_DECLINED, _('Declined')),
    )

    status = models.CharField(
        max_length=2,
        choices=STATUS,
        default=STATUS_PENDING,
        editable=False,
    )
    """Status of the submission, e.g. accepted or declined"""


class AbstractHistoryMixin:
    """
    Abstract class used to model specific historical records.

    Utilized in conjunction with simple_history's HistoricalRecords.
    """

    @property
    def author_history(self):
        """Author history is the unique set of license authors from historical records"""
        return collect_model_author_history(self)


def collect_model_author_history(model):
    """
    Get unique set of license authors from historical records from model.
    """
    out = set()
    for author in [h.license_author for h in set(model.history.all()) if h.license_author]:
        out.add(author)
    return out


def collect_models_author_history(models):
    """
    Get unique set of license authors from historical records from models.
    """
    out = set()
    for model in models:
        out = out.union(collect_model_author_history(model))
    return out
