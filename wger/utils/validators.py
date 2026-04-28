# Django
from django.core.exceptions import ValidationError
from django.utils.dateparse import (
    parse_date,
    parse_datetime,
)
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import Language


def validate_language_code(value):
    try:
        language = Language.objects.get(short_name=value)
    except Language.DoesNotExist:
        raise ValidationError(f'The language "{value}" does not exist in this wger database.')


def validate_iso_date(value):
    """
    Accept a date or datetime in ISO-8601 form.

    Django's `parse_datetime` covers full ISO-8601 (with or without timezone),
    `parse_date` covers the common short form `YYYY-MM-DD`. Both return None
    on a non-matching string rather than raising, so we test them in order.
    """
    if parse_datetime(value) is None and parse_date(value) is None:
        raise ValidationError(
            f'"{value}" is not a valid ISO-8601 date or datetime '
            f'(e.g. "2026-04-01" or "2026-04-01T00:00:00Z").'
        )
