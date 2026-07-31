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

# Standard Library
import datetime
import logging
import random
import uuid
from decimal import Decimal

# Django
from django.contrib.auth.models import User
from django.core.management.base import (
    BaseCommand,
    CommandError,
)
from django.core.validators import MaxValueValidator
from django.utils import timezone

# wger
from wger.measurements.models import (
    Category,
    Measurement,
)
from wger.measurements.models.category import MetricType
from wger.measurements.models.measurement import MeasurementSource
from wger.utils.constants import TWOPLACES
from wger.utils.units import AbstractWeight


logger = logging.getLogger(__name__)

# Fixed namespace: the external IDs are derived from the entry's identity, so a
# second run generates the same IDs and the unique constraint on
# (category, source, external_id) turns it into a no-op instead of duplicating
EXTERNAL_ID_NAMESPACE = uuid.UUID('4b3a3b8e-1b4e-4b2a-9c3a-6b1e7f2d5c40')

# Largest value a measurement currently accepts. Real daily step and energy
# totals are well above it, they are capped so that everything the generator
# writes stays valid for the API as well
MAX_VALUE = min(
    (
        Decimal(validator.limit_value)
        for validator in Measurement._meta.get_field('value').validators
        if isinstance(validator, MaxValueValidator)
    ),
    default=Decimal('9999.99'),
)

# Device the entries claim to come from
DEVICES = {
    MeasurementSource.APPLE.value: ('Apple Watch', 'com.apple.health'),
    MeasurementSource.GOOGLE.value: ('Pixel Watch', 'com.google.android.apps.fitness'),
}

# Category per metric. The names match the canonical names the flutter importer
# uses, so generated data and imported data end up in the same categories
CATEGORIES = {
    'body_weight': (MetricType.BODY_WEIGHT, 'Body weight', 'kg'),
    'body_fat': (MetricType.BODY_FAT, 'Body fat', '%'),
    'height': (MetricType.HEIGHT, 'Height', 'cm'),
    'blood_pressure': (MetricType.BLOOD_PRESSURE, 'Blood pressure', 'mmHg'),
    'heart_rate': (MetricType.HEART_RATE, 'Heart rate', 'bpm'),
    'resting_heart_rate': (MetricType.RESTING_HEART_RATE, 'Resting heart rate', 'bpm'),
    'steps': (MetricType.STEPS, 'Steps', 'count'),
    'distance': (MetricType.DISTANCE, 'Distance', 'km'),
    'energy': (MetricType.ENERGY, 'Energy', 'kcal'),
    'sleep': (MetricType.SLEEP, 'Sleep', 'min'),
}

# Components of the blood pressure group, in the order the importer pairs them
BLOOD_PRESSURE_COMPONENTS = ('Systolic', 'Diastolic')


