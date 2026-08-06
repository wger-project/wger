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
Condensing measurements into what a chart draws.

A chart shows a few hundred points and a watch-fed metric holds tens of
thousands a year, so the condensing belongs in the query rather than in the
client. The flutter app does the same thing against its local SQLite; this is
the same ladder and the same bucket semantics for the clients without one.
"""

# Standard Library
from zoneinfo import (
    ZoneInfo,
    ZoneInfoNotFoundError,
)

# Django
from django.db.models import (
    Count,
    DecimalField,
    F,
    Max,
    Min,
    Sum,
)
from django.db.models.functions import (
    Cast,
    Coalesce,
    TruncDay,
    TruncHour,
    TruncMonth,
    TruncWeek,
)


#: Points a chart is condensed to. Mirrors `measurementChartMaxPoints` in the
#: flutter app, and both clients may pass their own.
DEFAULT_MAX_POINTS = 200

#: Calendar units entries are condensed into, finest first. Not equal slices of
#: the span: these metrics have a daily rhythm, so slices that do not line up
#: with a day each catch a different phase of it and the chart oscillates at
#: the slice frequency.
BUCKET_UNITS = {
    'hour': TruncHour,
    'day': TruncDay,
    'week': TruncWeek,
    'month': TruncMonth,
}


class InvalidBucket(ValueError):
    """The client asked for a unit or a timezone that does not exist"""


def parse_timezone(name: str | None):
    """
    The zone the calendar buckets are cut in, the server's own when the client
    names none.

    Buckets follow the user's calendar, not UTC: a reading half an hour after
    midnight belongs to the day the user had it.
    """
    if not name:
        return None

    try:
        return ZoneInfo(name)
    except (ZoneInfoNotFoundError, ValueError):
        raise InvalidBucket(f'Unknown timezone: {name}')


def _bounds_expression(key: str, aggregate):
    """
    The stored bound of a daily aggregate, falling back to the value itself.

    An entry that already summarises a day (heart rate) carries the range it
    stands for in `extra_data`, and contributes that rather than its mean, so
    condensing an aggregate keeps the true extremes.
    """
    return aggregate(
        Coalesce(
            Cast(F(f'extra_data__{key}'), DecimalField(max_digits=8, decimal_places=2)),
            F('value'),
        )
    )


def ladder_unit(queryset, tz, max_points: int) -> str:
    """
    The finest unit that keeps the series under [max_points], counting what
    each one would produce in a single pass.

    Mirrors the ladder the flutter repository walks. There is no unit below
    the hour: an entry-level read is the plain list endpoint.
    """
    counts = queryset.aggregate(
        **{
            name: Count(trunc('date', tzinfo=tz), distinct=True)
            for name, trunc in BUCKET_UNITS.items()
        }
    )

    for name in BUCKET_UNITS:
        if counts[name] <= max_points:
            return name
    return 'month'


def bucket_rows(queryset, unit: str, tz, max_points: int = DEFAULT_MAX_POINTS) -> list[dict]:
    """
    One row per category, calendar bucket and stored unit, oldest first.

    Grouped by the unit the values were entered in as well, because a mean over
    kg and lb values is a number in neither: the client converts each row
    through its own helper and merges them afterwards (see `Measurement.unit`).
    """
    if unit == 'auto':
        unit = ladder_unit(queryset, tz, max_points)
    if unit not in BUCKET_UNITS:
        raise InvalidBucket(f'Unknown bucket: {unit}')

    rows = (
        queryset.annotate(
            start=BUCKET_UNITS[unit]('date', tzinfo=tz),
            stored_unit=F('extra_data__unit'),
        )
        .values('category', 'start', 'stored_unit')
        .annotate(
            count=Count('id'),
            total=Sum('value'),
            low=_bounds_expression('min', Min),
            high=_bounds_expression('max', Max),
        )
        .order_by('start')
    )

    return [
        {
            'category': row['category'],
            'start': row['start'],
            'unit': row['stored_unit'],
            'count': row['count'],
            'sum': row['total'],
            'min': row['low'],
            'max': row['high'],
        }
        for row in rows
    ]


def value_count_rows(queryset, tz, summed_per_day: bool = False) -> list[dict]:
    """
    How often each value occurred, for the histogram.

    Not bucketed by time but by value, which is the granularity a histogram
    bins at anyway: a year of heart rate is tens of thousands of readings over
    some two hundred distinct bpm. Counting instead of binning keeps the
    conversion of a mixed-unit category exact, since the values still go
    through the client's helper. [summed_per_day] counts daily totals rather
    than single readings, for the metrics whose samples mean nothing alone.
    """
    if summed_per_day:
        daily = (
            queryset.annotate(day=TruncDay('date', tzinfo=tz), stored_unit=F('extra_data__unit'))
            .values('category', 'day', 'stored_unit')
            .annotate(value=Sum('value'), newest=Max('date'))
        )
        counted: dict[tuple, dict] = {}
        for row in daily:
            key = (row['category'], row['stored_unit'], row['value'])
            entry = counted.setdefault(
                key,
                {
                    'category': row['category'],
                    'unit': row['stored_unit'],
                    'value': row['value'],
                    'count': 0,
                    'newest': row['newest'],
                },
            )
            entry['count'] += 1
            entry['newest'] = max(entry['newest'], row['newest'])
        return sorted(counted.values(), key=lambda r: (str(r['category']), r['value']))

    rows = (
        queryset.annotate(stored_unit=F('extra_data__unit'))
        .values('category', 'stored_unit', 'value')
        .annotate(count=Count('id'), newest=Max('date'))
        .order_by('value')
    )

    return [
        {
            'category': row['category'],
            'unit': row['stored_unit'],
            'value': row['value'],
            'count': row['count'],
            'newest': row['newest'],
        }
        for row in rows
    ]
