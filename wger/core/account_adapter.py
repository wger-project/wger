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
from django.utils import timezone

# Third Party
from allauth.account.adapter import DefaultAccountAdapter


class WgerAccountAdapter(DefaultAccountAdapter):
    """Wger Account Adapter for allauth"""

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
