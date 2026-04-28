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
from wger.core.tests.base_testcase import WgerTestCase
from wger.utils.constants import PAGINATION_OBJECTS_PER_PAGE


class IngredientOverviewTestCase(WgerTestCase):
    """
    Tests the ingredient overview
    """

    def test_overview_cursor_pagination(self):
        """
        The overview uses cursor pagination via ?after=<id>.
        """
        # Add more ingredients so we can test the pagination
        self.user_login('admin')
        data = {
            'name': 'Test ingredient',
            'language': 2,
            'sodium': 10.54,
            'energy': 176,
            'fat': 8.19,
            'carbohydrates_sugar': 0.0,
            'fat_saturated': 3.24,
            'fiber': 0.0,
            'protein': 25.63,
            'carbohydrates': 0.0,
            'license': 1,
            'license_author': 'internet',
        }
        for i in range(0, 50):
            self.client.post(reverse('nutrition:ingredient:add'), data)

        self.user_logout()
        url = reverse('nutrition:ingredient:list')

        # First page: full PAGE_SIZE, has_next, no previous, not paginated yet.
        response = self.client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ingredients_list']), PAGINATION_OBJECTS_PER_PAGE)
        self.assertTrue(response.context['has_next'])
        self.assertFalse(response.context['has_prev'])
        self.assertFalse(response.context['is_paginated'])
        self.assertIsNotNone(response.context['next_url'])
        self.assertIsNone(response.context['prev_url'])
        self.assertIn('after=', response.context['next_url'])

        # Walk the catalogue forward until exhausted by following next_url.
        seen_ids = []
        page_count = 0
        next_url = url
        while True:
            response = self.client.get(next_url)
            self.assertEqual(response.status_code, 200)
            seen_ids.extend(i.id for i in response.context['ingredients_list'])
            page_count += 1
            if not response.context['has_next']:
                break
            # next_url is relative ('?after=N&...'); join with the list path.
            next_url = url + response.context['next_url']

        # Every ingredient appears exactly once across the walk.
        self.assertEqual(len(seen_ids), len(set(seen_ids)))

        # Pages are at most PAGE_SIZE; with 50 created + the fixture rows we
        # should have at least 3 pages.
        self.assertGreaterEqual(page_count, 3)

        # An invalid cursor falls back to the first page (no 500, no 404).
        response = self.client.get(url, {'after': 'foobar'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['ingredients_list']), PAGINATION_OBJECTS_PER_PAGE)

        # A cursor past the end yields an empty page with no next link.
        response = self.client.get(url, {'after': 999_999_999})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['ingredients_list'], [])
        self.assertFalse(response.context['has_next'])
        self.assertIsNone(response.context['next_url'])

    def test_overview_backward_pagination(self):
        """`?before=<id>` walks backward through the catalogue."""

        self.user_login('admin')
        data = {
            'name': 'Test ingredient',
            'language': 2,
            'sodium': 10.54,
            'energy': 176,
            'fat': 8.19,
            'carbohydrates_sugar': 0.0,
            'fat_saturated': 3.24,
            'fiber': 0.0,
            'protein': 25.63,
            'carbohydrates': 0.0,
            'license': 1,
            'license_author': 'internet',
        }
        for i in range(0, 80):
            self.client.post(reverse('nutrition:ingredient:add'), data)

        self.user_logout()
        url = reverse('nutrition:ingredient:list')

        # Navigate forward two pages, then back via prev_url.
        page1 = self.client.get(url)
        page1_ids = [i.id for i in page1.context['ingredients_list']]

        page2 = self.client.get(url + page1.context['next_url'])
        page2_ids = [i.id for i in page2.context['ingredients_list']]

        # Page 2 must offer a "prev" link, since we've moved past page 1.
        self.assertTrue(page2.context['has_prev'])
        self.assertIsNotNone(page2.context['prev_url'])
        self.assertIn('before=', page2.context['prev_url'])

        # Going back from page 2 must yield exactly page 1.
        page1_again = self.client.get(url + page2.context['prev_url'])
        page1_again_ids = [i.id for i in page1_again.context['ingredients_list']]
        self.assertEqual(page1_again_ids, page1_ids)

        # On the (re)first page, prev disappears, next reappears.
        self.assertFalse(page1_again.context['has_prev'])
        self.assertTrue(page1_again.context['has_next'])

        # Going forward from there must take us back to page 2 again.
        page2_again = self.client.get(url + page1_again.context['next_url'])
        page2_again_ids = [i.id for i in page2_again.context['ingredients_list']]
        self.assertEqual(page2_again_ids, page2_ids)

        # An invalid `?before=` cursor falls back to the first page.
        response = self.client.get(url, {'before': 'foobar'})
        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.context['has_prev'])

        # `?before=<very small id>` yields an empty page with no prev link.
        response = self.client.get(url, {'before': 0})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['ingredients_list'], [])
        self.assertFalse(response.context['has_prev'])
        self.assertIsNone(response.context['prev_url'])

    def test_next_url_preserves_filter_params(self):
        """The next_url must keep filter parameters like ?is_vegan=1 attached."""
        self.user_login('admin')
        for i in range(0, 30):
            self.client.post(
                reverse('nutrition:ingredient:add'),
                {
                    'name': 'Vegan ingredient',
                    'language': 2,
                    'sodium': 10.54,
                    'energy': 176,
                    'fat': 8.19,
                    'carbohydrates_sugar': 0.0,
                    'fat_saturated': 3.24,
                    'fiber': 0.0,
                    'protein': 25.63,
                    'carbohydrates': 0.0,
                    'license': 1,
                    'license_author': 'internet',
                    'is_vegan': 'on',
                },
            )

        self.user_logout()
        response = self.client.get(reverse('nutrition:ingredient:list'), {'is_vegan': '1'})
        self.assertEqual(response.status_code, 200)

        if response.context['has_next']:
            self.assertIn('is_vegan=1', response.context['next_url'])
            self.assertIn('after=', response.context['next_url'])

    def ingredient_overview(self):
        """
        Helper function to test the ingredient overview page
        """

        # Page exists
        response = self.client.get(reverse('nutrition:ingredient:list'))
        self.assertEqual(response.status_code, 200)

    def test_ingredient_index_editor(self):
        """
        Tests the ingredient overview page as a logged-in user with editor rights
        """

        self.user_login('admin')
        self.ingredient_overview()

    def test_ingredient_index_non_editor(self):
        """
        Tests the overview page as a logged-in user without editor rights
        """

        self.user_login('test')
        self.ingredient_overview()

    def test_ingredient_index_demo_user(self):
        """
        Tests the overview page as a logged in demo user
        """

        self.user_login('demo')
        self.ingredient_overview()

    def test_ingredient_index_logged_out(self):
        """
        Tests the overview page as an anonymous (logged out) user
        """

        self.ingredient_overview()
