from django.db import migrations, models

from wger.utils.uuid import uuid7


def migrate_weight_units(apps, schema_editor):
    """
    Copy unit names from WeightUnit into IngredientWeightUnit.name,
    then delete entries that are not referenced by any MealItem or LogItem.
    """
    IngredientWeightUnit = apps.get_model('nutrition', 'IngredientWeightUnit')
    MealItem = apps.get_model('nutrition', 'MealItem')
    LogItem = apps.get_model('nutrition', 'LogItem')

    # Copy names from the related WeightUnit
    for iwu in IngredientWeightUnit.objects.select_related('unit').filter(unit__isnull=False):
        iwu.name = iwu.unit.name
        iwu.save(update_fields=['name'])

    # Delete entries not referenced by any MealItem or LogItem.
    # These units will become orphaned in local wger instances since we won't be able to update
    # as they will have a local UUID. However, the current units in the system are from the USDA
    # entries which can't be updated anymore and are dwarfed by the 3 million OFF entries, so
    # this step is acceptable.
    referenced_ids = set(
        MealItem.objects.filter(weight_unit__isnull=False).values_list('weight_unit_id', flat=True)
    ) | set(
        LogItem.objects.filter(weight_unit__isnull=False).values_list('weight_unit_id', flat=True)
    )
    IngredientWeightUnit.objects.exclude(id__in=referenced_ids).delete()


class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0030_add_indices'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredientweightunit',
            name='name',
            field=models.CharField(default='Serving', max_length=200, verbose_name='Name'),
            preserve_default=False,
        ),
        # Copy names and delete unreferenced entries
        migrations.RunPython(migrate_weight_units, migrations.RunPython.noop),
        migrations.AddField(
            model_name='ingredientweightunit',
            name='uuid',
            field=models.UUIDField(default=uuid7, editable=False, unique=True),
        ),
        migrations.RemoveField(
            model_name='ingredientweightunit',
            name='unit',
        ),
        migrations.RemoveField(
            model_name='ingredientweightunit',
            name='amount',
        ),
        migrations.DeleteModel(
            name='WeightUnit',
        ),
    ]
