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
from django.urls import reverse

# wger
from wger.core.tests.base_testcase import WgerTestCase


class SitemapTestCase(WgerTestCase):
    """
    Tests the generated sitemap
    """

    def test_sitemap_index(self):

        response = self.client.get(reverse('sitemap'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['sitemaps']), 2)

    def test_sitemap_exercises(self):

        response = self.client.get(reverse('django.contrib.sitemaps.views.sitemap',
                                           kwargs={'section': 'exercises'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['urlset']), 9)

    def test_sitemap_ingredients(self):

        response = self.client.get(reverse('django.contrib.sitemaps.views.sitemap',
                                           kwargs={'section': 'nutrition'}))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['urlset']), 13)
