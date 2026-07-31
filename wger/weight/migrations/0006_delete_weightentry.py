from django.db import migrations

from wger.utils.constants import TWOPLACES
from wger.utils.units import AbstractWeight

BATCH_SIZE = 2000


def restore_weight_entries(apps, schema_editor):
    """
    Rebuild the WeightEntry table from the official body-weight categories
    so that measurements.0007 can be reverted afterwards.

    WeightEntry stores values in the user's preferred weight unit, so
    entries stamped with a different unit are converted back. Measurement
    ids become the WeightEntry uuids again, mirroring the forward backfill
    in measurements.0007.
    """
    WeightEntry = apps.get_model('weight', 'WeightEntry')
    Measurement = apps.get_model('measurements', 'Measurement')
    UserProfile = apps.get_model('core', 'UserProfile')

    unit_by_user = dict(UserProfile.objects.values_list('user_id', 'weight_unit'))

    batch = []
    entries = Measurement.objects.filter(
        category__metric_type='body_weight',
        category__is_official=True,
    ).select_related('category')
    for measurement in entries.iterator():
        user_id = measurement.category.user_id
        profile_unit = unit_by_user.get(user_id) or 'kg'
        entry_unit = measurement.extra_data.get('unit') or measurement.category.unit
        value = measurement.value
        if entry_unit != profile_unit and entry_unit in ('kg', 'lb'):
            weight = AbstractWeight(value, entry_unit)
            value = (weight.kg if profile_unit == 'kg' else weight.lb).quantize(TWOPLACES)

        batch.append(
            WeightEntry(
                uuid=measurement.id,
                user_id=user_id,
                date=measurement.date,
                weight=value,
            )
        )
        if len(batch) >= BATCH_SIZE:
            WeightEntry.objects.bulk_create(batch)
            batch = []
    WeightEntry.objects.bulk_create(batch)


class Migration(migrations.Migration):
    dependencies = [
        ('weight', '0005_add_uuid'),
        # The forward backfill in measurements.0007 reads this table, so it
        # may only be dropped afterwards. On a full rollback this ordering
        # also runs the restore here before measurements.0007 deletes the
        # official categories.
        ('measurements', '0007_official_categories'),
    ]

    operations = [
        # Listed before DeleteModel so that the reverse recreates the table
        # first and then repopulates it
        migrations.RunPython(migrations.RunPython.noop, restore_weight_entries),
        migrations.DeleteModel(name='WeightEntry'),
    ]
