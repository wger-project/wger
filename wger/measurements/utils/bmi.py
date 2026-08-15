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

# Standard Library
from decimal import Decimal


def calculate_bmi(user) -> list[dict]:
    """
    Returns one row per body weight entry: its date, the BMI it works out to
    and the id of the entry it derives from
    """
    # wger
    from wger.measurements.models import Measurement

    profile = user.userprofile
    if not profile.height or profile.height <= 0:
        return []

    height_sq = (Decimal(profile.height) / 100) ** 2

    return [
        {
            'source_id': entry.id,
            'date': entry.date,
            'value': round(entry.value_in('kg') / height_sq, 2),
        }
        for entry in Measurement.body_weight_for(user).order_by('date')
    ]
