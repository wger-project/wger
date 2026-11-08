#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
Captcha providers for the signup and password reset forms

WGER_SETTINGS['CAPTCHA_PROVIDER'] names one of the PROVIDERS (or 'none'). A new
provider is a CaptchaProvider subclass with an entry in PROVIDERS; the forms and
the system checks only go through this module.
"""

# Standard Library
import logging

# Django
from django import forms
from django.conf import settings
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy

# Third Party
import requests
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV3

# wger
from wger.utils.requests import wger_headers


logger = logging.getLogger(__name__)

TURNSTILE_SCRIPT_URL = 'https://challenges.cloudflare.com/turnstile/v0/api.js'
TURNSTILE_VERIFY_URL = 'https://challenges.cloudflare.com/turnstile/v0/siteverify'


class TurnstileWidget(forms.Widget):
    """
    Cloudflare's Turnstile widget, rendered implicitly by its script

    The script adds the token as the hidden input cf-turnstile-response to the
    surrounding form.
    """

    template_name = 'forms/turnstile.html'

    def __init__(self, action: str, attrs=None):
        super().__init__(attrs)
        self.action = action

    def get_context(self, name, value, attrs):
        context = super().get_context(name, value, attrs)
        context['widget'].update(
            {
                'site_key': settings.TURNSTILE_SITE_KEY,
                'action': self.action,
                'script_url': TURNSTILE_SCRIPT_URL,
            }
        )
        return context

    def value_from_datadict(self, data, files, name):
        return data.get('cf-turnstile-response')


class TurnstileField(forms.CharField):
    """
    Verifies the Turnstile token with Cloudflare, rejects it if that fails
    """

    default_error_messages = {
        'required': gettext_lazy('The captcha could not be verified, please try again.'),
        'invalid': gettext_lazy('The captcha could not be verified, please try again.'),
    }

    def __init__(self, action: str, **kwargs):
        # Cloudflare's tokens are at most 2048 characters
        super().__init__(widget=TurnstileWidget(action), max_length=2048, **kwargs)

    def validate(self, value):
        super().validate(value)

        try:
            response = requests.post(
                TURNSTILE_VERIFY_URL,
                data={'secret': settings.TURNSTILE_SECRET_KEY, 'response': value},
                headers=wger_headers(),
                timeout=10,
            )
            response.raise_for_status()
            result = response.json()
        except (requests.RequestException, ValueError) as e:
            logger.warning('Turnstile verification request failed: %s', type(e).__name__)
            result = None

        if not isinstance(result, dict) or result.get('success') is not True:
            raise ValidationError(self.error_messages['invalid'], code='invalid')


class CaptchaProvider:
    """A captcha service the forms can be secured with"""

    required_settings: tuple[str, ...] = ()
    """Settings that must not be empty for the captcha to work"""

    def field(self, action: str) -> forms.Field:
        """
        A fresh form field; the action names the form, e.g. for the provider's statistics
        """
        raise NotImplementedError

    def missing_settings(self) -> list[str]:
        return [name for name in self.required_settings if not getattr(settings, name, '')]


class RecaptchaProvider(CaptchaProvider):
    required_settings = ('RECAPTCHA_PUBLIC_KEY', 'RECAPTCHA_PRIVATE_KEY')

    def field(self, action: str) -> forms.Field:
        return ReCaptchaField(
            widget=ReCaptchaV3(action=action),
            label='reCaptcha',
            help_text=gettext_lazy('The form is secured with reCAPTCHA'),
        )


class TurnstileProvider(CaptchaProvider):
    required_settings = ('TURNSTILE_SITE_KEY', 'TURNSTILE_SECRET_KEY')

    def field(self, action: str) -> forms.Field:
        return TurnstileField(
            action,
            label='Turnstile',
            help_text=gettext_lazy('The form is secured with Cloudflare Turnstile'),
        )


PROVIDERS: dict[str, CaptchaProvider] = {
    'recaptcha': RecaptchaProvider(),
    'turnstile': TurnstileProvider(),
}


def captcha_provider() -> str:
    """
    The configured captcha provider, 'none' or a key of PROVIDERS

    The deprecated USE_RECAPTCHA=True still means 'recaptcha' when no other
    provider is set.
    """
    provider = settings.WGER_SETTINGS.get('CAPTCHA_PROVIDER', 'none')
    if provider == 'none' and settings.WGER_SETTINGS.get('USE_RECAPTCHA'):
        return 'recaptcha'
    return provider


def captcha_field(action: str) -> forms.Field | None:
    """
    The field for the configured captcha provider, None if there is none
    """
    provider = PROVIDERS.get(captcha_provider())
    return provider.field(action) if provider else None
