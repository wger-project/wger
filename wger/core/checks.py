# Django
from django.conf import settings
from django.core.checks import (
    Error,
    Warning,
    register,
)

# wger
from wger.utils.constants import DOWNLOAD_INGREDIENT_OPTIONS


@register()
def settings_check(app_configs, **kwargs):
    errors = []

    # Upstream wger instance should be configured
    if not settings.WGER_SETTINGS.get('WGER_INSTANCE'):
        errors.append(
            Warning(
                'wger instance not set',
                hint='No wger instance configured, sync commands will not work',
                obj=settings,
                id='wger.W001',
            )
        )

    # Only one setting should be set
    if settings.WGER_SETTINGS['DOWNLOAD_INGREDIENTS_FROM'] not in DOWNLOAD_INGREDIENT_OPTIONS:
        errors.append(
            Error(
                'Ingredient images configuration error',
                hint=f'Origin for ingredient images misconfigured. Valid options are '
                f'{DOWNLOAD_INGREDIENT_OPTIONS}',
                obj=settings,
                id='wger.E001',
            )
        )
    return errors
