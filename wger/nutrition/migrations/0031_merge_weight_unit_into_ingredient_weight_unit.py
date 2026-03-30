from django.db import migrations, models
from django.db.migrations.state import StateApps


def copy_weight_unit_names(apps: StateApps, schema_editor):
    """Copy the name from WeightUnit into IngredientWeightUnit.name"""

    IngredientWeightUnit = apps.get_model('nutrition', 'IngredientWeightUnit')
    for iwu in IngredientWeightUnit.objects.select_related('unit').filter(unit__isnull=False):
        iwu.name = iwu.unit.name
        iwu.save(update_fields=['name'])


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
        migrations.RunPython(copy_weight_unit_names, migrations.RunPython.noop),
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
