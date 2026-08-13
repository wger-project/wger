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
import json
from decimal import Decimal

# Third Party
from rest_framework import serializers

# wger
from wger.measurements.limits import (
    CHART_CONFIG_MAX_BYTES,
    EXTRA_DATA_MAX_BYTES,
    VALUE_DECIMAL_PLACES,
    VALUE_MAX_DIGITS,
    limits_for,
)
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import (
    BODY_WEIGHT_UNITS,
    MetricType,
)


def validate_json_object(value, field: str, max_bytes: int):
    """
    Refuses anything that is not an object, or whose compact serialization
    (what the column stores) is larger than ``max_bytes``
    """
    if not isinstance(value, dict):
        raise serializers.ValidationError(f'{field} must be an object')

    size = len(json.dumps(value, separators=(',', ':'), ensure_ascii=False).encode())
    if size > max_bytes:
        raise serializers.ValidationError(f'{field} must be at most {max_bytes} bytes, got {size}')
    return value


class CategorySerializer(serializers.ModelSerializer):
    """
    Measurement category serializer
    """

    class Meta:
        model = Category
        fields = (
            'id',
            'name',
            'unit',
            'metric_type',
            'chart_type',
            'chart_config',
            'parent',
            'order',
            'is_official',
        )
        read_only_fields = ('is_official',)

    def validate_chart_config(self, chart_config):
        """
        Only the shape is the server's business, the keys are the clients'
        """
        return validate_json_object(chart_config, 'chart_config', CHART_CONFIG_MAX_BYTES)

    def validate_metric_type(self, metric_type):
        """
        The metric type is fixed once the category exists: the key of a typed
        one is derived from it (Category.deterministic_id). Assigning a type to
        an existing category is a move, not a change of this field
        """
        if self.instance and metric_type != self.instance.metric_type:
            raise serializers.ValidationError('The metric type of a category cannot be changed')
        return metric_type

    def validate_parent(self, parent):
        """
        Enforce the structural rules for multi-value groups: one level of
        nesting, no cycles, and parents stay measurement-free.
        """
        if parent is None:
            return parent

        if self.instance:
            if parent.pk == self.instance.pk:
                raise serializers.ValidationError('A category cannot be its own parent')

            if self.instance.children.exists():
                raise serializers.ValidationError(
                    'A category with subcategories cannot itself have a parent'
                )

        if parent.parent_id is not None:
            raise serializers.ValidationError('Categories can only be nested one level deep')

        if parent.measurement_set.exists():
            raise serializers.ValidationError(
                'A category with measurements cannot be used as a parent'
            )

        return parent

    def validate(self, data):
        """
        Structural rules of the typed categories.

        Each metric type has one role: components live under the group they
        belong to, every other typed category is top-level, and there is exactly
        one category per type and user (see Category.deterministic_id).
        """
        instance = self.instance
        metric_type = data.get(
            'metric_type',
            instance.metric_type if instance else MetricType.CUSTOM,
        )
        parent = data.get('parent', instance.parent if instance else None)

        if MetricType.is_component(metric_type):
            group = MetricType.group_of(metric_type)
            if parent is None or parent.metric_type != group:
                raise serializers.ValidationError(
                    {'parent': f'A {metric_type} category must be part of a {group} group'}
                )
        elif metric_type != MetricType.CUSTOM and parent is not None:
            raise serializers.ValidationError(
                {'parent': f'A {metric_type} category cannot be nested'}
            )

        if parent is not None and MetricType.is_group(parent.metric_type):
            allowed = [c for c, _ in MetricType.components_of(parent.metric_type)]
            if metric_type not in allowed:
                raise serializers.ValidationError(
                    {'metric_type': f'A {parent.metric_type} group only holds its own components'}
                )

        # Body weight is read through Measurement.value_in(), which converts
        # between kg and lb and knows no third unit
        if metric_type == MetricType.BODY_WEIGHT:
            unit = data.get('unit', instance.unit if instance else None)
            if unit not in BODY_WEIGHT_UNITS:
                raise serializers.ValidationError(
                    {'unit': 'Body weight categories only support kg and lb as unit'}
                )

        self._validate_unique_metric_type(metric_type)
        return data

    def _validate_unique_metric_type(self, metric_type):
        """
        Only one category per metric type and user.

        DRF generates a validator for a UniqueConstraint only when the
        serializer maps every field of it. The owner is not part of the payload
        (it is passed to save() by the viewset and the PowerSync handler), so
        this constraint is skipped and a duplicate would otherwise only surface
        as an IntegrityError when saving.
        """
        user_id = self._get_user_id()
        if metric_type == MetricType.CUSTOM or user_id is None:
            return

        categories = Category.objects.filter(user_id=user_id, metric_type=metric_type)
        if self.instance is not None:
            categories = categories.exclude(pk=self.instance.pk)
        if categories.exists():
            raise serializers.ValidationError(
                {'metric_type': f'You already have a {metric_type} category'}
            )

    def _get_user_id(self):
        """
        Returns the id of the user the category belongs to.

        The owner is not part of the payload, it is passed to save() by the
        viewset (as a request) or by the PowerSync handler (as a context value).
        """
        user_id = self.context.get('user_id')
        if user_id is not None:
            return user_id

        request = self.context.get('request')
        user = getattr(request, 'user', None) if request else None
        return user.pk if user is not None and user.is_authenticated else None

    def create(self, validated_data):
        """
        Derives the key of a typed category and fills a group with components
        """
        metric_type = validated_data.get('metric_type', MetricType.CUSTOM)
        user_id = validated_data.get('user_id') or getattr(validated_data.get('user'), 'pk', None)

        # A client that creates the category offline derives the same key, so
        # only fill it in when the payload brought none of its own
        if 'id' not in validated_data and Category.has_deterministic_id(metric_type) and user_id:
            validated_data['id'] = Category.deterministic_id(user_id, metric_type)

        category = super().create(validated_data)
        category.create_components()
        return category

    def update(self, instance, validated_data):
        """
        Fills in the components a group is missing
        """
        category = super().update(instance, validated_data)
        category.create_components()
        return category


