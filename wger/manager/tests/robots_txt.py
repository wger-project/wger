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

from django.core.urlresolvers import reverse

from django.contrib.auth.models import User

from wger.manager.tests.testcase import WorkoutManagerTestCase
from wger.exercises.models import Language


class RobotsTxtTestCase(WorkoutManagerTestCase):
    '''
    Tests the generated robots.txt
    '''

    def test_robots(self):

        response = self.client.get(reverse('robots'))
        for lang in Language.objects.all():
            self.assertTrue('wger.de/{0}/sitemap.xml'.format(lang.short_name) in response.content)
