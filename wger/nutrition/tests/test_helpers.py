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
from django.test import SimpleTestCase

# wger
from wger.nutrition.helpers import (
    change_html_entities_to_human_readable,
    remove_problematic_characters,
)


class HelperFunctionsTestCase(SimpleTestCase):
    def test_change_html_entities_to_human_readable(self):
        string = 'Proper Corn Sweet &amp; Salty'
        result = change_html_entities_to_human_readable(string)
        correct_result = 'Proper Corn Sweet & Salty'
        self.assertEqual(result, correct_result)

        string = 'Stonebaked Pizza &quot;the american pepperoni&quot;'
        result = change_html_entities_to_human_readable(string)
        correct_result = 'Stonebaked Pizza "the american pepperoni"'
        self.assertEqual(result, correct_result)

        string = 'Van Houten VH10 Kakao &#40;12,1&#37;&#41; 1KG'
        result = change_html_entities_to_human_readable(string)
        correct_result = 'Van Houten VH10 Kakao (12,1%) 1KG'
        self.assertEqual(result, correct_result)

        string = 'String with not existing html entitiy &#999;'
        result = change_html_entities_to_human_readable(string)
        correct_result = 'String with not existing html entitiy &#999;'
        self.assertEqual(result, correct_result)

    def test_remove_problematic_characters(self):
        string = 'Danone Danette Mousse Liégeoise Schokolade 2x(2x80g) 320g'
        result = remove_problematic_characters(string)
        correct_result = 'Danone Danette Mousse Liégeoise Schokolade 2x(2x80g) 320g'
        self.assertEqual(result, correct_result)

        string = "POM'POTES Compotes Gourdes BIO Pomme Framboise 4x90g"
        result = remove_problematic_characters(string)
        correct_result = "POM'POTES Compotes Gourdes BIO Pomme Framboise 4x90g"
        self.assertEqual(result, correct_result)

        string = 'String with \x9a control characters \t \x85'
        result = remove_problematic_characters(string)
        correct_result = 'String with  control characters  '
        self.assertEqual(result, correct_result)
