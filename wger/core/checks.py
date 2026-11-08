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
from wger.core.captcha import (
    PROVIDERS,
    captcha_provider,
)
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

    # The captcha provider must exist and have its keys
    provider_name = captcha_provider()
    valid_providers = ('none', *PROVIDERS)
    if provider_name not in valid_providers:
        errors.append(
            Error(
                f"Invalid CAPTCHA_PROVIDER: '{provider_name}'",
                hint=f'CAPTCHA_PROVIDER must be one of {valid_providers}',
                obj=settings,
                id='wger.E002',
            )
        )
    elif provider_name != 'none':
        missing = PROVIDERS[provider_name].missing_settings()
        if missing:
            errors.append(
                Warning(
                    f'Captcha provider "{provider_name}" is not configured',
                    hint=f'Set {", ".join(missing)}, otherwise the captcha will not work.',
                    obj=settings,
                    id='wger.W004',
                )
            )

    # USE_RECAPTCHA is deprecated, an explicit CAPTCHA_PROVIDER overrides it
    if settings.WGER_SETTINGS.get('USE_RECAPTCHA'):
        configured = settings.WGER_SETTINGS.get('CAPTCHA_PROVIDER', 'none')
        if configured == 'none':
            message = 'USE_RECAPTCHA is deprecated'
            hint = 'Set CAPTCHA_PROVIDER to "recaptcha" instead and remove USE_RECAPTCHA.'
        else:
            message = 'USE_RECAPTCHA is ignored'
            hint = f'CAPTCHA_PROVIDER "{configured}" takes precedence, remove USE_RECAPTCHA.'
        errors.append(Warning(message, hint=hint, obj=settings, id='wger.W005'))

    return errors
