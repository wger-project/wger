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

# Django
from django.core import mail
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import (
    WgerAccessTestCase,
    WgerTestCase,
)
from wger.mailer.models import (
    CronEntry,
    Log,
)


class AccessContractTestCase(WgerAccessTestCase):
    """
    Test accessing the detail page of a contract
    """

    url = reverse('email:email:overview', kwargs={'gym_pk': 1})
    user_success = ('manager1', 'manager2')
    user_fail = (
        'admin',
        'general_manager1',
        'manager3',
        'manager4',
        'test',
        'member1',
        'member2',
        'member3',
        'member4',
        'member5',
    )


class EmailListFormPreviewTestCase(WgerTestCase):
    """
    Tests authorization on the gym mass-email FormPreview (both stages).
    """

    def setUp(self):
        super().setUp()
        self.url = reverse('email:email:add-gym', kwargs={'gym_pk': 1})

    def test_preview_stage_rejects_unauthorized(self):
        """
        Stage 1 must reject unauthorized callers before process_preview()
        runs — otherwise the preview email is sent regardless.
        """
        # Anonymous
        response = self.client.post(
            self.url,
            {'stage': '1', 'subject': 'Spam subject', 'body': 'Spam body'},
        )
        self.assertEqual(response.status_code, 403)

        # A logged-in user without the mailer permission
        self.user_login('member1')
        response = self.client.post(
            self.url,
            {'stage': '1', 'subject': 'Spam subject', 'body': 'Spam body'},
        )
        self.assertEqual(response.status_code, 403)

        # No preview email was sent in either case
        self.assertEqual(len(mail.outbox), 0)

    def test_send_stage_rejects_cross_gym_hash_replay(self):
        """
        The formtools security hash only covers the form fields, not the gym.
        A valid hash obtained for one gym must not let done() run against
        another gym.
        """
        # manager1 legitimately previews for their own gym (gym 1) -> valid hash
        self.user_login('manager1')
        preview = self.client.post(
            self.url,
            {'stage': '1', 'subject': 'Hello', 'body': 'Hello body'},
        )
        self.assertEqual(preview.status_code, 200)
        hash_value = preview.context['hash_value']

        # ...then replays stage 2 with that hash against gym 2
        log_count = Log.objects.count()
        cron_count = CronEntry.objects.count()
        cross_gym_url = reverse('email:email:add-gym', kwargs={'gym_pk': 2})
        response = self.client.post(
            cross_gym_url,
            {'stage': '2', 'hash': hash_value, 'subject': 'Hello', 'body': 'Hello body'},
        )

        self.assertEqual(response.status_code, 403)
        self.assertEqual(Log.objects.count(), log_count)
        self.assertEqual(CronEntry.objects.count(), cron_count)

    def test_authorized_manager_can_preview_and_send(self):
        """The happy path still works: a gym manager can preview and queue emails."""
        self.user_login('manager1')

        preview = self.client.post(
            self.url,
            {'stage': '1', 'subject': 'Hello', 'body': 'Hello body'},
        )
        self.assertEqual(preview.status_code, 200)
        hash_value = preview.context['hash_value']

        log_count = Log.objects.count()
        response = self.client.post(
            self.url,
            {'stage': '2', 'hash': hash_value, 'subject': 'Hello', 'body': 'Hello body'},
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Log.objects.count(), log_count + 1)
