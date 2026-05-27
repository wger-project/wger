# This file is part of wger Workout Manager.
#
# wger Workout Manager is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# wger Workout Manager is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License

# Standard Library
from datetime import timedelta

# Django
from django.conf import settings
from django.utils import (
    timezone,
    translation,
)

# Third Party
from allauth.account.adapter import DefaultAccountAdapter


class WgerAccountAdapter(DefaultAccountAdapter):
    """Wger Account Adapter for allauth"""

    def is_open_for_signup(self, request):
        return settings.WGER_SETTINGS['ALLOW_REGISTRATION']

    def save_user(self, request, user, form, commit=True):
        """
        Create the user via allauth, then pre-fill the wger profile bits the
        old registration view used to set (notification language, default gym).
        """
        # wger
        from wger.config.models import GymConfig
        from wger.gym.models import GymUserConfig
        from wger.utils.language import load_language

        user = super().save_user(request, user, form, commit=commit)
        if not commit:
            return user

        profile = user.userprofile
        profile.notification_language = load_language(translation.get_language())

        gym_config = GymConfig.objects.get(pk=1)
        if gym_config.default_gym:
            profile.gym = gym_config.default_gym
        profile.save()

        if gym_config.default_gym:
            GymUserConfig.objects.get_or_create(gym=gym_config.default_gym, user=user)

        return user

    def send_mail(self, template_prefix, email, context):
        """
        Add token expiration info to the email context.

        Note that we add this to the context of all emails, even if this
        doesn't make sense for some of them. However, this is acceptable since it's
        only the template context and we currently only use the verification email,
        which needs this information.
        """

        expire_days = settings.ACCOUNT_EMAIL_CONFIRMATION_EXPIRE_DAYS
        context['expire_hours'] = expire_days * 24
        context['expire_date'] = timezone.now() + timedelta(days=expire_days)
        super().send_mail(template_prefix, email, context)
