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
        return self.client.post(self.url, payload, content_type='application/json')

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


class ChartConfigApiTestCase(WgerTestCase):
    """
    The per-category chart settings
    """

    # Pinned in test-measurement-categories.json
    category = 'cccccccc-cccc-cccc-cccc-000000000003'  # user 'test'

    def setUp(self):
        super().setUp()
        self.user_login('test')
        self.url = reverse('measurement-category-detail', kwargs={'pk': self.category})

    def patch_config(self, chart_config):
        return self.client.patch(
            self.url,
            {'chart_config': chart_config},
            content_type='application/json',
        )

    def test_defaults_to_an_empty_object(self):
        response = self.client.get(self.url)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['chart_config'], {})

    def test_roundtrip(self):
        """
        Test that the keys are stored as sent: they are client business
        """
        response = self.patch_config({'trend': 'sluggish', 'average_window': 14})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['chart_config'], {'trend': 'sluggish', 'average_window': 14})

    def test_unknown_keys_are_kept(self):
        """
        Test that a key this release knows nothing about is not dropped
        """
        response = self.patch_config({'goal_line': 75})

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Category.objects.get(pk=self.category).chart_config, {'goal_line': 75})

    def test_non_object_rejected(self):
        response = self.patch_config(['sluggish'])

        self.assertEqual(response.status_code, 400)
        self.assertIn('chart_config', response.data)

    def test_size_bound(self):
        """
        Test that the column cannot be used as a blob store
        """
        response = self.patch_config({'trend': 'x' * 1000})

        self.assertEqual(response.status_code, 400)
        self.assertIn('chart_config', response.data)


