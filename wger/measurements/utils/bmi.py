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


def calculate_bmi(user, category_id):
    # wger
    from wger.weight.models import WeightEntry

    profile = getattr(user, 'userprofile', None)
    if not profile or not profile.height or profile.height <= 0:
        return []

    # height_sq will be a float
    height_sq = (profile.height / 100) ** 2

    weights = WeightEntry.objects.filter(user=user).order_by('date')

    return [
        {
            'id': w.id,  # Use integer IDs so the frontend state manager doesn't complain
            'category': int(category_id),  # Link it to the requested category
            'date': w.date.isoformat() if hasattr(w.date, 'isoformat') else w.date,
            'value': round(float(w.weight) / height_sq, 2),
            'notes': 'Auto-calculated from weight entry',
        }
        for w in weights
    ]
