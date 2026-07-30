from django.db import migrations, models

BATCH_SIZE = 2000


def migrate_weight_to_measurements(apps, schema_editor):
    """
    Give every user an official 'body_weight' Category and create a
    Measurement row for every existing WeightEntry.

    The WeightEntry uuid is carried over as the Measurement id so that
    clients that already synchronise weight entries by uuid keep a stable
    identity. The category unit follows the user's preferred weight unit,
    since WeightEntry values are stored in that unit.
    """
    WeightEntry = apps.get_model('weight', 'WeightEntry')
    Category = apps.get_model('measurements', 'Category')
    Measurement = apps.get_model('measurements', 'Measurement')
    UserProfile = apps.get_model('core', 'UserProfile')

    unit_by_user = dict(UserProfile.objects.values_list('user_id', 'weight_unit'))

    category_by_user = {}
    user_ids = WeightEntry.objects.values_list('user_id', flat=True).distinct()
    for user_id in user_ids.iterator():
        category, _ = Category.objects.get_or_create(
            user_id=user_id,
            metric_type='body_weight',
            is_official=True,
            defaults={'name': 'Body weight', 'unit': unit_by_user.get(user_id, 'kg')},
        )
        category_by_user[user_id] = category

    # Users without weight entries get the official category as well, new
    # users get it via the post_save signal on registration
    remaining = [
        Category(
            user_id=user_id,
            metric_type='body_weight',
            is_official=True,
            name='Body weight',
            unit=unit or 'kg',
        )
        for user_id, unit in unit_by_user.items()
        if user_id not in category_by_user
    ]
    Category.objects.bulk_create(remaining, batch_size=BATCH_SIZE)

    batch = []
    for entry in WeightEntry.objects.all().iterator():
        batch.append(
            Measurement(
                id=entry.uuid,
                category=category_by_user[entry.user_id],
                date=entry.date,
                value=entry.weight,
                source='user',
            )
        )
        if len(batch) >= BATCH_SIZE:
            Measurement.objects.bulk_create(batch)
            batch = []
    if batch:
        Measurement.objects.bulk_create(batch)


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        (
            'measurements',
            '0006_category_externally_synced_category_metric_type_and_more',
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
        migrations.AddConstraint(
            model_name='category',
            constraint=models.UniqueConstraint(
                condition=models.Q(('is_official', True)),
                fields=('user', 'metric_type'),
                name='unique_official_category_per_metric_type',
            ),
        ),
        migrations.RunPython(migrate_weight_to_measurements, noop_reverse),
    ]