class Command(BaseCommand):
    """
    Dummy generator for health-synced measurements
    """

    help = (
        'Dummy generator for measurements as the Apple Health / Health Connect importer '
        'writes them (source, external_id and provenance in extra_data). By default only '
        'a handful of entries per metric, --realistic generates the data volume the '
        'platforms actually deliver.'
    )

    def add_arguments(self, parser):
        parser.add_argument(
            '--days',
            action='store',
            default=30,
            dest='days',
            type=int,
            help='The number of days to generate data for (default: 30)',
        )
        parser.add_argument(
            '--realistic',
            action='store_true',
            dest='realistic',
            help='Generate the raw sample volume the platforms deliver (heart rate samples, '
            'hourly step/distance/energy buckets, sleep segments) instead of the daily '
            'aggregates the importer writes today',
        )
        parser.add_argument(
            '--metrics',
            action='store',
            dest='metrics',
            help=f'Comma separated list of metrics to generate, one or more of '
            f'{", ".join(CATEGORIES)} (default: all)',
        )
        parser.add_argument(
            '--source',
            action='store',
            default=MeasurementSource.APPLE.value,
            dest='source',
            choices=list(DEVICES),
            help='The platform the entries claim to come from (default: apple)',
        )
        parser.add_argument(
            '--seed',
            action='store',
            default=42,
            dest='seed',
            type=int,
            help='Seed for the random values, the same seed generates the same data (default: 42)',
        )
        parser.add_argument(
            '--user-id',
            action='store',
            dest='user_id',
            type=int,
            help='Add only to the specified user-ID (default: all users)',
        )

    def handle(self, **options):
        days = options['days']
        if days < 1:
            raise CommandError('--days must be at least 1')

        metrics = self.parse_metrics(options['metrics'])
        self.days = days
        self.realistic = options['realistic']
        self.source = MeasurementSource(options['source']).value
        self.seed = options['seed']
        self.clamped = 0

        # All timestamps are built by adding to this, so the data lines up with
        # the local calendar days the clients aggregate by
        self.today = timezone.localtime(timezone.now()).replace(
            hour=0, minute=0, second=0, microsecond=0
        )

        users = (
            [User.objects.get(pk=options['user_id'])] if options['user_id'] else User.objects.all()
        )

        volume = 'realistic' if self.realistic else 'sparse'
        self.stdout.write(
            f'** Generating {volume} health data ({self.source}) for the last {days} days'
        )

        for user in users:
            self.stdout.write(f'- processing user {user.username}')

            entries = []
            for metric in metrics:
                entries += self.generate(user, metric)

            Measurement.objects.bulk_create(entries, batch_size=500, ignore_conflicts=True)
            self.stdout.write(f'  {len(entries)} entries')

        if self.clamped:
            self.stdout.write(
                self.style.WARNING(
                    f'  {self.clamped} values were capped at {MAX_VALUE}: real daily step or '
                    f'energy totals are above what a measurement currently accepts'
                )
            )

    def parse_metrics(self, metrics: str | None) -> list[str]:
        """
        Returns the metrics to generate data for
        """
        if not metrics:
            return list(CATEGORIES)

        selected = [entry.strip() for entry in metrics.split(',') if entry.strip()]
        unknown = [entry for entry in selected if entry not in CATEGORIES]
        if unknown:
            raise CommandError(f'Unknown metrics: {", ".join(unknown)}')

        return selected

    def generate(self, user: User, metric: str) -> list[Measurement]:
        """
        Generates the entries of one metric for one user
        """
        # One generator per user and metric, so selecting a subset of the
        # metrics or users does not change the generated data
        rng = random.Random(f'{self.seed}-{user.pk}-{metric}')
        category = self.get_category(user, metric)

        match metric:
            case 'body_weight':
                return self.generate_body_weight(rng, category)
            case 'body_fat':
                return self.generate_body_fat(rng, category)
            case 'height':
                return self.generate_height(rng, category)
            case 'blood_pressure':
                return self.generate_blood_pressure(rng, self.get_components(category))
            case 'heart_rate':
                return self.generate_heart_rate(rng, category)
            case 'resting_heart_rate':
                return self.generate_resting_heart_rate(rng, category)
            case 'steps':
                return self.generate_cumulative(
                    rng, category, record_type='STEPS', daily_min=3000, daily_max=16000
                )
            case 'distance':
                return self.generate_cumulative(
                    rng, category, record_type='DISTANCE_DELTA', daily_min=2, daily_max=12
                )
            case 'energy':
                return self.generate_cumulative(
                    rng, category, record_type='ACTIVE_ENERGY_BURNED', daily_min=250, daily_max=900
                )
            case 'sleep':
                return self.generate_sleep(rng, category)
            case _:
                raise CommandError(f'No generator for metric {metric}')

    #
    # Categories
    #
    def get_category(self, user: User, metric: str) -> Category:
        """
        Returns the category the metric is imported into, creating it if needed
        """
        metric_type, name, unit = CATEGORIES[metric]

        if metric_type == MetricType.BODY_WEIGHT:
            return Category.get_or_create_official(
                user,
                metric_type,
                name=name,
                unit=user.userprofile.weight_unit,
            )

        category = Category.objects.filter(user=user, metric_type=metric_type).first()
        if category is None:
            category = Category.objects.create(
                user=user,
                metric_type=metric_type,
                name=name,
                unit=unit,
            )
        return category

    def get_components(self, group: Category) -> list[Category]:
        """
        Returns the child categories of a multi-value group, e.g. blood pressure.

        Only the leaves carry measurements, the group itself stays empty.
        """
        components = []
        for order, name in enumerate(BLOOD_PRESSURE_COMPONENTS):
            component = group.children.filter(name=name).first()
            if component is None:
                component = Category.objects.create(
                    user=group.user,
                    name=name,
                    unit=group.unit,
                    parent=group,
                    order=order,
                )
            components.append(component)
        return components

    #
    # Entries
    #
    def entry(
        self,
        category: Category,
        date: datetime.datetime,
        value: float,
        *,
        record_type: str,
        key: str,
        extra: dict | None = None,
        recording_method: str = 'automatic',
    ) -> Measurement:
        """
        Builds one entry as the health importer would write it
        """
        device, source_id = DEVICES[self.source]
        extra_data = {
            'record_type': record_type,
            'recording_method': recording_method,
            'source_name': device,
            'source_id': source_id,
        }
        extra_data.update(extra or {})

        decimal_value = Decimal(value).quantize(TWOPLACES)
        if decimal_value > MAX_VALUE:
            self.clamped += 1
            decimal_value = MAX_VALUE

        return Measurement(
            category=category,
            date=date,
            value=decimal_value,
            source=self.source,
            external_id=uuid.uuid5(EXTERNAL_ID_NAMESPACE, key),
            extra_data=extra_data,
        )

    def day_start(self, offset: int) -> datetime.datetime:
        """
        Returns midnight of the day `offset` days ago
        """
        return self.today - datetime.timedelta(days=offset)

    def day_range(self) -> range:
        """
        Returns the day offsets to generate, oldest first
        """
        return range(self.days, -1, -1)

    #
    # Generators, one per metric
    #
    def generate_body_weight(self, rng: random.Random, category: Category) -> list[Measurement]:
        weight = rng.uniform(62, 95)
        trend = rng.uniform(-0.04, 0.03)
        # A scale that syncs writes every morning, manual weigh-ins are sporadic
        interval = 1 if self.realistic else 3

        entries = []
        for offset in self.day_range():
            weight += trend + rng.gauss(0, 0.3)
            if offset % interval:
                continue

            date = self.day_start(offset) + datetime.timedelta(hours=7, minutes=rng.randint(0, 45))
            extra = {'unit': 'kg'}

            # Imperial readings are converted on import, the original is kept
            if rng.random() < 0.2:
                extra['source_unit'] = 'lb'
                extra['source_value'] = float(AbstractWeight(weight, 'kg').lb.quantize(TWOPLACES))

            entries.append(
                self.entry(
                    category,
                    date,
                    weight,
                    record_type='WEIGHT',
                    key=f'weight:{date.isoformat()}',
                    extra=extra,
                )
            )
        return entries

    def generate_body_fat(self, rng: random.Random, category: Category) -> list[Measurement]:
        percent = rng.uniform(11, 31)
        trend = rng.uniform(-0.02, 0.01)
        interval = 1 if self.realistic else 3

        entries = []
        for offset in self.day_range():
            percent += trend + rng.gauss(0, 0.2)
            if offset % interval:
                continue

            # Same session as the weight, the scale writes both at once
            date = self.day_start(offset) + datetime.timedelta(hours=7, minutes=rng.randint(0, 45))
            entries.append(
                self.entry(
                    category,
                    date,
                    max(3.0, percent),
                    record_type='BODY_FAT_PERCENTAGE',
                    key=f'body_fat:{date.isoformat()}',
                )
            )
        return entries

    def generate_height(self, rng: random.Random, category: Category) -> list[Measurement]:
        # Height barely changes, the platforms hold a single entered value
        date = self.day_start(self.days) + datetime.timedelta(hours=9)
        return [
            self.entry(
                category,
                date,
                rng.uniform(158, 196),
                record_type='HEIGHT',
                key=f'height:{date.isoformat()}',
                recording_method='manual',
            )
        ]

    def generate_blood_pressure(
        self,
        rng: random.Random,
        components: list[Category],
    ) -> list[Measurement]:
        systolic_category, diastolic_category = components
        systolic_base = rng.uniform(112, 134)
        diastolic_base = rng.uniform(70, 86)

        entries = []
        for offset in self.day_range():
            if self.realistic:
                hours = [7, 21]
            elif offset % 4:
                continue
            else:
                hours = [rng.choice([8, 20])]

            for hour in hours:
                # A reading is the pair sharing one timestamp
                date = self.day_start(offset) + datetime.timedelta(
                    hours=hour, minutes=rng.randint(0, 50)
                )
                entries.append(
                    self.entry(
                        systolic_category,
                        date,
                        systolic_base + rng.gauss(0, 6),
                        record_type='BLOOD_PRESSURE_SYSTOLIC',
                        key=f'blood_pressure:systolic:{date.isoformat()}',
                    )
                )
                entries.append(
                    self.entry(
                        diastolic_category,
                        date,
                        diastolic_base + rng.gauss(0, 4),
                        record_type='BLOOD_PRESSURE_DIASTOLIC',
                        key=f'blood_pressure:diastolic:{date.isoformat()}',
                    )
                )
        return entries

    def generate_heart_rate(self, rng: random.Random, category: Category) -> list[Measurement]:
        entries = []
        for offset in self.day_range():
            day = self.day_start(offset)
            samples = self.heart_rate_samples(rng, day, rng.uniform(48, 64))

            if self.realistic:
                entries += [
                    self.entry(
                        category,
                        date,
                        value,
                        record_type='HEART_RATE',
                        key=f'heart_rate:{date.isoformat()}',
                    )
                    for date, value in samples
                ]
                continue

            # The importer stores high-frequency metrics as one entry per
            # calendar day: the day average, with the spread in extra_data
            values = [value for _, value in samples]
            entries.append(
                self.entry(
                    category,
                    day,
                    sum(values) / len(values),
                    record_type='HEART_RATE',
                    key=f'heart_rate:day:{day.date().isoformat()}',
                    extra={
                        'min': round(min(values), 2),
                        'max': round(max(values), 2),
                        'sample_count': len(values),
                    },
                )
            )
        return entries

    def heart_rate_samples(
        self,
        rng: random.Random,
        day: datetime.datetime,
        resting: float,
    ) -> list[tuple[datetime.datetime, float]]:
        """
        Returns a day of heart rate samples: sparser at night, denser while
        awake, with a workout block on most days
        """
        workout_hour = rng.randint(16, 20) if rng.random() < 0.6 else None

        samples = []
        for hour in range(24):
            asleep = hour < 7 or hour >= 23
            for minute in range(0, 60, 10 if asleep else 5):
                date = day + datetime.timedelta(hours=hour, minutes=minute)

                if asleep:
                    value = resting + rng.gauss(0, 3)
                elif hour == workout_hour:
                    value = resting + 70 + rng.gauss(0, 12)
                else:
                    value = resting + 18 + rng.gauss(0, 8)

                samples.append((date, max(40.0, value)))
        return samples

    def generate_resting_heart_rate(
        self,
        rng: random.Random,
        category: Category,
    ) -> list[Measurement]:
        # Imported raw: the platforms compute one value per day themselves
        resting = rng.uniform(48, 64)

        entries = []
        for offset in self.day_range():
            resting += rng.gauss(0, 0.6)
            date = self.day_start(offset) + datetime.timedelta(hours=6, minutes=45)
            entries.append(
                self.entry(
                    category,
                    date,
                    max(38.0, resting),
                    record_type='RESTING_HEART_RATE',
                    key=f'resting_heart_rate:{date.isoformat()}',
                )
            )
        return entries

    def generate_cumulative(
        self,
        rng: random.Random,
        category: Category,
        *,
        record_type: str,
        daily_min: float,
        daily_max: float,
    ) -> list[Measurement]:
        """
        Generates a cumulative metric (steps, distance, energy).

        Sparse mode imports the daily total the platform aggregates itself,
        realistic mode the raw interval records, one per active hour.
        """
        entries = []
        for offset in self.day_range():
            day = self.day_start(offset)
            total = rng.uniform(daily_min, daily_max) * (1.25 if day.weekday() >= 5 else 1)

            if not self.realistic:
                entries.append(
                    self.entry(
                        category,
                        day,
                        total,
                        record_type=record_type,
                        key=f'{record_type}:day:{day.date().isoformat()}',
                        extra={'date_to': (day + datetime.timedelta(days=1)).isoformat()},
                    )
                )
                continue

            # Spread the day over the waking hours, some of them barely active
            buckets = {hour: rng.random() ** 2 for hour in range(7, 23)}
            weight_sum = sum(buckets.values())

            for hour, weight in buckets.items():
                value = total * weight / weight_sum
                if value < 0.01:
                    continue

                start = day + datetime.timedelta(hours=hour)
                entries.append(
                    self.entry(
                        category,
                        start,
                        value,
                        record_type=record_type,
                        key=f'{record_type}:{start.isoformat()}',
                        extra={'date_to': (start + datetime.timedelta(hours=1)).isoformat()},
                    )
                )
        return entries

    def generate_sleep(self, rng: random.Random, category: Category) -> list[Measurement]:
        """
        Generates sleep in minutes, the unit both platforms report.

        Sparse mode writes the night as the importer does: one entry per wake
        day, the summed time asleep as the value and the window the segments
        really cover in extra_data. Realistic mode writes the stage segments.
        """
        entries = []
        for offset in self.day_range():
            # A night is attributed to the day the user wakes up on, so it
            # starts on the previous evening
            wake_day = self.day_start(offset)
            bedtime = wake_day - datetime.timedelta(minutes=rng.randint(60, 180))
            duration = rng.uniform(330, 540)

            if not self.realistic:
                entries.append(
                    self.entry(
                        category,
                        wake_day,
                        duration,
                        record_type='SLEEP_ASLEEP',
                        key=f'sleep:day:{wake_day.date().isoformat()}',
                        extra={
                            'date_from': bedtime.isoformat(),
                            'date_to': (bedtime + datetime.timedelta(minutes=duration)).isoformat(),
                        },
                    )
                )
                continue

            # The platforms report a night as a series of stage segments
            start = bedtime
            remaining = duration
            while remaining > 10:
                segment = min(remaining, rng.uniform(30, 110))
                end = start + datetime.timedelta(minutes=segment)
                stage = rng.choice(['SLEEP_DEEP', 'SLEEP_LIGHT', 'SLEEP_REM', 'SLEEP_AWAKE'])

                entries.append(
                    self.entry(
                        category,
                        start,
                        segment,
                        record_type=stage,
                        key=f'sleep:{start.isoformat()}',
                        extra={'date_to': end.isoformat()},
                    )
                )
                start = end
                remaining -= segment
        return entries
