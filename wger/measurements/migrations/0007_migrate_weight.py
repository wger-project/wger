from django.db import migrations, models

BATCH_SIZE = 2000


def official_category(user_id, weight_unit):
    """
    The official body weight category a user gets, in the unit they entered
    their weight in so far
    """
    return {
        'user_id': user_id,
        'metric_type': 'body_weight',
        'is_official': True,
        'name': 'Body weight',
        'unit': weight_unit or 'kg',
    }


def measurement_from(entry, category_id, unit):
    """
    The measurement a weight entry becomes.

    The uuid is carried over as the id, so a client that already synchronises
    weight entries keeps their identity. [unit] is the category's, which is
    what the values were entered in.
    """
    return {
        'id': entry.uuid,
        'category_id': category_id,
        'date': entry.date,
        'value': entry.weight,
        'source': 'user',
        'extra_data': {'unit': unit},
    }


def migrate_weight_to_measurements(apps, schema_editor):
    """
    Give every user an official 'body_weight' Category and create a
    Measurement row for every existing WeightEntry.

    The WeightEntry uuid is carried over as the Measurement id so that
    clients that already synchronise weight entries by uuid keep a stable
    identity. WeightEntry values are stored in the user's preferred weight
    unit, so that unit becomes the category unit and is stamped on every
    migrated entry.
    """
    WeightEntry = apps.get_model('weight', 'WeightEntry')
    Category = apps.get_model('measurements', 'Category')
    Measurement = apps.get_model('measurements', 'Measurement')
    UserProfile = apps.get_model('core', 'UserProfile')

    # The is_official flag was added in this very migration, so no official
    # categories exist yet: every profile unconditionally gets one. New users
    # get theirs via the post_save signal on registration.
    batch = []
    for user_id, unit in UserProfile.objects.values_list('user_id', 'weight_unit').iterator():
        batch.append(Category(**official_category(user_id, unit)))
        if len(batch) >= BATCH_SIZE:
            Category.objects.bulk_create(batch)
            batch = []
    Category.objects.bulk_create(batch)

    # Only users with weight entries are needed for the FK lookup, and only
    # as (pk, unit) tuples instead of model instances
    entry_user_ids = WeightEntry.objects.values_list('user_id', flat=True).distinct()
    category_by_user = {
        user_id: (category_id, unit)
        for category_id, user_id, unit in Category.objects.filter(
            is_official=True,
            user_id__in=entry_user_ids,
        ).values_list('id', 'user_id', 'unit')
    }

    batch = []
    # A zero is not a measurement, but were being added by faulty logic in the BMR calculator
    for entry in WeightEntry.objects.exclude(weight=0).iterator():
        if entry.user_id not in category_by_user:
            # Entries of users without a profile (created outside the normal
            # signal path)
            fields = official_category(entry.user_id, None)
            defaults = {'name': fields.pop('name'), 'unit': fields.pop('unit')}
            category, _ = Category.objects.get_or_create(**fields, defaults=defaults)
            category_by_user[entry.user_id] = (category.id, category.unit)

        category_id, unit = category_by_user[entry.user_id]
        batch.append(Measurement(**measurement_from(entry, category_id, unit)))
        if len(batch) >= BATCH_SIZE:
            Measurement.objects.bulk_create(batch)
            batch = []
    Measurement.objects.bulk_create(batch)


def delete_official_categories(apps, schema_editor):
    """
    Delete the official categories together with all their measurements.

    The forward migration leaves the WeightEntry rows untouched, so this
    restores the pre-migration state and lets the migration re-apply
    cleanly. Body-weight measurements written after the forward migration
    exist only as measurements and are deleted with their category.
    """
    Category = apps.get_model('measurements', 'Category')
    Measurement = apps.get_model('measurements', 'Measurement')

    Measurement.objects.filter(category__is_official=True).delete()
    Category.objects.filter(is_official=True).delete()


class Migration(migrations.Migration):
    dependencies = [
        (
            'measurements',
            '0006_health_sync',
        ),
        ('weight', '0005_add_uuid'),
        ('core', '0002_auto_20141225_1512'),
    ]

    operations = [
        migrations.AddField(
            model_name='category',
            name='is_official',
            field=models.BooleanField(default=False, verbose_name='Official category'),
        ),
        migrations.AddField(
            model_name='measurement',
            name='extra_data',
            field=models.JSONField(blank=True, default=dict, verbose_name='Extra data'),
        ),
        migrations.RunPython(migrate_weight_to_measurements, delete_official_categories),
    ]
