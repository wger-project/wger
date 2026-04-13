from django.db import migrations, models

from wger.utils.uuid import uuid7


class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0032_continue_weight_unit_merge'),
    ]

    operations = [
        # Now make uuid non-nullable and unique
        migrations.AlterField(
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
