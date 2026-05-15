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

# Standard Library
from urllib.parse import urlsplit

# Django
from django.db import models
from django.utils.html import (
    escape,
    format_html,
)
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import License
from wger.utils.constants import CC_BY_SA_4_LICENSE_ID


"""
Abstract model classes
"""


def _safe_attribution_url(url: str) -> str:
    """
    Return ``url`` only if it uses an http(s) scheme, otherwise an empty string.

    ``attribution_link`` embeds these values into ``<a href="...">``; a
    ``javascript:`` (or ``data:`` etc.) scheme would otherwise become a
    clickable stored-XSS payload once the rendered link reaches a template.
    """
    if not url:
        return ''
    try:
        scheme = urlsplit(url).scheme
    except ValueError:
        return ''
    return url if scheme in ('http', 'https') else ''


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
        default=CC_BY_SA_4_LICENSE_ID,
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
        # Only http(s) URLs may be embedded as links — a javascript:/data: URL
        # in any of these (sync-populated) fields would otherwise be rendered
        # as a clickable stored-XSS payload.
        object_url = _safe_attribution_url(self.license_object_url)
        author_url = _safe_attribution_url(self.license_author_url)
        derivative_url = _safe_attribution_url(self.license_derivative_source_url)
        license_url = _safe_attribution_url(self.license.url)

        if object_url:
            title = format_html('<a href="{}">{}</a>', object_url, self.license_title)
        else:
            title = escape(self.license_title)

        if author_url:
            author = format_html('<a href="{}">{}</a>', author_url, self.license_author)
        else:
            author = escape(self.license_author)

        if license_url:
            license_link = format_html('<a href="{}">{}</a>', license_url, self.license.short_name)
        else:
            license_link = escape(self.license.short_name)

        derivative = ''
        if derivative_url:
            derivative = format_html(
                ' / A derivative work from <a href="{}">the original work</a>',
                derivative_url,
            )

        return format_html(
            '{} by {} is licensed under {}{}',
            title,
            author,
            license_link,
            derivative,
        )


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
