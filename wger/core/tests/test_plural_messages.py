# This file is part of wger Workout Manager, licensed under AGPL-3.0-or-later.

# Standard Library
from datetime import timedelta

# Django
from django.contrib.auth.models import AnonymousUser
from django.template.loader import render_to_string
from django.test import SimpleTestCase
from django.utils import timezone
from django.utils.html import strip_tags
from django.utils.translation import override


class CountedTemplateMessagesTestCase(SimpleTestCase):
    """Counted messages in pages and emails select the appropriate plural form."""

    def render_message(self, template: str, context: dict) -> str:
        with override('en'):
            rendered = render_to_string(template, {'user': AnonymousUser(), **context})
        return ' '.join(strip_tags(rendered).split())

    def test_confirmation_link_lifetime(self):
        for hours in (1, 2, 24):
            with self.subTest(hours=hours):
                text = self.render_message(
                    'account/email/email_confirmation_message.html',
                    {'expire_hours': hours, 'expire_date': timezone.now() + timedelta(hours=hours)},
                )
                unit = 'hour' if hours == 1 else 'hours'
                self.assertIn(f'The link is valid for {hours} {unit} (until', text)

    def test_inactive_member_reminder(self):
        for weeks in (1, 2, 21):
            with self.subTest(weeks=weeks):
                text = self.render_message('gym/email_inactive_members.html', {'weeks': weeks})
                unit = 'week' if weeks == 1 else 'weeks'
                self.assertIn(f'in the last {weeks} {unit}', text)
                if weeks == 1:
                    self.assertNotIn('in the last 1 weeks', text)
