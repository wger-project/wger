from django.db import migrations, models
from django.db.migrations.state import StateApps


def migrate_foreign_key_to_m2m(apps: StateApps, schema_editor):
    Ingredient = apps.get_model('nutrition', 'Ingredient')
    for ingre in Ingredient.objects.exclude(category_id__isnull=True):
        ingre.categories.add(ingre.category)


class Migration(migrations.Migration):
    dependencies = [
        ('nutrition', '0037_powersync_synced_ingredient_tables'),
    ]

    operations = [
        migrations.AddField(
            model_name='ingredient',
            name='categories',
            field=models.ManyToManyField(
                blank=True,
                related_name='ingredients',
                to='nutrition.ingredientcategory',
                verbose_name='Categories',
            ),
        ),
        migrations.RunPython(migrate_foreign_key_to_m2m, reverse_code=migrations.RunPython.noop),
        migrations.RemoveField(
            model_name='ingredient',
            name='category',
        ),
        migrations.RenameField(model_name='ingredient', old_name='categories', new_name='category'),
    ]
