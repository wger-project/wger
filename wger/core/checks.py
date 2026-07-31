# Standard Library
from datetime import timedelta

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

    # A very short refresh token lifetime is usually a unit mix-up: the
    # REFRESH_TOKEN_LIFETIME environment variable is in hours, not days
    # or minutes. Apps can only stay logged in for this long while unused.
    refresh_lifetime = settings.SIMPLE_JWT['REFRESH_TOKEN_LIFETIME']
    if refresh_lifetime < timedelta(days=7):
        errors.append(
            Warning(
                f'Very short JWT refresh token lifetime: {refresh_lifetime}',
                hint='The REFRESH_TOKEN_LIFETIME environment variable is set in hours '
                '(default 2880, i.e. 120 days). Users of the mobile app have to log in '
                'again after not opening it for longer than this value.',
                obj=settings,
                id='wger.W003',
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
