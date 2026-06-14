from django.db import migrations


def insert_kcal_unit(apps, schema_editor):
    WeightUnit = apps.get_model('core', 'WeightUnit')
    WeightUnit(name='kcal', pk=7).save()


class Migration(migrations.Migration):
    dependencies = [
        ('core', '0022_move_email_verified_to_emailaddress'),
    ]

    operations = [
        migrations.RunPython(insert_kcal_unit, reverse_code=migrations.RunPython.noop),
    ]
