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
import datetime

# Django
from django.contrib.auth.models import (
    Permission,
    User,
)
from django.contrib.contenttypes.models import ContentType
from django.urls import reverse

# wger
from wger.core.models import UserProfile
from wger.core.tests.base_testcase import WgerTestCase
from wger.gym.models import (
    Gym,
    GymAdminConfig,
)


class GymAddUserTestCase(WgerTestCase):
    """
    Tests admin adding users to gyms
    """

    def add_user(self, fail=False):
        """
        Helper function to add users
        """
        count_before = User.objects.all().count()
        GymAdminConfig.objects.all().delete()
        response = self.client.get(reverse('gym:gym:add-user', kwargs={'gym_pk': 1}))
        self.assertEqual(GymAdminConfig.objects.all().count(), 0)
        if fail:
            self.assertEqual(response.status_code, 403)
        else:
            self.assertEqual(response.status_code, 200)

        response = self.client.post(
            reverse('gym:gym:add-user', kwargs={'gym_pk': 1}),
            {
                'first_name': 'Cletus',
                'last_name': 'Spuckle',
                'username': 'cletus',
                'email': 'cletus@spuckle-megacorp.com',
                'role': 'admin',
            },
        )
        count_after = User.objects.all().count()
        if fail:
            self.assertEqual(response.status_code, 403)
            self.assertEqual(count_before, count_after)
            self.assertFalse(self.client.session.get('gym.user'))
        else:
            self.assertEqual(count_before + 1, count_after)
            self.assertEqual(response.status_code, 302)
            self.assertTrue(self.client.session['gym.user']['user_pk'], 3)
            self.assertTrue(self.client.session['gym.user']['password'])
            self.assertEqual(len(self.client.session['gym.user']['password']), 15)
            new_user = User.objects.get(pk=self.client.session['gym.user']['user_pk'])
            self.assertEqual(GymAdminConfig.objects.all().count(), 1)
            self.assertEqual(new_user.userprofile.gym_id, 1)

    def test_add_user_authorized(self):
        """
        Tests adding a user as authorized user
        """
        self.user_login('admin')
        self.add_user()

    def test_add_user_authorized2(self):
        """
        Tests adding a user as authorized user
        """
        self.user_login('general_manager1')
        self.add_user()

    def test_add_user_unauthorized(self):
        """
        Tests adding a user an unauthorized user
        """
        self.user_login('test')
        self.add_user(fail=True)

    def test_add_user_unauthorized2(self):
        """
        Tests adding a user an unauthorized user
        """
        self.user_login('trainer1')
        self.add_user(fail=True)

    def test_add_user_unauthorized3(self):
        """
        Tests adding a user an unauthorized user
        """
        self.user_login('manager3')
        self.add_user(fail=True)

    def test_add_user_logged_out(self):
        """
        Tests adding a user a logged out user
        """
        self.add_user(fail=True)

    def new_user_data_export(self, fail=False):
        """
        Helper function to test exporting the data of a newly created user
        """
        response = self.client.get(reverse('gym:gym:new-user-data-export'))
        if fail:
            self.assertIn(response.status_code, (302, 403))
        else:
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response['Content-Type'], 'text/csv')
            today = datetime.date.today()
            filename = 'User-data-{t.year}-{t.month:02d}-{t.day:02d}-cletus.csv'.format(t=today)
            self.assertEqual(response['Content-Disposition'], f'attachment; filename={filename}')
            self.assertGreaterEqual(len(response.content), 90)
            self.assertLessEqual(len(response.content), 120)

    def test_new_user_data_export(self):
        """
        Test exporting the data of a newly created user
        """
        self.user_login('admin')
        self.add_user()
        self.new_user_data_export(fail=False)

        self.user_logout()
        self.new_user_data_export(fail=True)

        self.user_logout()
        self.user_login('test')
        self.new_user_data_export(fail=True)


