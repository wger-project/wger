# Django
from django.core.exceptions import ValidationError

# wger
from wger.core.models import Language


def validate_language_code(value):
    try:
        language = Language.objects.get(short_name=value)
    except Language.DoesNotExist:
        raise ValidationError(f'The language "{value}" does not exist in this wger database.')
