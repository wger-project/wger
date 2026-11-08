#  This file is part of wger Workout Manager <https://github.com/wger-project>.
#
#  wger Workout Manager is free software: you can redistribute it and/or modify
#  it under the terms of the GNU Affero General Public License as published by
#  the Free Software Foundation, either version 3 of the License, or
#  (at your option) any later version.
#
#  wger Workout Manager is distributed in the hope that it will be useful,
#  but WITHOUT ANY WARRANTY; without even the implied warranty of
#  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#  GNU Affero General Public License for more details.
#
#  You should have received a copy of the GNU Affero General Public License
#  along with this program.  If not, see <http://www.gnu.org/licenses/>.

"""
One-rep max (1RM) estimates, shared by the routine statistics, the calculated
measurement categories and the personal record trophy
"""

# Standard Library
from decimal import Decimal

# wger
from wger.manager.consts import (
    REP_UNIT_REPETITIONS,
    WEIGHT_UNIT_KG,
    WEIGHT_UNIT_LB,
)
from wger.utils.units import AbstractWeight


def brzycki(weight: Decimal | int, reps: Decimal | int) -> Decimal | None:
    """
    Brzycki estimate of the 1RM: weight * 36 / (37 - reps).

    None outside 1 <= reps < 37, where the formula has no meaning.
    """
    reps = Decimal(reps)
    if reps < 1 or reps >= 37:
        return None

    return Decimal(weight) * Decimal(36) / (Decimal(37) - reps)


def brzycki_intensity(weight: Decimal, reps: Decimal) -> Decimal | None:
    """Weight relative to the Brzycki 1RM, None where the formula has no meaning"""
    one_rm = brzycki(weight, reps)
    if one_rm is None:
        return None
    return weight / one_rm if one_rm != 0 else Decimal(0)


def estimate_from_log(
    log,
    *,
    max_reps: int | None = None,
    unit: int = WEIGHT_UNIT_KG,
) -> Decimal | None:
    """
    1RM estimate of a single set in the given weight unit, or None if the set
    doesn't qualify.

    Qualifying means: counted in repetitions, 1 to max_reps logged repetitions
    (if a cap is given), a weight over zero in kg or lb. The reps in reserve
    count as repetitions the set could still have done.
    """
    weight = log.weight
    reps = log.repetitions

    if weight is None or reps is None or weight <= 0 or reps < 1:
        return None
    if log.repetitions_unit_id != REP_UNIT_REPETITIONS:
        return None
    if log.weight_unit_id not in (WEIGHT_UNIT_KG, WEIGHT_UNIT_LB):
        return None
    if max_reps is not None and reps > max_reps:
        return None

    if log.weight_unit_id != unit:
        converted = AbstractWeight(weight, 'lb' if log.weight_unit_id == WEIGHT_UNIT_LB else 'kg')
        weight = converted.kg if unit == WEIGHT_UNIT_KG else converted.lb

    return brzycki(weight, reps + (log.rir or 0))
