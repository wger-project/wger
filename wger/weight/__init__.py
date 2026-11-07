# -*- coding: utf-8 -*-

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

"""
Compatibility surface for body weight, which lives in wger.measurements.

No models of its own since 2.7: a body weight is a Measurement in the category
with metric_type=body_weight. What is left here is the surface that was public
before the merge plus the migration history that keeps the app in
INSTALLED_APPS. New body weight features belong in wger.measurements.
"""

# wger
from wger.version import get_version


VERSION = get_version()
