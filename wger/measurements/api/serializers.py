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

# Third Party
from rest_framework import serializers

# wger
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType


class CategorySerializer(serializers.ModelSerializer):
    """
    Measurement category serializer
    """

    class Meta:
        model = Category
        fields = ('id', 'name', 'unit', 'metric_type', 'parent', 'order', 'is_official')
        read_only_fields = ('is_official',)

    def validate_metric_type(self, metric_type):
        """
        The metric type of an official category is fixed: the legacy weight
        endpoint and the health sync rely on it
        """
        if self.instance and self.instance.is_official:
            if metric_type != self.instance.metric_type:
                raise serializers.ValidationError(
                    'The metric type of an official category cannot be changed'
                )
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

        # A group is a container. It never carries measurements, so a category
        # that has some cannot become one
        if MetricType.is_group(metric_type) and instance and instance.measurement_set.exists():
            raise serializers.ValidationError(
                {'metric_type': 'A category with measurements cannot become a group'}
            )

        self._validate_unique_metric_type(metric_type)
        return data

    def _validate_unique_metric_type(self, metric_type):
        """
        Only one category per metric type and user.

        The constraint carries a condition, for which DRF generates no validator
        of its own, so a duplicate would otherwise only surface as an
        IntegrityError when saving.
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
        A category that becomes a group gets its components
        """
        category = super().update(instance, validated_data)
        category.create_components()
        return category


class MeasurementSerializer(serializers.ModelSerializer):
    """
    Measurement serializer
    """

    # Manually set the serializer to set the coerce_to_string option
    value = serializers.DecimalField(
        max_digits=6,
        decimal_places=2,
        min_value=Decimal(0.0),
        max_value=Decimal(5000.0),
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
        The unit key holds the unit the value was entered in
        """
        if not isinstance(extra_data, dict):
            raise serializers.ValidationError('extra_data must be an object')
        return extra_data

    def validate(self, data):
        """
        Body weight entries only support the weight units of the user profile
        """
        category = data.get('category') or (self.instance.category if self.instance else None)
        extra_data = data.get('extra_data', self.instance.extra_data if self.instance else {})
        unit = extra_data.get('unit')

        if unit is not None and category is not None:
            if category.metric_type == MetricType.BODY_WEIGHT and unit not in ('kg', 'lb'):
                raise serializers.ValidationError(
                    {'extra_data': 'Body weight entries only support kg and lb as unit'}
                )
        return data