class TrainerLoginTestCase(WgerTestCase):
    """
    Tests the trainer login view (switching to user ID)
    """

    def test_anonymous(self):
        """
        Test the trainer login as an anonymous user
        """
        response = self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 1}))
        self.assertEqual(response.status_code, 302)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_user(self):
        """
        Test the trainer login as a logged in user without rights
        """
        self.user_login('test')
        response = self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 1}))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_trainer(self):
        """
        Test the trainer login as a logged in user with enough rights
        """
        self.user_login('admin')
        response = self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('trainer.identity'))

    def test_wrong_gym(self):
        """
        Test changing the identity to a user in a different gym
        """
        profile = UserProfile.objects.get(user_id=2)
        profile.gym_id = 2
        profile.save()
        self.user_login('admin')
        response = self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 404)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_gym_trainer(self):
        """
        Test changing the identity to a user with trainer rights
        """
        user = User.objects.get(pk=2)
        content_type = ContentType.objects.get_for_model(Gym)
        permission = Permission.objects.get(content_type=content_type, codename='gym_trainer')
        user.user_permissions.add(permission)

        self.user_login('admin')
        response = self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_gym_manager(self):
        """
        Test changing the identity to a user with gym management rights
        """
        user = User.objects.get(pk=2)
        content_type = ContentType.objects.get_for_model(Gym)
        permission = Permission.objects.get(content_type=content_type, codename='manage_gym')
        user.user_permissions.add(permission)

        self.user_login('admin')
        response = self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_chained_hop_into_manager_is_blocked(self):
        """
        After a trainer legitimately switches into a regular user, the
        session flag ``trainer.identity`` is set. Calling trainer-login
        again must not let the (now non-trainer) session climb into a
        gym manager account just because that flag is present.
        """

        # Step 1: legitimate hop — trainer1 (user 4) into test (user 2)
        self.user_login('trainer1')
        response = self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(self.client.session.get('trainer.identity'))

        # Step 2: chained hop — now-as-test, target manager1 (user 9, has manage_gym)
        response = self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 9}))
        self.assertEqual(response.status_code, 403)

    def test_open_redirect_external_next_blocked(self):
        """
        The ?next= parameter must only redirect to the same origin.
        """
        for evil in ('https://evil.example/', '//evil.example/x', '%2F%2Fevil.example'):
            self.user_login('admin')
            response = self.client.post(
                reverse('core:user:trainer-login', kwargs={'user_pk': 2}) + f'?next={evil}'
            )
            self.assertEqual(response.status_code, 302)
            self.assertNotIn('evil.example', response['Location'])
            self.user_logout()

    def test_safe_next_passes_through(self):
        self.user_login('admin')
        response = self.client.post(
            reverse('core:user:trainer-login', kwargs={'user_pk': 2}) + '?next=/exercise/overview'
        )
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response['Location'], '/exercise/overview')

    def test_gyms_manager(self):
        """
        Test changing the identity to a user with gyms management rights
        """
        user = User.objects.get(pk=2)
        content_type = ContentType.objects.get_for_model(Gym)
        permission = Permission.objects.get(content_type=content_type, codename='manage_gyms')
        user.user_permissions.add(permission)

        self.user_login('admin')
        response = self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 403)
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_get_does_not_rebind_session(self):
        """
        ``trainer_login`` must reject unsafe HTTP methods
        """
        self.user_login('admin')
        response = self.client.get(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
        self.assertEqual(response.status_code, 405)
        self.assertFalse(self.client.session.get('trainer.identity'))


class GymScopeGuardsTestCase(WgerTestCase):
    """
    Test the gym-scope guards
    """

    VICTIM_USER_PK = 2  # 'test'

    def _set_gym(self, user_pk, gym_id):
        profile = UserProfile.objects.get(user_id=user_pk)
        profile.gym_id = gym_id
        profile.save()

    def _both_gyms_none(self, attacker_pk):
        self._set_gym(attacker_pk, None)
        self._set_gym(self.VICTIM_USER_PK, None)

    def test_reset_password_blocked_when_both_gyms_none(self):
        """
        A manager with gym=None must not reset another gym=None user's
        password.
        """
        self._both_gyms_none(attacker_pk=9)  # manager1
        self.user_login('manager1')

        response = self.client.get(
            reverse('gym:gym:reset-user-password', kwargs={'user_pk': self.VICTIM_USER_PK})
        )
        self.assertEqual(response.status_code, 403)

    def test_reset_password_blocked_attacker_none_victim_real_gym(self):
        """
        Sanity check: an attacker with gym=None must not be able to reset
        the password of a user that is in a real gym either.
        """
        self._set_gym(9, None)  # manager1; victim keeps fixture gym=1
        self.user_login('manager1')

        response = self.client.get(
            reverse('gym:gym:reset-user-password', kwargs={'user_pk': self.VICTIM_USER_PK})
        )
        self.assertEqual(response.status_code, 403)

    def test_reset_password_allowed_same_gym(self):
        """
        Sanity check: the legitimate same-gym flow must keep working.
        """
        self.user_login('manager1')

        response = self.client.get(
            reverse('gym:gym:reset-user-password', kwargs={'user_pk': self.VICTIM_USER_PK})
        )
        self.assertEqual(response.status_code, 200)

    def test_permissions_edit_blocked_when_both_gyms_none(self):
        self._both_gyms_none(attacker_pk=9)
        self.user_login('manager1')

        response = self.client.get(
            reverse('gym:gym:edit-user-permission', kwargs={'user_pk': self.VICTIM_USER_PK})
        )
        self.assertEqual(response.status_code, 403)

    def test_user_edit_blocked_when_both_gyms_none(self):
        self._both_gyms_none(attacker_pk=9)
        self.user_login('manager1')

        response = self.client.get(reverse('core:user:edit', kwargs={'pk': self.VICTIM_USER_PK}))
        self.assertEqual(response.status_code, 403)

    def test_user_overview_blocked_when_both_gyms_none(self):
        self._both_gyms_none(attacker_pk=9)
        self.user_login('manager1')

        response = self.client.get(
            reverse('core:user:overview', kwargs={'pk': self.VICTIM_USER_PK})
        )
        self.assertEqual(response.status_code, 403)

    def test_trainer_login_blocked_when_both_gyms_none(self):
        self._both_gyms_none(attacker_pk=4)  # trainer1
        self.user_login('trainer1')

        response = self.client.post(
            reverse('core:user:trainer-login', kwargs={'user_pk': self.VICTIM_USER_PK})
        )
        self.assertIn(response.status_code, (403, 404))
        self.assertFalse(self.client.session.get('trainer.identity'))

    def test_admin_notes_list_blocked_when_both_gyms_none(self):
        """
        A trainer with gym=None must not list admin notes attached to
        another gym=None user.
        """
        self._set_gym(4, None)  # trainer1
        self._set_gym(14, None)  # member1, owner of admin note pk=1
        self.user_login('trainer1')

        response = self.client.get(reverse('gym:admin_note:list', kwargs={'user_pk': 14}))
        self.assertEqual(response.status_code, 403)

    def test_admin_notes_update_blocked_when_both_gyms_none(self):
        """
        Editing an admin note that belongs to a gym=None member must be
        blocked for a gym=None trainer.
        """
        self._set_gym(4, None)
        self._set_gym(14, None)
        self.user_login('trainer1')

        response = self.client.get(reverse('gym:admin_note:edit', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    def test_documents_list_blocked_when_both_gyms_none(self):
        self._set_gym(4, None)
        self._set_gym(14, None)
        self.user_login('trainer1')

        response = self.client.get(reverse('gym:document:list', kwargs={'user_pk': 14}))
        self.assertEqual(response.status_code, 403)

    def test_documents_update_blocked_when_both_gyms_none(self):
        self._set_gym(4, None)
        self._set_gym(14, None)
        self.user_login('trainer1')

        response = self.client.get(reverse('gym:document:edit', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    def test_contracts_list_blocked_when_both_gyms_none(self):
        self._set_gym(9, None)  # manager1
        self._set_gym(15, None)  # member2, owner of contract pk=1
        self.user_login('manager1')

        response = self.client.get(reverse('gym:contract:list', kwargs={'user_pk': 15}))
        self.assertEqual(response.status_code, 403)

    def test_contracts_update_blocked_when_both_gyms_none(self):
        self._set_gym(9, None)
        self._set_gym(15, None)
        self.user_login('manager1')

        response = self.client.get(reverse('gym:contract:edit', kwargs={'pk': 1}))
        self.assertEqual(response.status_code, 403)

    def test_delete_blocked_when_both_gyms_none(self):
        """
        A manager with gym=None must not be able to load (or POST to) the
        delete-account form for another gym=None user.
        """
        self._both_gyms_none(attacker_pk=9)  # manager1
        self.user_login('manager1')

        response = self.client.get(
            reverse('core:user:delete', kwargs={'user_pk': self.VICTIM_USER_PK})
        )
        self.assertEqual(response.status_code, 403)

    def test_delete_post_does_not_remove_victim_when_both_gyms_none(self):
        """
        Even on POST with correct password confirmation the destructive
        ``user.delete()`` must not run when the attacker is not in the
        victim's gym.
        """
        self._both_gyms_none(attacker_pk=9)
        self.user_login('manager1')

        response = self.client.post(
            reverse('core:user:delete', kwargs={'user_pk': self.VICTIM_USER_PK}),
            {'password': 'manager1manager1'},
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.filter(pk=self.VICTIM_USER_PK).exists())

    def test_deactivate_blocked_when_both_gyms_none(self):
        self._both_gyms_none(attacker_pk=9)
        self.user_login('manager1')

        response = self.client.get(
            reverse('core:user:deactivate', kwargs={'pk': self.VICTIM_USER_PK})
        )
        self.assertEqual(response.status_code, 403)
        self.assertTrue(User.objects.get(pk=self.VICTIM_USER_PK).is_active)

    def test_activate_blocked_when_both_gyms_none(self):
        self._both_gyms_none(attacker_pk=9)
        victim = User.objects.get(pk=self.VICTIM_USER_PK)
        victim.is_active = False
        victim.save()
        self.user_login('manager1')

        response = self.client.get(
            reverse('core:user:activate', kwargs={'pk': self.VICTIM_USER_PK})
        )
        self.assertEqual(response.status_code, 403)
        self.assertFalse(User.objects.get(pk=self.VICTIM_USER_PK).is_active)


class TrainerLogoutTestCase(WgerTestCase):
    """
    Tests the trainer logout view (switching back to trainer ID)
    """

    def test_logout(self):
        """
        Test the trainer login as an anonymous user
        """
        self.user_login('admin')
        self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 2}))
        self.assertTrue(self.client.session.get('trainer.identity'))

        self.client.post(reverse('core:user:trainer-login', kwargs={'user_pk': 1}))
        self.assertFalse(self.client.session.get('trainer.identity'))
