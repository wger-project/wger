# This file is part of wger Workout Manager.
#
# wger is free software: you can redistribute it and/or modify
# it under the terms of the GNU Affero General Public License as published by
# the Free Software Foundation, either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public License
# along with Workout Manager.  If not, see <http://www.gnu.org/licenses/>.

# Standard Library
import time

# Django
from django.test import TestCase

# wger
from wger.utils.uuid import uuid7


class UUID7TestCase(TestCase):
    def test_version(self):
        """
        Check if the generated UUIDs have the correct version.
        """
        uuid_obj = uuid7()
        self.assertEqual(uuid_obj.version, 7)

    def test_monotonicity(self):
        """
        Check if the generated UUIDs are monotonic (increasing).
        """
        uuids = []
        for _ in range(10):
            uuids.append(uuid7())

            # Wait 5ms to ensure timestamp increases
            time.sleep(0.005)

        # Check values
        for i in range(len(uuids) - 1):
            self.assertLess(uuids[i], uuids[i + 1])

        # Check string representation sort order
        str_uuids = [str(u) for u in uuids]
        sorted_str_uuids = sorted(str_uuids)
        self.assertEqual(str_uuids, sorted_str_uuids)
