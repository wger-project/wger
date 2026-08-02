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
from typing import NamedTuple

# wger
from wger.measurements.models.category import MetricType


VALUE_MAX_DIGITS = 8
VALUE_DECIMAL_PLACES = 2

SCHEMA_MAX_VALUE = Decimal(10) ** (VALUE_MAX_DIGITS - VALUE_DECIMAL_PLACES) - Decimal('0.01')
"""
Largest value the column can hold. It is what a category without a metric type
is bounded by, since nothing about a free-form category says more.
"""


class Limits(NamedTuple):
    """
    The range a measurement value of one metric type may be in.

    ``min``/``max`` are enforced by the API, a value outside them is a 400.
    ``soft_min``/``soft_max`` are the everyday range: they are meant for
    warnings and chart axes in the clients and are never enforced anywhere.
    """

    min: Decimal
    max: Decimal
    soft_min: Decimal | None = None
    soft_max: Decimal | None = None


# Body weight is the only metric whose values come in more than one unit, so it
# is also the only one whose bounds are per unit (see wger-project/wger#1019,
# where a single 300 kg cap locked out everyone entering pounds)
_BODY_WEIGHT_KG = Limits(Decimal(20), Decimal(350), Decimal(30), Decimal(300))
_SLEEP_STAGE = Limits(Decimal(0), Decimal(1440), Decimal(0), Decimal(720))

METRIC_LIMITS: dict[str, dict[str | None, Limits]] = {
    MetricType.BODY_WEIGHT: {
        'kg': _BODY_WEIGHT_KG,
        'lb': Limits(Decimal(44), Decimal(770), Decimal(66), Decimal(661)),
        None: _BODY_WEIGHT_KG,
    },
    MetricType.BODY_FAT: {None: Limits(Decimal(2), Decimal(60), Decimal(5), Decimal(50))},
    MetricType.HEIGHT: {None: Limits(Decimal(50), Decimal(250), Decimal(140), Decimal(210))},
    MetricType.BLOOD_PRESSURE_SYSTOLIC: {
        None: Limits(Decimal(50), Decimal(250), Decimal(90), Decimal(180)),
    },
    MetricType.BLOOD_PRESSURE_DIASTOLIC: {
        None: Limits(Decimal(30), Decimal(150), Decimal(50), Decimal(110)),
    },
    MetricType.HEART_RATE: {None: Limits(Decimal(30), Decimal(250), Decimal(40), Decimal(200))},
    MetricType.RESTING_HEART_RATE: {
        None: Limits(Decimal(30), Decimal(120), Decimal(40), Decimal(100)),
    },
    # The cumulative types hold a whole day, and a rest day really is 0 steps
    MetricType.STEPS: {None: Limits(Decimal(0), Decimal(100000), Decimal(0), Decimal(30000))},
    MetricType.DISTANCE: {None: Limits(Decimal(0), Decimal(500), Decimal(0), Decimal(30))},
    MetricType.ENERGY: {None: Limits(Decimal(0), Decimal(10000), Decimal(0), Decimal(2000))},
    # Sleep is stored in minutes, so the upper bound is not a rarity but
    # arithmetic: a day has 1440 of them
    MetricType.SLEEP_TOTAL: {None: Limits(Decimal(0), Decimal(1440), Decimal(180), Decimal(720))},
    MetricType.SLEEP_LIGHT: {None: _SLEEP_STAGE},
    MetricType.SLEEP_DEEP: {None: _SLEEP_STAGE},
    MetricType.SLEEP_REM: {None: _SLEEP_STAGE},
    MetricType.SLEEP_AWAKE: {None: _SLEEP_STAGE},
}
"""
The bounds per metric type, in the unit the type is stored in.

A hard bound answers "beyond this it is almost certainly a typo", not "no human
could reach this": they start low deliberately, because the direction we may
have to correct them in later is wider, and widening is the safe one. Tightening
a bound after the release is not: a client that still knows the old, wider one
would write values the server then rejects permanently, which in the offline
sync path is silent data loss.

The clients mirror this table (flutter ``MetricType.limits``, react
``limitsFor``), so a change here needs a change there.
"""

DEFAULT_LIMITS = Limits(Decimal(0), SCHEMA_MAX_VALUE)


def limits_for(metric_type: str, unit: str | None = None) -> Limits:
    """
    Returns the bounds a value in a category of this metric type must be in.

    Types without an entry fall back to the technical cap of the column: the
    free-form categories, which have no semantics to derive a bound from, and
    the group containers, which carry no measurements at all.
    """
    per_unit = METRIC_LIMITS.get(metric_type)
    if per_unit is None:
        return DEFAULT_LIMITS

    return per_unit.get(unit) or per_unit[None]