class TypedCategoryTestCase(WgerTestCase):
    """
    Identity and structural rules of the categories with a metric type
    """

    # Pinned in test-measurement-categories.json
    category_empty = 'cccccccc-cccc-cccc-cccc-000000000003'  # user 'test', no measurements

    def setUp(self):
        super().setUp()
        self.url = reverse('measurement-category-list')
        self.user_login('test')
        self.user = User.objects.get(username='test')

    def create_category(self, **data):
        payload = {'name': 'Steps', 'unit': 'count', **data}
        return self.client.post(self.url, payload, content_type='application/json')

    def detail_url(self, pk):
        return reverse('measurement-category-detail', kwargs={'pk': pk})

    def test_typed_category_gets_derived_id(self):
        """
        Test that the key of a typed category is derived from user and type
        """
        response = self.create_category(metric_type=MetricType.STEPS)

        self.assertEqual(response.status_code, 201)
        self.assertEqual(
            response.data['id'],
            str(Category.deterministic_id(self.user.pk, MetricType.STEPS)),
        )

    def test_official_category_keeps_random_id(self):
        """
        Test that the server-managed body weight category is not derived
        """
        category = Category.objects.get(user=self.user, is_official=True)

        self.assertNotEqual(
            category.pk,
            Category.deterministic_id(self.user.pk, MetricType.BODY_WEIGHT),
        )

    def test_second_typed_category_rejected(self):
        """
        Test that a metric type can only be used once per user
        """
        self.create_category(metric_type=MetricType.STEPS)

        response = self.create_category(name='Steps again', metric_type=MetricType.STEPS)

        self.assertEqual(response.status_code, 400)
        self.assertIn('metric_type', response.data)

    def test_same_type_of_other_user_allowed(self):
        """
        Test that the uniqueness is per user
        """
        Category.objects.create(
            user=User.objects.get(username='admin'),
            name='Steps',
            unit='count',
            metric_type=MetricType.STEPS,
        )

        response = self.create_category(metric_type=MetricType.STEPS)

        self.assertEqual(response.status_code, 201)

    def test_custom_categories_can_repeat(self):
        """
        Test that free-form categories are unaffected by the uniqueness
        """
        self.create_category(name='Biceps left', unit='cm')

        response = self.create_category(name='Biceps right', unit='cm')

        self.assertEqual(response.status_code, 201)

    def test_group_creates_components(self):
        """
        Test that a group category is created with its component children
        """
        response = self.create_category(
            name='Blood pressure',
            unit='mmHg',
            metric_type=MetricType.BLOOD_PRESSURE,
        )

        self.assertEqual(response.status_code, 201)
        children = Category.objects.filter(parent_id=response.data['id']).order_by('order')
        self.assertEqual(
            [(c.name, c.metric_type, c.unit) for c in children],
            [
                ('Systolic', MetricType.BLOOD_PRESSURE_SYSTOLIC, 'mmHg'),
                ('Diastolic', MetricType.BLOOD_PRESSURE_DIASTOLIC, 'mmHg'),
            ],
        )

    def test_free_form_category_cannot_be_typed(self):
        """
        Test that a metric type cannot be assigned to an existing category
        """
        response = self.client.patch(
            self.detail_url(self.category_empty),
            {'metric_type': MetricType.DISTANCE},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('metric_type', response.data)
        self.assertEqual(
            Category.objects.get(pk=self.category_empty).metric_type,
            MetricType.CUSTOM,
        )

    def test_typed_category_cannot_be_reset(self):
        """
        Test that a typed category cannot go back to being free-form
        """
        category = self.create_category(metric_type=MetricType.STEPS)

        response = self.client.patch(
            self.detail_url(category.data['id']),
            {'metric_type': MetricType.CUSTOM},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('metric_type', response.data)

    def test_group_cannot_change_its_type(self):
        """
        Test that a group keeps its type, and with it its components
        """
        group = self.create_category(
            name='Blood pressure',
            unit='mmHg',
            metric_type=MetricType.BLOOD_PRESSURE,
        )

        response = self.client.patch(
            self.detail_url(group.data['id']),
            {'metric_type': MetricType.SLEEP},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertEqual(Category.objects.filter(parent_id=group.data['id']).count(), 2)

    def test_unchanged_metric_type_accepted(self):
        """
        Test that an edit sending the type along is not read as a change
        """
        category = self.create_category(metric_type=MetricType.STEPS)

        response = self.client.patch(
            self.detail_url(category.data['id']),
            {'name': 'Schritte', 'metric_type': MetricType.STEPS},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)

    def test_component_without_group_rejected(self):
        """
        Test that a component category cannot be created on its own
        """
        response = self.create_category(
            name='Systolic',
            unit='mmHg',
            metric_type=MetricType.BLOOD_PRESSURE_SYSTOLIC,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('parent', response.data)

    def test_component_under_wrong_group_rejected(self):
        """
        Test that a component category only fits under its own group type
        """
        response = self.create_category(
            name='Systolic',
            unit='mmHg',
            metric_type=MetricType.BLOOD_PRESSURE_SYSTOLIC,
            parent=self.category_empty,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('parent', response.data)

    def test_typed_category_cannot_be_nested(self):
        """
        Test that a non-component metric type stays top-level
        """
        response = self.create_category(
            metric_type=MetricType.STEPS,
            parent=self.category_empty,
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('parent', response.data)

    def test_group_only_holds_its_own_components(self):
        """
        Test that a group does not take children other than its components
        """
        group = self.create_category(
            name='Blood pressure',
            unit='mmHg',
            metric_type=MetricType.BLOOD_PRESSURE,
        )

        response = self.create_category(
            name='Something else',
            unit='mmHg',
            parent=group.data['id'],
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('metric_type', response.data)


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

    def test_unit_of_body_weight_restricted(self):
        """
        Test that a body weight category only takes kg and lb as unit
        """
        response = self.client.patch(
            self.detail_url(self.official),
            {'unit': 'stone'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 400)
        self.assertIn('unit', response.data)
        self.assertEqual(Category.objects.get(pk=self.official).unit, 'kg')

    def test_unit_of_body_weight_switchable(self):
        """
        Test that the category can still be switched between kg and lb
        """
        response = self.client.patch(
            self.detail_url(self.official),
            {'unit': 'lb'},
            content_type='application/json',
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(Category.objects.get(pk=self.official).unit, 'lb')

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