class MeasurementSerializer(serializers.ModelSerializer):
    """
    Measurement serializer
    """

    # Manually set the serializer to set the coerce_to_string option. The upper
    # bound is the technical cap of the column, what a value may actually be is
    # decided by the metric type of its category, see validate()
    value = serializers.DecimalField(
        max_digits=VALUE_MAX_DIGITS,
        decimal_places=VALUE_DECIMAL_PLACES,
        min_value=Decimal(0),
        coerce_to_string=False,
    )

    class Meta:
        model = Measurement
        fields = (
            'id',
            'category',
            'date',
            'value',
            'notes',
            'source',
            'external_id',
            'extra_data',
        )

    def validate_category(self, category):
        """
        Only leaf categories carry measurements; group parents are containers
        """
        if category.children.exists():
            raise serializers.ValidationError(
                'Measurements cannot be added to a category with subcategories'
            )
        # A group type is a container by definition, also while it still has no
        # children: its readings belong in the component categories
        if MetricType.is_group(category.metric_type):
            raise serializers.ValidationError(
                f'Measurements cannot be added to a {category.metric_type} category, '
                f'they belong in its components'
            )
        return category

    def validate_extra_data(self, extra_data):
        """
        The unit key holds the unit the value was entered in, min and max the
        range a daily aggregate summarises.

        Those two have to be numbers: the chart aggregate casts them to a
        decimal in SQL, and Postgres refuses to cast a JSON string, even a
        numeric one. A single entry written with `"48"` would take down every
        chart read of its category. Booleans are rejected as well, `bool` is a
        subclass of `int` but stored as `true`, which no cast accepts either.
        """
        validate_json_object(extra_data, 'extra_data', EXTRA_DATA_MAX_BYTES)

        for key in ('min', 'max'):
            value = (extra_data or {}).get(key)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, (int, float))
            ):
                raise serializers.ValidationError(
                    f'The {key} of an aggregate has to be a number, not {type(value).__name__}'
                )

        return extra_data

    def validate(self, data):
        """
        The unit and the range of the value both depend on the metric type
        """
        category = data.get('category') or (self.instance.category if self.instance else None)
        extra_data = data.get('extra_data', self.instance.extra_data if self.instance else {})
        unit = extra_data.get('unit')

        # Checked whenever the payload restamps the unit or moves the entry
        # into another category; a unit already stored must not block an
        # unrelated edit
        touches_unit = 'extra_data' in data or 'category' in data
        if touches_unit and unit is not None and category is not None:
            if category.metric_type == MetricType.BODY_WEIGHT and unit not in BODY_WEIGHT_UNITS:
                raise serializers.ValidationError(
                    {'extra_data': 'Body weight entries only support kg and lb as unit'}
                )

        self._validate_value_range(data, category, unit)
        return data

    def _validate_value_range(self, data, category, unit):
        """
        A value has to be in the range its metric type allows.

        The bound hangs off the category the entry lands in, so it is checked
        here rather than on the field: the same endpoint takes body weights in
        kilograms and daily step counts. Since a category can hold mixed units,
        the entry's own unit decides which of them applies.

        A stored value is only re-checked when the payload moves the entry under
        a different bound, by changing its category or its unit: entries
        predating the limits exist, and re-checking a stored value on every
        update would block all other edits to them.
        """
        if category is None:
            return

        limits = limits_for(category.metric_type, unit or category.unit)

        value = data.get('value')
        if value is None:
            if self.instance is None or limits == self._stored_limits():
                return
            value = self.instance.value

        if not limits.min <= value <= limits.max:
            raise serializers.ValidationError(
                {'value': f'Value must be between {limits.min} and {limits.max}'}
            )

    def _stored_limits(self):
        """
        The bounds that applied to the entry before the update
        """
        category = self.instance.category
        unit = (self.instance.extra_data or {}).get('unit')
        return limits_for(category.metric_type, unit or category.unit)


class BucketSerializer(serializers.Serializer):
    """
    One calendar bucket of a category's entries, see `api.aggregates`.

    Read-only: buckets are derived, there is nothing to write back.
    """

    category = serializers.UUIDField(read_only=True)
    start = serializers.DateTimeField(read_only=True)
    unit = serializers.CharField(read_only=True, allow_null=True)
    count = serializers.IntegerField(read_only=True)
    sum = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    min = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)
    max = serializers.DecimalField(read_only=True, max_digits=10, decimal_places=2)


class ValueCountSerializer(serializers.Serializer):
    """
    How often one value occurred, and when it was measured last. Read-only for
    the same reason as `BucketSerializer`.
    """

    category = serializers.UUIDField(read_only=True)
    value = serializers.DecimalField(read_only=True, max_digits=8, decimal_places=2)
    unit = serializers.CharField(read_only=True, allow_null=True)
    count = serializers.IntegerField(read_only=True)
    newest = serializers.DateTimeField(read_only=True)
