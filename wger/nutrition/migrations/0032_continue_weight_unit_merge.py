from django.db import migrations, models

from wger.utils.uuid import uuid7


def populate_uuids(apps, schema_editor):
    IngredientWeightUnit = apps.get_model('nutrition', 'IngredientWeightUnit')
    for iwu in IngredientWeightUnit.objects.all():
        iwu.uuid = uuid7()
        iwu.save(update_fields=['uuid'])


class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0031_start_weight_unit_merge'),
    ]

    operations = [
        # Add uuid field without unique constraint first
        migrations.AddField(
            model_name='ingredientweightunit',
            name='uuid',
            field=models.UUIDField(default=uuid7, editable=False, null=True),
        ),
        # Populate each row with a unique UUID
        migrations.RunPython(populate_uuids, migrations.RunPython.noop),
    ]
