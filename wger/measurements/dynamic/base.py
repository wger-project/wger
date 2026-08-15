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
import datetime
import uuid
from collections.abc import Callable
from dataclasses import (
    dataclass,
    field,
)
from decimal import Decimal

# Django
from django.db import models


@dataclass(frozen=True)
class Dependency:
    """
    One source model a calculated type derives its values from.

    ``user_id`` resolves a changed instance to the owner whose calculated
    categories need a recompute, ``when`` filters out instances the type does
    not care about.
    """

    model: type[models.Model]
    user_id: Callable[[models.Model], int | None]
    when: Callable[[models.Model], bool] = lambda instance: True


@dataclass(frozen=True)
class DesiredRow:
    """
    One entry a calculated category should hold. The external_id is the
    idempotency key the engine diffs on, see the unique constraint on
    (category, source, external_id).
    """

    external_id: uuid.UUID
    date: datetime.datetime
    value: Decimal
    extra_data: dict = field(default_factory=dict)


class DynamicMeasurementType:
    """
    A calculated category type.

    Subclasses provide the math (``compute``), the models it depends on
    (``depends_on``) and the schema of its configuration
    (``params_schema``). Everything else, the triggers, the backfill and the
    reconciliation, is engine code shared by all types.
    """

    slug: str
    label: str
    params_schema: dict = {'type': 'object', 'additionalProperties': False}
    depends_on: list[Dependency] = []

    def compute(self, category) -> list[DesiredRow]:
        """
        Returns the full desired state of the category; the engine diffs it
        against the stored rows
        """
        raise NotImplementedError


_registry: dict[str, DynamicMeasurementType] = {}


def register(cls: type[DynamicMeasurementType]) -> type[DynamicMeasurementType]:
    _registry[cls.slug] = cls()
    return cls


def get_type(slug: str) -> DynamicMeasurementType | None:
    return _registry.get(slug)


def all_types() -> list[DynamicMeasurementType]:
    return list(_registry.values())


def source_models() -> set[type[models.Model]]:
    """
    Every model at least one registered type depends on; the signal wiring
    connects one receiver per entry
    """
    return {dep.model for calc in _registry.values() for dep in calc.depends_on}
