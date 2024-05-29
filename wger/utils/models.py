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
from wger.utils.constants import CC_BY_SA_4_ID


"""
Abstract model classes
"""


class AbstractLicenseModel(models.Model):
    """
    Abstract class that adds license information to a model

    Implements TASL (Title - Author - Source - License) for proper attribution

    See also
    - https://wiki.creativecommons.org/wiki/Recommended_practices_for_attribution
    - https://wiki.creativecommons.org/wiki/Best_practices_for_attribution
    """

    class Meta:
        abstract = True

    license = models.ForeignKey(
        License,
        verbose_name=_('License'),
        default=CC_BY_SA_4_ID,
        on_delete=models.CASCADE,
    )

    license_title = models.CharField(
        verbose_name=_('The original title of this object, if available'),
        max_length=300,
        blank=True,
    )

    license_object_url = models.URLField(
        verbose_name=_('Link to original object, if available'),
        max_length=200,
        blank=True,
    )

    license_author = models.TextField(
        verbose_name=_('Author(s)'),
        max_length=3500,
        blank=True,
        null=True,
        help_text=_('If you are not the author, enter the name or source here.'),
    )

    license_author_url = models.URLField(
        verbose_name=_('Link to author profile, if available'),
        max_length=200,
        blank=True,
    )

    license_derivative_source_url = models.URLField(
        verbose_name=_('Link to the original source, if this is a derivative work'),
        help_text=_(
            'Note that a derivative work is one which is not only based on a previous '
            'work, but which also contains sufficient new, creative content to entitle it '
            'to its own copyright.'
        ),
        max_length=200,
        blank=True,
    )

    @property
    def attribution_link(self):
        out = ''

        if self.license_object_url:
            out += f'<a href="{self.license_object_url}">{self.license_title}</a>'
        else:
            out += self.license_title

        out += ' by '
        if self.license_author_url:
            out += f'<a href="{self.license_author_url}">{self.license_author}</a>'
        else:
            out += self.license_author

        out += f' is licensed under <a href="{self.license.url}">{self.license.short_name}</a>'

        if self.license_derivative_source_url:
            out += (
                f'/ A derivative work from <a href="{self.license_derivative_source_url}">the '
                f'original work</a>'
            )

        return out


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


def collect_models_author_history(model_list):
    """
    Get unique set of license authors from historical records from models.
    """
    out = set()
    for model in model_list:
        out = out.union(collect_model_author_history(model))
    return out
