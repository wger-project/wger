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
from django.urls import reverse

# wger
from wger.core.tests import api_base_test
from wger.core.tests.base_testcase import WgerTestCase
from wger.measurements.models import Category


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
