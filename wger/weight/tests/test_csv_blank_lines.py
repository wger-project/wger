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

# Standard Library
from types import SimpleNamespace

# Django
from django.contrib.auth.models import User

# wger
from wger.core.tests.base_testcase import WgerTestCase
from wger.weight.helpers import parse_weight_csv


class WeightCsvBlankLinesTestCase(WgerTestCase):
    """
    Test that blank lines in the CSV are not reported as errors
    """

    def test_blank_lines_are_ignored(self):
        request = SimpleNamespace(user=User.objects.get(username='test'))
        weights, errors = parse_weight_csv(
            request,
            {'csv_input': '2031-01-01,80\n\n2031-01-02,81\n', 'date_format': '%Y-%m-%d'},
        )

        self.assertEqual(len(weights), 2)
        self.assertEqual(errors, [])
