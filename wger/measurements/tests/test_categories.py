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
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.
# Django
from django.contrib.auth.models import User
from django.urls import reverse

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.measurements.models import Category
from wger.measurements.models.category import MetricType


class UnitApiTestCase(api_base_test.ApiBaseResourceTestCase):
    """
    Tests the measurement units endpoint
    """

    pk = 'cccccccc-cccc-cccc-cccc-000000000001'
    resource = Category
    private_resource = True
    data = {
        'name': 'Legs',
        'unit': 'cm',
    }

    def get_resource_name(self):
        return 'measurement-category'


class CategoryGroupApiTestCase(WgerTestCase):
    """
    Structural rules for multi-value groups (parent/child categories)
    """

    # Pinned in test-measurement-categories.json / test-measurements.json
    category_empty = 'cccccccc-cccc-cccc-cccc-000000000003'  # user 'test', no measurements
    category_with_measurements = 'cccccccc-cccc-cccc-cccc-000000000001'  # user 'test'
    category_other_user = 'cccccccc-cccc-cccc-cccc-0000000000aa'  # user 'admin'

    def setUp(self):
        super().setUp()
        self.url = reverse('measurement-category-list')
        self.user_login('test')

    def create_category(self, **data):
        payload = {'name': 'Systolic', 'unit': 'mmHg', **data}
        return self.client.post(self.url, payload)

    def detail_url(self, pk):
        return reverse('measurement-category-detail', kwargs={'pk': pk})

    def test_create_child(self):
        response = self.create_category(parent=self.category_empty)

        self.assertEqual(response.status_code, 201)
        category = Category.objects.get(pk=response.data['id'])
        self.assertEqual(str(category.parent_id), self.category_empty)

    def test_parent_of_other_user_rejected(self):
        response = self.create_category(parent=self.category_other_user)

        self.assertEqual(response.status_code, 403)

    def test_nesting_limited_to_one_level(self):
        child = self.create_category(parent=self.category_empty)

        response = self.create_category(name='Grandchild', parent=child.data['id'])

        self.assertEqual(response.status_code, 400)
        self.assertIn('parent', response.data)

    def test_own_parent_rejected(self):
        response = self.client.patch(
            self.detail_url(self.category_empty),
            {'parent': self.category_empty},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('parent', response.data)

    def test_parent_with_measurements_rejected(self):
        response = self.create_category(parent=self.category_with_measurements)

        self.assertEqual(response.status_code, 400)
        self.assertIn('parent', response.data)

    def test_category_with_children_cannot_be_nested(self):
        self.create_category(parent=self.category_empty)
        group = self.create_category(name='Another group')

        response = self.client.patch(
            self.detail_url(self.category_empty),
            {'parent': group.data['id']},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('parent', response.data)

    def test_deleting_parent_deletes_children(self):
        child = self.create_category(parent=self.category_empty)

        response = self.client.delete(self.detail_url(self.category_empty))

        self.assertEqual(response.status_code, 204)
        self.assertFalse(Category.objects.filter(pk=child.data['id']).exists())


class OfficialCategoryTestCase(WgerTestCase):
    """
    Automatic creation and protection of official categories
    """

    # Pinned in test-measurement-categories.json
    official = 'cccccccc-cccc-cccc-cccc-0000000000b0'  # user 'test'
    custom = 'cccccccc-cccc-cccc-cccc-000000000003'  # user 'test'

    def setUp(self):
        super().setUp()
        self.user_login('test')

    def detail_url(self, pk):
        return reverse('measurement-category-detail', kwargs={'pk': pk})

    def test_new_user_gets_official_category(self):
        """
        Test that creating a user creates the official body weight category
        """
        user = User.objects.create_user('fresh-user', password='123')

        category = Category.objects.get(user=user, is_official=True)
        self.assertEqual(category.metric_type, MetricType.BODY_WEIGHT)
        self.assertEqual(category.unit, user.userprofile.weight_unit)

    def test_delete_official_forbidden(self):
        """
        Test that the official category cannot be deleted over the API
        """
        response = self.client.delete(self.detail_url(self.official))

        self.assertEqual(response.status_code, 403)
        self.assertTrue(Category.objects.filter(pk=self.official).exists())

    def test_delete_custom_allowed(self):
        """
        Test that custom categories can still be deleted
        """
        response = self.client.delete(self.detail_url(self.custom))

        self.assertEqual(response.status_code, 204)

    def test_metric_type_of_official_fixed(self):
        """
        Test that the metric type of an official category cannot be changed
        """
        response = self.client.patch(
            self.detail_url(self.official),
            {'metric_type': 'custom'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('metric_type', response.data)

    def test_rename_official_allowed(self):
        """
        Test that the official category can still be renamed
        """
        response = self.client.patch(
            self.detail_url(self.official),
            {'name': 'Körpergewicht'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)

    def test_is_official_read_only(self):
        """
        Test that the official flag cannot be set over the API
        """
        response = self.client.patch(
            self.detail_url(self.custom),
            {'is_official': True},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(Category.objects.get(pk=self.custom).is_official)

    def test_filter_by_is_official(self):
        """
        Test that the category list can be filtered by the official flag
        """
        response = self.client.get(reverse('measurement-category-list'), {'is_official': True})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 1)
        self.assertEqual(response.data['results'][0]['id'], self.official)
