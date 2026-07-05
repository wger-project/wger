from django.db import migrations


def migrate_weight_to_measurements(apps, schema_editor):
    """
    For every existing WeightEntry, ensure the owning user has an official
    'body_weight' Category and create a matching Measurement row.
    """
    WeightEntry = apps.get_model('weight', 'WeightEntry')
    Category = apps.get_model('measurements', 'Category')
    Measurement = apps.get_model('measurements', 'Measurement')

    official_category_by_user = {}

    for entry in WeightEntry.objects.all().iterator():
        category = official_category_by_user.get(entry.user_id)
        if category is None:
            category, _ = Category.objects.get_or_create(
                user_id=entry.user_id,
                metric_type='body_weight',
                is_official=True,
                defaults={'name': 'Body weight', 'unit': 'kg'},
            )
            official_category_by_user[entry.user_id] = category

        Measurement.objects.create(
            category=category,
            date=entry.date,
            value=entry.weight,
            source='user',
        )


def noop_reverse(apps, schema_editor):
    pass


class Migration(migrations.Migration):
    dependencies = [
        ('measurements', '0007_category_is_official'),
        ('weight', '0005_add_uuid'),
    ]

    operations = [
        migrations.RunPython(migrate_weight_to_measurements, noop_reverse),
    ]
