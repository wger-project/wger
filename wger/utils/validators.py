# Django
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _

# wger
from wger.core.models import Language


def validate_language_code(value):
    try:
        language = Language.objects.get(short_name=value)
    except Language.DoesNotExist:
        raise ValidationError(f'The language "{value}" does not exist in this wger database.')
