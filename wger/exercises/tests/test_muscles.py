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
from django.core.cache import cache
from django.core.cache.utils import make_template_fragment_key
from django.urls import reverse

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import (
    WgerAccessTestCase,
    WgerAddTestCase,
    WgerDeleteTestCase,
    WgerEditTestCase,
    WgerTestCase
)
from wger.exercises.models import Muscle


class MuscleRepresentationTestCase(WgerTestCase):
    """
    Test the representation of a model
    """

    def test_representation(self):
        """
        Test that the representation of an object is correct
        """
        self.assertEqual("{0}".format(Muscle.objects.get(pk=1)), 'Anterior testoid')

        # Check image URL properties
        self.assertIn("images/muscles/main/muscle-2.svg",
                      Muscle.objects.get(pk=2).image_url_main)
        self.assertIn("images/muscles/secondary/muscle-1.svg",
                      Muscle.objects.get(pk=1).image_url_secondary)


class MuscleAdminOverviewTest(WgerAccessTestCase):
    """
    Tests the admin muscle overview page
    """
    url = 'exercise:muscle:admin-list'
    anonymous_fail = True
    user_success = 'admin'
    user_fail = ('manager1',
                 'manager2'
                 'general_manager1',
                 'manager3',
                 'manager4',
                 'test',
                 'member1',
                 'member2',
                 'member3',
                 'member4',
                 'member5')


class MusclesShareButtonTestCase(WgerTestCase):
    """
    Test that the share button is correctly displayed and hidden
    """

    def test_share_button(self):
        url = reverse('exercise:muscle:overview')

        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('admin')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])

        self.user_login('test')
        response = self.client.get(url)
        self.assertTrue(response.context['show_shariff'])


class AddMuscleTestCase(WgerAddTestCase):
    """
    Tests adding a muscle
    """

    object_class = Muscle
    url = 'exercise:muscle:add'
    data = {'name': 'A new muscle',
            'is_front': True}


class EditMuscleTestCase(WgerEditTestCase):
    """
    Tests editing a muscle
    """

    object_class = Muscle
    url = 'exercise:muscle:edit'
    pk = 1
    data = {'name': 'The new name',
            'is_front': True}


class DeleteMuscleTestCase(WgerDeleteTestCase):
    """
    Tests deleting a muscle
    """

    object_class = Muscle
    url = 'exercise:muscle:delete'
    pk = 1


class MuscleCacheTestCase(WgerTestCase):
    """
    Muscle cache test case
    """

    def test_overview(self):
        """
        Test the muscle overview cache is correctly generated on visit
        """

        self.assertFalse(cache.get(make_template_fragment_key('muscle-overview', [2])))
        self.client.get(reverse('exercise:muscle:overview'))
        self.assertTrue(cache.get(make_template_fragment_key('muscle-overview', [2])))


class MuscleOverviewTestCase(WgerAccessTestCase):
    """
    Test that only admins see the edit links
    """
    url = 'exercise:muscle:overview'
    anonymous_fail = False
    user_fail = []


class MuscleApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the muscle overview resource
    """
    pk = 1
    resource = Muscle
    private_resource = False
    data = {'name': 'The name',
            'is_front': True}

    def test_get_detail(self):
        super().test_get_detail()

        # Check that image URLs are present in response
        response = self.client.get(self.url_detail)
        response_object = response.json()
        self.assertIn("images/muscles/main/muscle-1.svg",
                      response_object["image_url_main"])
        self.assertIn("images/muscles/secondary/muscle-1.svg",
                      response_object["image_url_secondary"])
